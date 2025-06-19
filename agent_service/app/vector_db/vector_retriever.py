import logging
import os
from typing import List, Dict, Union

try:
    import torch
except ModuleNotFoundError:
    torch = None
from fastapi import Request
from typing import Any

from .embedder import embed_text

RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", "0.75"))
log = logging.getLogger(__name__)


async def retrieve_similar_vectors(
    query: str,
    ctx: Union[Request, Any, "FastAPI"],
    top_k: int = 5,
    relevance_threshold: float = RELEVANCE_THRESHOLD,
) -> List[Dict]:
    """
    Return answer vectors similar to ``query``.

    `ctx` can be:
      • FastAPI Request **or** FastAPI app → use encoder & indices on ``ctx.state``
      • pinecone index object            → legacy 768-dim path
    """
    # embed query to 768-dim
    raw_embedding = await embed_text(query)
    log.info(f"[RAG] Got raw embedding length {len(raw_embedding)}")

    # resolve encoder + index depending on ctx type
    if hasattr(ctx, "state"):
        encoder = getattr(ctx.state, "encoder", None)
        if encoder:
            if torch is None:
                raise RuntimeError("torch is required when using an encoder")
            with torch.no_grad():
                embedding = encoder(torch.tensor(raw_embedding)).tolist()
            vector_index = ctx.state.vector_index_256
            log.info("[RAG] Compressed embedding → 256-d")
        else:
            embedding = raw_embedding
            vector_index = ctx.state.vector_index_768
            log.info("[RAG] Using raw 768-d embedding (no encoder)")
    else:
        embedding = raw_embedding
        vector_index = ctx
        log.info("[RAG] Legacy path: raw 768-d")

    # query Pinecone
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
        {"id": m.id, "score": m.score, "metadata": m.metadata}
        for m in result.matches
        if m.score is None or m.score >= relevance_threshold
    ]
    for m in retrieved:
        log.info(f"[RAG] Retrieved {m['id']} (score={m['score']:.3f})")

    return retrieved
