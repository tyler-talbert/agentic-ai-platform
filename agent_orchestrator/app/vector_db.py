import pinecone
import os

def init_pinecone():
    api_key = os.getenv("PINECONE_API_KEY")
    environment = os.getenv("PINECONE_ENV", "us-west1-gcp")
    pinecone.init(api_key=api_key, environment=environment)
    print("Pinecone client initialized.")

def create_index(index_name, dimension=1536):
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(index_name, dimension=dimension)
        print(f"Index '{index_name}' created with dimension {dimension}.")
    else:
        print(f"Index '{index_name}' already exists.")

def get_index(index_name):
    try:
        index = pinecone.Index(index_name)
        print(f"Successfully retrieved index '{index_name}'.")
        return index
    except Exception as e:
        print(f"Failed to retrieve index '{index_name}': {e}")
        return None
