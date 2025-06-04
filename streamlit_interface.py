import streamlit as st
import requests
from typing import List

# uvicorn app.main should be on port 8200
API_URL = "http://localhost:8200/retrieve_images" 

st.title("Image Search with Natural Language Query")

query = st.text_input("Enter your search query:")

path_prefix = "/Users/arjunvijayan/Desktop/new/visual-search-system"

if st.button("Search"):
    if not query.strip():
        st.warning("Please enter a non-empty query.")
    else:
        with st.spinner("Searching..."):
            try:
                response = requests.post(API_URL, json={"query": query})
                response.raise_for_status()
                data = response.json()

                image_paths: List[str] = data.get("image_paths", [])
                rationale: List[str] = data.get("image_match_rationale", [])

                if not image_paths:
                    st.info("No images found for this query.")
                else:
                    st.success(f"Found {len(image_paths)} images:")

                    # Limit to max 5 images
                    images_to_show = image_paths[:5]
                    images_to_show = [path_prefix + image[1:] for image in images_to_show]
                    st.markdown(images_to_show)

                    # Create 2 rows of columns with 3 columns each
                    rows = 2
                    cols = 3
                    idx = 0

                    for _ in range(rows):
                        columns = st.columns(cols)
                        for col in columns:
                            if idx < len(images_to_show):
                                col.image(images_to_show[idx], caption=rationale[idx], use_container_width=True)
                                idx += 1
                            else:
                                # Empty column if no image
                                col.write("")

            except requests.exceptions.RequestException as e:
                st.error(f"API request failed: {e}")
