import time
import httpx
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(dotenv_path="agent_orchestrator/.env")
__test__ = True

mode = os.getenv("TEST_MODE", "docker")  # Options: "local", "docker"
ORCHESTRATOR_URL = "http://localhost:4000" if mode == "local" else "http://orchestrator:8000"
AGENT_URL = "http://localhost:4001" if mode == "local" else "http://agent_service:4001"

def test_health_check():
    print("Testing /health endpoints...")
    orch = httpx.get(f"{ORCHESTRATOR_URL}/health")
    agent = httpx.get(f"{AGENT_URL}/health")
    assert orch.status_code == 200, f"Orchestrator health failed: {orch.text}"
    assert agent.status_code == 200, f"Agent service health failed: {agent.text}"
    print("[PASS] /health endpoints OK")

def test_cross_service_call():
    print("Testing orchestrator --> agent_service via /run-agent...")
    res = httpx.get(f"{ORCHESTRATOR_URL}/run-agent")
    assert res.status_code == 200, f"Run-agent failed: {res.text}"
    assert res.json()["agent_response"]["status"] == "agent_service is healthy"
    print("[PASS] Cross-service call succeeded")

def test_task_submission_kafka_roundtrip():
    print("Testing Kafka roundtrip via /v1/tasks endpoint...")
    payload = {"input": "hello test"}
    res = httpx.post(f"{ORCHESTRATOR_URL}/v1/tasks", json=payload)
    assert res.status_code == 200, f"Task submission failed: {res.text}"
    data = res.json()
    assert "task_id" in data
    assert data["status"] == "PENDING"
    print("[PASS] Task submission acknowledged")

    print("Polling for task completion...")
    task_id = data["task_id"]
    for _ in range(10):
        time.sleep(1)
        status_res = httpx.get(f"{ORCHESTRATOR_URL}/v1/tasks/{task_id}")
        assert status_res.status_code == 200, f"Status check failed: {status_res.text}"
        status_json = status_res.json()
        if status_json["status"] == "completed":
            print(f"[PASS] Task {task_id} completed with result: {status_json['result']}")
            break
    else:
        raise AssertionError(f"[FAIL] Task {task_id} did not complete in time")



@patch("agent_orchestrator.app.vector_db.init_pinecone")
@patch("agent_orchestrator.app.vector_db.create_index")
@patch("agent_orchestrator.app.vector_db.get_index")
def test_pinecone_startup(mock_get_index, mock_create_index, mock_init_pinecone):
    mock_index = MagicMock()
    mock_get_index.return_value = mock_index

    from agent_orchestrator.main import app

    with TestClient(app) as client:
        assert app.state.vector_index == mock_index
        print("[Test] Pinecone vector index successfully attached to app state.")

