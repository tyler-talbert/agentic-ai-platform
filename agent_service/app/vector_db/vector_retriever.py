import logging
import os
from typing import List, Dict, Union

import torch
from fastapi import Request
from pinecone import Index

from app.vector_db.embedder import embed_text

RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", "0.75"))
log = logging.getLogger(__name__)


async def retrieve_similar_vectors(
    query: str,
    ctx: Union[Request, Index],
    top_k: int = 5,
    relevance_threshold: float = RELEVANCE_THRESHOLD,
) -> List[Dict]:
    """
    Return answer vectors similar to ``query``.

    `ctx` can be:
      • FastAPI Request  → use encoder & indices on `app.state`
      • pinecone.Index   → fall back to 768-dim flow (legacy call path)
    """
    # --- embed -------------------------------------------------------------
    raw = await embed_text(query)
    log.info(f"[RAG] Got raw embedding length {len(raw)}")

    # --- resolve encoder + index depending on ctx type --------------------
    if isinstance(ctx, Request):  # new path
        encoder = getattr(ctx.app.state, "encoder", None)
        if encoder:
            with torch.no_grad():
                embedding = encoder(torch.tensor(raw)).tolist()
            vector_index = ctx.app.state.vector_index_256
            log.info("[RAG] Compressed embedding → 256-d")
        else:
            embedding = raw
            vector_index = ctx.app.state.vector_index_768
            log.info("[RAG] Using raw 768-d embedding (no encoder)")
    else:  # legacy call with raw Index
        embedding = raw
        vector_index = ctx
        log.info("[RAG] Legacy call: raw 768-d path")

    # --- query Pinecone ----------------------------------------------------
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
