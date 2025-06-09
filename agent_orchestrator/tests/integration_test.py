import os
from unittest.mock import patch, MagicMock, AsyncMock

import httpx
import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("PINECONE_API_KEY", "dummy")
os.environ.setdefault("PINECONE_ENV", "test-env")

_fake_index = MagicMock(name="pinecone_index")
_fake_client = MagicMock(name="pinecone_client")
_fake_client.list_indexes().names.return_value = ["agent-knowledge-base"]
_fake_client.Index.return_value = _fake_index

with patch("pinecone.Pinecone", return_value=_fake_client), \
     patch("app.kafka.producer.init_kafka_producer", return_value=MagicMock()):

    from agent_orchestrator.main import app  # noqa: E402

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_lifespan_attaches_vector_index(client):
    assert app.state.vector_index is _fake_index


def test_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "agent_orchestrator is healthy"


def test_cross_service_call(client):
    mock_resp = httpx.Response(200, json={"status": "agent_service is healthy"})
    with patch(
        "agent_orchestrator.main.httpx.AsyncClient.get",
        new_callable=AsyncMock,
        return_value=mock_resp,
    ):
        res = client.get("/run-agent")
        assert res.status_code == 200
        assert res.json()["agent_response"]["status"] == "agent_service is healthy"


@patch("app.orchestrator.orchestrator_engine.embed_text", new_callable=AsyncMock)
@patch("app.orchestrator.orchestrator_engine.produce_task")
def test_task_submission_endpoint(mock_produce_task, mock_embed_text, client):
    mock_embed_text.return_value = [0.1] * 1536

    payload = {"input": "hello test"}
    res = client.post("/v1/tasks", json=payload)

    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "PENDING"
    mock_produce_task.assert_called_once()
