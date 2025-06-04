from llama_index.core import Settings
from app.vector_store_utils.helper import unpickle_vector_store
from app.model.openai_models import azure_o4_mini_client, embed_model

import os
import json
import dotenv
import traceback

dotenv.load_dotenv()
model_name = os.getenv('AZURE_OPENAI_O4_MINI_DEPLOYMENT_NAME')
# Settings.llm = azure_o4_mini_client
Settings.embed_model = embed_model

index_id = os.getenv('IMG_EMBEDDINGS_STORAGE_PATH')
image_map_dir = os.getenv('IMG_MAP_PATH')
embed_path = os.getenv('VECTOR_INDEX_SAMPLE_PATH')


class ImageRetriever:
    def __init__(self):
        self.index = None
        self.retriever = None
        self.load_index_from_storage(embed_path)

    @staticmethod
    def save_img_map_as_json(data, filename):
        with open(f'{image_map_dir}{filename}', 'w') as f:
            json.dump(data, f)

        return f'{image_map_dir}{filename}'
    
    def load_index_from_storage(self, embed_path=None):
        try:
            self.retriever = unpickle_vector_store(embed_path)
            return {'success': True, 'message': 'image index restored'}
        
        except Exception as e:
            return {'success': False, 'message': f'exception in restoring index -> {e}'}


    def explain_match(self, query: str, description: str) -> str:
        reasoning_prompt =  f"""You are a reasoning engine that explains why a search query matched a description. Query: "{query}". Matched Description: "{description}" 
        Explain in detail **why** this query was a good match for the description. Consider meaning, synonyms, visual content, conceptual overlap, and possible intent of the query. 
        Respond as if you're helping a user understand the match. Exaplain in a thought like manner. Short, concise. 20 - 30 words. Major thought flow only."""

        response = azure_o4_mini_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert in semantic reasoning and search result explanation."},
                {"role": "user", "content": reasoning_prompt}
            ],
            temperature=0.7,
        )

        return response.choices[0].message.content.strip()

    def retrieve_image(self, query: str):
        try:
            if self.retriever:
                response = self.retriever.retrieve(query)
                path_list = []
                description_list = []

                for resp in response:
                    path_list.append(resp.metadata["image_path"])
                    match_reason = self.explain_match(query, resp.metadata["description"])
                    print('match_reason', match_reason)
                    description_list.append(match_reason)
                return path_list, description_list
            
        except Exception as e:
            print(traceback.print_exc())
            print(f"error {e}")
