import os
import json
import uuid
import base64
from io import BytesIO
from PIL import Image
from llama_index.core.schema import IndexNode
from llama_index.core import VectorStoreIndex, Settings
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.prompts.image_prompts import IMAGE_DESCRIPTION_SYSTEM
from app.model.openai_models import azure_o4_mini_client, embed_model
from app.vector_store_utils.helper import pickle_vector_store 

import logging

Settings.embed_model = embed_model
model_name = 'gpt-4o-mini'

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


class AzureImageCaptioning:
    def __init__(self, image_dir="./assets/downloaded_images", max_workers=10):
        self.image_dir = image_dir
        self.max_workers = max_workers
        print(f"[INIT] Initialized AzureImageCaptioning with directory: {self.image_dir} and workers: {self.max_workers}")

    def read_all_images_from_folder(self):
        image_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".webp")
        images, image_paths = [], []

        print(f"\n[INFO] Scanning folder: {self.image_dir}")
        for filename in os.listdir(self.image_dir):
            if filename.lower().endswith(image_extensions):
                full_path = os.path.join(self.image_dir, filename)
                try:
                    img = Image.open(full_path).convert("RGB")
                    img = self.compress_image(img)
                    images.append(img)
                    image_paths.append(full_path)
                    print(f"[✓] Loaded and compressed: {filename}")
                except Exception as e:
                    print(f"[✗] Failed to load {filename}: {e}")
            else:
                print(f"[SKIP] Unsupported file type: {filename}")
        print(f"[INFO] Total valid images: {len(images)}")
        return images, image_paths

    @staticmethod
    def compress_image(image, max_width=1024):
        if image.size[0] <= max_width:
            return image
        width_percent = max_width / float(image.size[0])
        height_size = int((float(image.size[1]) * width_percent))
        return image.resize((max_width, height_size), Image.LANCZOS)

    def encode_image_to_base64(self, image):
        buffered = BytesIO()
        image.save(buffered, format="PNG", optimize=True)
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def describe_images_batch(self, images, batch_idx=None):
        messages = [{"role": "system", "content": IMAGE_DESCRIPTION_SYSTEM}]
        contents = []

        for idx, img in enumerate(images):
            base64_img = self.encode_image_to_base64(img)
            contents.append({"type": "text", "text": f"Image {idx + 1}: Please describe the diagram shown in this image."})
            contents.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_img}"}})

        messages.append({"role": "user", "content": contents})

        try:
            print(f"\n[INFO] Sending batch {batch_idx} for captioning...")
            response = azure_o4_mini_client.chat.completions.create(
                model=model_name,
                messages=messages,
            )
            print(f"[✓] Received response for batch {batch_idx}")
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"[✗] Error in batch {batch_idx}: {e}")
            return []

    def format_description_result(self, results, paths):
        formatted = []
        for idx, (result, path) in enumerate(zip(results, paths)):
            try:
                desc = result.get("description", "").strip()
                img_class = result.get("class", "").strip()
                category = result.get("category", "").strip()
                subcategory = result.get("subcategory", "").strip()
                action = result.get("action", None)
                obj = result.get("object", None)

                parts = [desc]

                if img_class or category or subcategory:
                    parts.append(f"This is a {img_class} in the category '{category}' and subcategory '{subcategory}'.")

                if obj:
                    parts.append(f"Primary object: {obj}.")
                else:
                    parts.append("No prominent object is identified.")

                if action:
                    parts.append(f"Main action: {action}.")
                else:
                    parts.append("No action is depicted.")

                description_str = " ".join(parts)

                formatted.append({
                    "image_path": path,
                    "image_description": description_str
                })

                print(f"[✓] Formatted image {idx + 1}: {os.path.basename(path)}")

            except Exception as e:
                print(f"[✗] Failed to format image {os.path.basename(path)}: {e}")
        return formatted

    def process_page(self, batch_size=10):
        images, paths = self.read_all_images_from_folder()
        described_images = []

        if not images:
            print("[✗] No images found to process.")
            return [], {'success': False, 'reason': 'No images found'}

        batches = [images[i:i + batch_size] for i in range(0, len(images), batch_size)]
        path_batches = [paths[i:i + batch_size] for i in range(0, len(paths), batch_size)]

        print(f"\n[INFO] Processing {len(images)} images in {len(batches)} batches using {self.max_workers} workers...")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_map = {
                executor.submit(self.describe_images_batch, batch, idx): (idx, path_batch)
                for idx, (batch, path_batch) in enumerate(zip(batches, path_batches), 1)
            }

            for future in as_completed(future_map):
                idx, path_batch = future_map[future]
                try:
                    batch_result = future.result()
                    formatted = self.format_description_result(batch_result, path_batch)
                    described_images.extend(formatted)
                    print(f"[✓] Batch {idx} processed.")
                except Exception as e:
                    print(f"[✗] Failed batch {idx}: {e}")

        print(f"\n[✓] Finished processing. Total described images: {len(described_images)}")
        return described_images, {'success': True}

    def save_img_map_as_json(self, image_data, filename):
        output_dir = "./indexes"
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, filename)
        with open(path, "w") as f:
            json.dump(image_data, f, indent=2)
        print(f"[✓] Saved image map JSON: {path}")
        return path

    def create_index(self, batch_size=10):
        print("\n⚙️ Starting image processing and index creation...")
        image_data, resp = self.process_page(batch_size=batch_size)

        if not resp.get('success'):
            print(f"[✗] Index creation failed: {resp.get('reason')}")
            return {'success': False, 'message': resp.get('reason')}

        print(f"[✓] Total image descriptions: {len(image_data)}")

        nodes = [
            IndexNode(
                text=item["image_description"],
                index_id=item["image_path"],
                extra_info={"image_path": item["image_path"],
                            "description": item["image_description"]}
            ) for item in image_data
        ]

        print(f"[✓] Created {len(nodes)} index nodes")

        vectorindex = VectorStoreIndex(nodes)
        self.retriever = vectorindex.as_retriever(k=5)

        img_map_path = self.save_img_map_as_json(image_data, filename=f'img_map_{uuid.uuid4()}.json')
        pickled_path = pickle_vector_store(self.retriever, is_image=True)

        print(f"[✓] Vector store pickled at: {pickled_path}")

        return {
            'success': True,
            'message': 'Index created successfully',
            'pickled_image_index': pickled_path,
            'image_map_path': img_map_path
        }


if __name__ == "__main__":
    print("\n🚀 Launching AzureImageCaptioning...")
    captioner = AzureImageCaptioning(image_dir="./assets/data_sample", max_workers=15)
    result = captioner.create_index(batch_size=10)
    print("\n🟩 Final Result:")
    print(json.dumps(result, indent=2))
