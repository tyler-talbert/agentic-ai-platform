import os
import subprocess
import time
import json
import shutil
import httpx
import pytest
from kafka import KafkaConsumer

COMPOSE_FILE = os.path.join(os.path.dirname(__file__), '..', 'docker-compose.yml')
ORCH_URL = 'http://localhost:4000'

def _docker(*args):
    return ['docker', 'compose', '-f', COMPOSE_FILE, *args]

@pytest.fixture(scope="module", autouse=True)
def stack():
    if shutil.which('docker') is None:
        pytest.skip('docker not available')
    subprocess.check_call(_docker('up', '-d'))
    # wait briefly for services
    time.sleep(10)
    yield
    subprocess.check_call(_docker('down', '-v'))


def test_grpc_and_kafka_flow(stack):
    payload = {"input": "ping"}
    resp = httpx.post(f"{ORCH_URL}/v1/tasks", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    task_id = data["task_id"]

    start = time.time()
    while time.time() - start < 20:
        poll = httpx.get(f"{ORCH_URL}/v1/tasks/{task_id}")
        if poll.status_code == 200 and poll.json().get("status") == "COMPLETED":
            break
        time.sleep(1)
    else:
        pytest.fail('task did not complete')

    consumer = KafkaConsumer(
        'agent-tasks-completed',
        bootstrap_servers='localhost:9092',
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        consumer_timeout_ms=5000,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    )
    msgs = [m.value for m in consumer if m.value.get('task_id') == task_id]
    assert len(msgs) == 1
