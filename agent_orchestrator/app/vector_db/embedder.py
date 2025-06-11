import asyncio
import logging
import os
from typing import List

import httpx

_MAX_RETRIES = 5
_BACKOFF = 2

log = logging.getLogger(__name__)

async def embed_text(text: str) -> List[float]:
    """
    Send `text` to the Ollama embedding endpoint and return the embedding vector.
    Reads OLLAMA_EMBEDDING_URL & OLLAMA_EMBEDDING_MODEL from env on every call
    so tests can monkeypatch the URL.
    Retries up to _MAX_RETRIES times with exponential backoff on HTTP errors.
    """
    url = os.getenv(
        "OLLAMA_EMBEDDING_URL",
        "http://ollama:11434/api/embeddings"
    )
    model = os.getenv(
        "OLLAMA_EMBEDDING_MODEL",
        "nomic-embed-text"
    )
    payload = {"model": model, "text": text}

    async with httpx.AsyncClient(timeout=60) as client:
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                if "embedding" not in data:
                    raise RuntimeError(f"[Embedding] Unexpected response: {data}")
                embedding: List[float] = data["embedding"]
                log.info(f"[Embedding] Success: len={len(embedding)}")
                return embedding

            except httpx.HTTPError as e:
                log.warning(f"[Embedding] Attempt {attempt}/{_MAX_RETRIES} failed: {e}")

            await asyncio.sleep(_BACKOFF ** attempt)

    raise RuntimeError("Failed to obtain embedding after max retries")
