import logging
from typing import List, Dict
from app.vector_db.embedder import embed_text

log = logging.getLogger(__name__)

async def retrieve_similar_vectors(
    query: str,
    vector_index,
    top_k: int = 5
) -> List[Dict]:
    """Retrieve the top-k vectors most similar to `query`.

       First embeds the query using Ollama, then issues a Pinecone
       query with `include_metadata=True`, and finally transforms
       each match into a simple dict with `id`, `score`, and
       `metadata`.

       Args:
           query: The raw text to embed and search for.
           vector_index: Initialized Pinecone Index client.
           top_k: How many nearest neighbors to return.

       Returns:
           A list of dicts, each containing the vector `id`, its
           similarity `score`, and associated `metadata`.
       """
    log.info("[RAG] Embedding query for retrieval")
    embedding = await embed_text(query)
    log.info(f"[RAG] Received embedding of length {len(embedding)}")

    result = vector_index.query(
        namespace="",
        top_k=top_k,
        include_metadata=True,
        vector=embedding
    )

    retrieved: List[Dict] = []
    for match in result.matches:
        retrieved.append({
            "id": match.id,
            "score": match.score,
            "metadata": match.metadata
        })
        log.info(f"[RAG] Retrieved vector {match.id} (score={match.score})")

    log.info("[RAG] Context injection complete")
    return retrieved
