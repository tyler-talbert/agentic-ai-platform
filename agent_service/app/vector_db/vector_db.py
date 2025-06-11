import os
from typing import Optional

from pinecone import Pinecone, ServerlessSpec

PINECONE_API_KEY   = os.getenv("PINECONE_API_KEY")
PINECONE_ENV       = os.getenv("PINECONE_ENV")
INDEX_NAME         = os.getenv("PINECONE_INDEX_NAME", "agent-knowledge-base")
INDEX_DIM          = int(os.getenv("PINECONE_INDEX_DIM", 768))
INDEX_METRIC       = os.getenv("PINECONE_INDEX_METRIC", "cosine")
SPEC_CLOUD         = os.getenv("PINECONE_SPEC_CLOUD", "aws")
SPEC_REGION        = os.getenv("PINECONE_SPEC_REGION", "us-east-1")


_pinecone_client: Optional[Pinecone] = None


def init_pinecone() -> None:
    """
    Instantiate the Pinecone client using API key & environment.
    Must be called before any other function in this module.
    """
    global _pinecone_client
    assert PINECONE_API_KEY, "PINECONE_API_KEY not set"
    assert PINECONE_ENV, "PINECONE_ENV not set"

    _pinecone_client = Pinecone(
        api_key=PINECONE_API_KEY,
        environment=PINECONE_ENV,
    )
    print(f"[VectorDB] Pinecone client initialized in '{PINECONE_ENV}'.")


def create_index(
    name: str = INDEX_NAME,
    dimension: int = INDEX_DIM,
    metric: str = INDEX_METRIC
) -> None:
    """
    Create the index if it does not already exist.
    Uses ServerlessSpec(cloud=SPEC_CLOUD, region=SPEC_REGION).
    """
    assert _pinecone_client, "Pinecone client not initialized"
    existing = _pinecone_client.list_indexes().names()
    if name not in existing:
        _pinecone_client.create_index(
            name=name,
            dimension=dimension,
            metric=metric,
            spec=ServerlessSpec(
                cloud=SPEC_CLOUD,
                region=SPEC_REGION
            )
        )
        print(f"[VectorDB] Created Pinecone index '{name}'.")


def get_index(name: str = INDEX_NAME):
    """
    Return a handle to the named Pinecone index.
    """
    assert _pinecone_client, "Pinecone client not initialized"
    return _pinecone_client.Index(name)
