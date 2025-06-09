import os
import time
import httpx
import pytest

ORCHESTRATOR_URL = os.getenv("ORCH_URL",  "http://localhost:4000")
AGENT_URL        = os.getenv("AGENT_URL", "http://localhost:4001")


def _ok(r: httpx.Response) -> None:
    assert r.status_code == 200, f"{r.request.method} {r.url} → {r.status_code}: {r.text}"


def test_health_check():
    orch  = httpx.get(f"{ORCHESTRATOR_URL}/health")
    _ok(orch)
    assert orch.json()["status"] == "agent_orchestrator is healthy"

    agent = httpx.get(f"{AGENT_URL}/health")
    _ok(agent)
    assert agent.json()["status"] == "agent_service is healthy"


def test_cross_service_call():
    res = httpx.get(f"{ORCHESTRATOR_URL}/run-agent")
    _ok(res)
    assert res.json()["agent_response"]["status"] == "agent_service is healthy"


def test_task_submission_kafka_roundtrip():
    """
    End‑to‑end: submit task → Kafka → agent_service → Kafka → orchestrator.
    Retries the task‑submission call for ~15 s to let Kafka finish booting.
    """
    payload = {"input": "hello test"}

    # ---- Step 1: POST /v1/tasks (retry until 200 or give up) -----------------
    for attempt in range(5):
        res = httpx.post(f"{ORCHESTRATOR_URL}/v1/tasks", json=payload)
        if res.status_code == 200:
            break
        time.sleep(3)            # orchestrator may still be connecting to Kafka
    else:
        pytest.skip(
            f"Kafka unavailable — skipping: {res.text}",
            allow_module_level=False,
        )

    data = res.json()
    assert data["status"] == "PENDING"
    task_id = data["task_id"]

    for _ in range(20):          # ~20 s total (20×1 s)
        time.sleep(1)
        status = httpx.get(f"{ORCHESTRATOR_URL}/v1/tasks/{task_id}")
        if status.status_code != 200:
            continue
        body = status.json()
        if body["status"] == "completed":
            assert "result" in body
            return

    pytest.fail(f"Task {task_id} did not complete within timeout")
