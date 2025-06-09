import os
from pinecone import Pinecone, ServerlessSpec

INDEX_NAME = "agent-knowledge-base"
INDEX_DIMENSION = 1536

def get_pinecone_client():
    return Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

def init_pinecone():
    print("[VectorDB] Pinecone client initialized.")

def create_index(index_name: str, dimension: int):
    pc = get_pinecone_client()
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        print(f"[VectorDB] Created Pinecone index '{index_name}'.")

def get_index(index_name: str):
    pc = get_pinecone_client()
    return pc.Index(index_name)
