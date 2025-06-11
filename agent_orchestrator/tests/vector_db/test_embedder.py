import os
import pytest
import respx
from httpx import Response
from app.vector_db.embedder import embed_text

@pytest.fixture(autouse=True)
def patch_url(monkeypatch):
    monkeypatch.setenv("OLLAMA_EMBEDDING_URL", "http://localhost:11434/api/embeddings")

@respx.mock
@pytest.mark.asyncio
async def test_embed_text_returns_vector():
    mock_vector = [0.1] * 1536
    respx.post("http://localhost:11434/api/embeddings").mock(
        return_value=Response(200, json={"embedding": mock_vector})
    )
    result = await embed_text("test input")
    assert result == mock_vector
