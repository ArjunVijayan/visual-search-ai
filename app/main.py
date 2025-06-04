from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from app.model.retriever import ImageRetriever

app = FastAPI(title="Image Search API", description="Retrieve similar images using a natural language query.")

retriever = ImageRetriever()

class QueryRequest(BaseModel):
    query: str

class ImageResponse(BaseModel):
    image_paths: List[str]
    image_match_rationale: List[str]

@app.post("/retrieve_images", response_model=ImageResponse)
def retrieve_images(request: QueryRequest):
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query string is empty.")

        print(f"[INFO] Received query: {request.query}")
        path_list, description_list = retriever.retrieve_image(request.query)

        print(f'retrieved {len(path_list)} images and {len(description_list)} reasons')

        if path_list is None:
            raise HTTPException(status_code=500, detail="Image retriever failed to return results.")

        return {"image_paths": path_list, "image_match_rationale": description_list}

    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
