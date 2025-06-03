import os
import time
import httpx
import sys

# Allow switching between Docker/Local/CI via environment vars
ORCHESTRATOR_URL = os.getenv("ORCH_URL", "http://localhost:4000")
AGENT_URL = os.getenv("AGENT_URL", "http://localhost:4001")


def log(message):
    print(f"[TEST] {message}")


def assert_status(response, expected_code=200):
    assert response.status_code == expected_code, f"Expected {expected_code}, got {response.status_code}: {response.text}"


def test_health_check():
    log("Testing /health endpoints for orchestrator and agent_service...")

    orch = httpx.get(f"{ORCHESTRATOR_URL}/health")
    assert_status(orch)
    assert orch.json().get("status") == "agent_orchestrator is healthy"

    agent = httpx.get(f"{AGENT_URL}/health")
    assert_status(agent)
    assert agent.json().get("status") == "agent_service is healthy"

    log("✅ Health checks passed.")


def test_cross_service_call():
    log("Testing orchestrator -> agent_service call via /run-agent...")

    res = httpx.get(f"{ORCHESTRATOR_URL}/run-agent")
    assert_status(res)

    response_data = res.json()
    assert "agent_response" in response_data, "Missing 'agent_response' key"
    assert response_data["agent_response"].get("status") == "agent_service is healthy"

    log("✅ Cross-service call successful.")


def test_task_submission():
    log("Submitting test task to /tasks (Kafka roundtrip test)...")

    payload = {"input": "test input for agent"}
    res = httpx.post(f"{ORCHESTRATOR_URL}/tasks", json=payload)
    assert_status(res)

    assert res.json().get("message") == "Task submitted to Kafka"
    log("✅ Task accepted by orchestrator.")

    log("Waiting 5 seconds to allow async Kafka consumption...")
    time.sleep(5)

    # TODO: Add result verification once agent outputs to a persistent store (Redis/vector DB/etc.)
    log("Manual verification required: check agent_service logs for 'Received message' and 'Result produced'.")


def run_all_tests():
    try:
        test_health_check()
        test_cross_service_call()
        test_task_submission()
        log("✅ All automated integration tests passed (manual log verification needed).")
    except AssertionError as e:
        log(f"❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
