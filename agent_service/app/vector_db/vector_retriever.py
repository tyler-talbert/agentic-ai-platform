import logging
from typing import List, Dict
from app.vector_db.embedder import embed_text

log = logging.getLogger(__name__)

async def retrieve_similar_vectors(
    query: str,
    vector_index,
    top_k: int = 5,
) -> List[Dict]:
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

    retrieved: List[Dict] = [
        {"id": m.id, "score": m.score, "metadata": m.metadata}
        for m in result.matches
    ]
    for m in retrieved:
        log.info(f"[RAG] Retrieved answer vector {m['id']} (score={m['score']})")

    return retrieved

