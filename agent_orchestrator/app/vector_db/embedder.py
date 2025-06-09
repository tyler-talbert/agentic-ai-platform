import os
import httpx

OLLAMA_EMBEDDING_URL = os.getenv("OLLAMA_EMBEDDING_URL", "http://localhost:11434/api/embeddings")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")


async def embed_text(text: str) -> list[float]:
    payload = {
        "model": OLLAMA_EMBEDDING_MODEL,
        "prompt": text
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(OLLAMA_EMBEDDING_URL, json=payload)
        response.raise_for_status()
        return response.json()["embedding"]
