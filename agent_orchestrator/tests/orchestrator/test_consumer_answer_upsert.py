import logging
from typing import List, Dict
from app.vector_db.embedder import embed_text

log = logging.getLogger(__name__)

async def retrieve_similar_vectors(
    query: str,
    vector_index,
    top_k: int = 5
) -> List[Dict]:
    """
    Retrieve the top-k *answer* vectors most similar to `query`.

    Steps:
      1. Embed the query text via Ollama.
      2. Query Pinecone for vectors with metadata type="answer".
      3. Return a list of dicts: {id, score, metadata}.
      4. On query failure, log error and return empty list.
    """
    log.info("[RAG] Embedding query for retrieval")
    embedding = await embed_text(query)
    log.info(f"[RAG] Received embedding of length {len(embedding)}")

    try:
        result = vector_index.query(
            namespace="",
            vector=embedding,
            top_k=top_k,
            include_metadata=True,
            filter={"type": "answer"},
        )
    except Exception as e:
        log.error(f"[RAG] Pinecone query error: {e}")
        return []

    retrieved: List[Dict] = []
    for match in result.matches:
        retrieved.append({
            "id": match.id,
            "score": match.score,
            "metadata": match.metadata
        })
        log.info(f"[RAG] Retrieved answer vector {match.id} (score={match.score})")

    log.info("[RAG] Context injection complete")
    return retrieved