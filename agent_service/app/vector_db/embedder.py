import asyncio
import json
import logging
import os
from typing import Any, List

import httpx

_MAX_RETRIES  = 5
_BACKOFF      = 2
_EXPECTED_DIM = int(os.getenv("OLLAMA_EMBEDDING_DIM", "768"))

log = logging.getLogger(__name__)


async def embed_text(text: Any) -> List[float]:
    """
    Convert `text` (str / dict / list / number, etc.) to a JSON‑serialised
    string if necessary, send it to Ollama’s /api/embeddings endpoint, and
    return the embedding vector (validated length = _EXPECTED_DIM).

    Retries on any HTTP or dimension error with exponential back‑off.
    """
    url   = os.getenv("OLLAMA_EMBEDDING_URL", "http://ollama:11434/api/embeddings")
    model = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

    if not isinstance(text, str):
        text = json.dumps(text, ensure_ascii=False, separators=(",", ":"))

    payload = {"model": model, "prompt": text}

    async with httpx.AsyncClient(timeout=60) as client:
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()

                embedding = data.get("embedding", [])
                if not isinstance(embedding, list) or len(embedding) != _EXPECTED_DIM:
                    raise RuntimeError(
                        f"[Embedding] Bad dim {len(embedding)} vs expected {_EXPECTED_DIM}"
                    )

                log.info(f"[Embedding] Success: len={len(embedding)}")
                return embedding

            except Exception as e:
                log.warning(
                    f"[Embedding] Attempt {attempt}/{_MAX_RETRIES} failed: {e}"
                )
                await asyncio.sleep(_BACKOFF ** attempt)

    raise RuntimeError("Failed to obtain valid embedding after max retries")
