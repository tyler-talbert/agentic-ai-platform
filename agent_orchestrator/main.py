# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager
import httpx
from app.kafka.producer import init_kafka_producer
import os

TOPIC_IN = os.getenv("TOPIC_IN", "agent-tasks-inbound")

producer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global producer
    print("[Orchestrator] Initializing producer...")
    producer = init_kafka_producer()
    yield
    print("[Orchestrator] Shutdown complete.")

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
