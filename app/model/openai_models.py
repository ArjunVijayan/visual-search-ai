import os
import sys

import dotenv

from openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding

dotenv.load_dotenv()

azure_openai_O4_mini_api_key = os.getenv("AZURE_OPENAI_O4_MINI_API_KEY")
azure_openai_O4_mini_deployment_name = os.getenv("AZURE_OPENAI_O4_MINI_DEPLOYMENT_NAME")
azure_openai_O4_mini_version = os.getenv("AZURE_OPENAI_O4_MINI_VERSION")
azure_openai_O4_mini_endpoint = os.getenv("AZURE_OPENAI_O4_MINI_END_POINT")

azure_embedding_deployment_name = os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME")
azure_embedding_version = os.getenv("AZURE_EMBEDDING_VERSION")
azure_embedding_endpoint = os.getenv("AZURE_EMBEDDING_ENDPOINT")


# o4 mini
azure_o4_mini_client = AzureOpenAI(
    api_key=azure_openai_O4_mini_api_key,
    api_version=azure_openai_O4_mini_version,
    azure_endpoint=azure_openai_O4_mini_endpoint
)

# text embeddings
embed_model = AzureOpenAIEmbedding(
    model="text-embedding-3-large",
    api_key=azure_openai_O4_mini_api_key,
    deployment_name=azure_embedding_deployment_name,
    azure_endpoint=azure_embedding_endpoint,
    api_version=azure_embedding_version,
    dimensions=512
)
