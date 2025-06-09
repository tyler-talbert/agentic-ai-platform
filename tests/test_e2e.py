import os
import time
import sys
import httpx
import pytest

ORCHESTRATOR_URL = os.getenv("ORCH_URL", "http://localhost:4000")
AGENT_URL        = os.getenv("AGENT_URL", "http://localhost:4001")


def _log(msg: str) -> None:
    print(f"[TEST] {msg}")


def _assert_ok(resp: httpx.Response, code: int = 200) -> None:
    assert resp.status_code == code, (
        f"{resp.request.method} {resp.url} → {resp.status_code}: {resp.text}"
    )


def _status(val) -> str:
    """Normalise a status value for comparisons."""
    return str(val).lower()


def _result_from(body: dict):
    """Return whichever field the API uses for the completed result."""
    if "result" in body:
        return body["result"]
    if "output" in body:
        return body["output"]
    return None


def test_health_check():
    orch  = httpx.get(f"{ORCHESTRATOR_URL}/health")
    _assert_ok(orch)
    assert orch.json()["status"] == "agent_orchestrator is healthy"

    agent = httpx.get(f"{AGENT_URL}/health")
    _assert_ok(agent)
    assert agent.json()["status"] == "agent_service is healthy"


def test_cross_service_call():
    res = httpx.get(f"{ORCHESTRATOR_URL}/run-agent")
    _assert_ok(res)
    assert res.json()["agent_response"]["status"] == "agent_service is healthy"


def test_task_submission_kafka_roundtrip():
    payload = {"input": "hello test"}

    # Submit task (retry a few times while Kafka warms up)
    for attempt in range(5):
        resp = httpx.post(f"{ORCHESTRATOR_URL}/v1/tasks", json=payload)
        if resp.status_code == 200:
            break
        time.sleep(3)
    else:
        pytest.skip(f"Kafka unavailable — skipping: {resp.text}")

    data = resp.json()
    assert _status(data["status"]) == "pending"
    task_id = data["task_id"]
    _log(f"submitted task {task_id}")

    for _ in range(60):
        time.sleep(1)
        poll = httpx.get(f"{ORCHESTRATOR_URL}/v1/tasks/{task_id}")
        if poll.status_code != 200:
            continue
        body = poll.json()
        if _status(body.get("status")) == "completed":
            result = _result_from(body)
            assert result is not None, "completed task has no result/output payload"
            _log("completed ✓")
            return

    pytest.fail(f"Task {task_id} did not complete in time")


if __name__ == "__main__":  # pragma: no cover
    try:
        test_health_check()
        test_cross_service_call()
        test_task_submission_kafka_roundtrip()
        _log("✅ All checks passed")
    except AssertionError as exc:
        _log(f"❌ {exc}")
        sys.exit(1)
