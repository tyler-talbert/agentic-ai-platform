import time
import os
import httpx

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
    print("Testing Kafka roundtrip via /tasks endpoint...")
    payload = {"input": "hello test"}
    res = httpx.post(f"{ORCHESTRATOR_URL}/tasks", json=payload)
    assert res.status_code == 200, f"Task submission failed: {res.text}"
    assert res.json()["message"] == "Task submitted to Kafka"
    print("[PASS] Task submission acknowledged")

    print("Waiting 5s for async agent consumption...")
    time.sleep(5)

    # TODO: Replace manual log inspection with assertion against /results/{task_id}
    print("[NOTE] Manually confirm logs in agent_service to verify result.")
