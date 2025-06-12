import logging
from typing import List, Dict
import os
from app.vector_db.embedder import embed_text

RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", "0.75"))

log = logging.getLogger(__name__)

async def retrieve_similar_vectors(
    query: str,
    vector_index,
    top_k: int = 5,
    relevance_threshold: float = RELEVANCE_THRESHOLD,
) -> List[Dict]:
    """Return answer vectors similar to ``query`` above a score threshold.

    Parameters
    ----------
    query:
        Text used to search the vector index.
    vector_index:
        Pinecone index instance used for retrieval.
    top_k:
        Number of matches to request from Pinecone.
    relevance_threshold:
        Minimum similarity score to include a match. Defaults to
        the ``RELEVANCE_THRESHOLD`` environment variable.
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
            score_threshold=relevance_threshold,
        )
    except Exception as e:
        log.error(f"[RAG] Pinecone query error: {e}")
        return []

    retrieved: List[Dict] = [
        {
            "id": m.id,
            "score": m.score,
            "metadata": m.metadata,
        }
        for m in result.matches
        if m.score is None or m.score >= relevance_threshold
    ]
    for m in retrieved:
        log.info(f"[RAG] Retrieved answer vector {m['id']} (score={m['score']})")

    return retrieved

