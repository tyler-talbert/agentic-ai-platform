import asyncio
import logging
import os
from typing import List

import httpx

OLLAMA_EMBEDDING_URL = os.getenv(
    "OLLAMA_EMBEDDING_URL",
    "http://ollama:11434/api/embeddings"
)
OLLAMA_EMBEDDING_MODEL = os.getenv(
    "OLLAMA_EMBEDDING_MODEL",
    "nomic-embed-text"
)

_MAX_RETRIES = 5
_BACKOFF = 2

log = logging.getLogger(__name__)


async def embed_text(text: str) -> List[float]:
    payload = {"model": OLLAMA_EMBEDDING_MODEL, "prompt": text}

    async with httpx.AsyncClient(timeout=60) as client:
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                resp = await client.post(OLLAMA_EMBEDDING_URL, json=payload)
                resp.raise_for_status()
                data = resp.json()
                if "embedding" not in data:
                    raise RuntimeError(f"[Embedding] Unexpected response format: {data}")
                embedding: List[float] = data["embedding"]
                log.info(f"[Embedding] Success: received vector len={len(embedding)}")
                return embedding
            except httpx.HTTPError as e:
                log.warning(f"[Embedding] Ollama request failed ({attempt}/{_MAX_RETRIES}): {e}")

            await asyncio.sleep(_BACKOFF ** attempt)

    raise RuntimeError("Failed to obtain embedding after max retries")
