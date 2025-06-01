from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager
import httpx
import json
from kafka import KafkaProducer
import os
import time

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC_IN = os.getenv("TOPIC_IN", "agent-tasks-inbound")

producer = None  # Initialized in lifespan

@asynccontextmanager
async def lifespan(app: FastAPI):
    global producer
    print("[Orchestrator] Starting up and initializing KafkaProducer...", flush=True)

    for attempt in range(10):
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            print(f"[Orchestrator] Connected to Kafka at {KAFKA_BROKER}", flush=True)
            break
        except Exception as e:
            print(f"[Orchestrator] Attempt {attempt + 1} failed: {e}", flush=True)
            time.sleep(3)
    else:
        print("[Orchestrator] Could not connect to Kafka after 10 attempts. Exiting.", flush=True)
        raise RuntimeError("Kafka unavailable")

    yield

    print("[Orchestrator] Shutting down...")

app = FastAPI(lifespan=lifespan)

class TaskRequest(BaseModel):
    input: str

@app.get("/health")
def health_check():
    return {"status": "agent_orchestrator is healthy"}

@app.get("/run-agent")
async def run_agent():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://agent_service:4001/health")
        return {"agent_response": response.json()}

@app.post("/tasks")
async def submit_task(task: TaskRequest):
    if not producer:
        return {"error": "KafkaProducer is not initialized"}
    producer.send(TOPIC_IN, task.dict())
    return {"message": "Task submitted to Kafka"}
