from fastapi import FastAPI
from app.orchestrator.agent_router import router as agent_router
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
app.include_router(agent_router)

@app.get("/health")
def health_check():
    return {"status": "agent_orchestrator is healthy"}

@app.get("/run-agent")
async def run_agent():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://agent_service:4001/health")
        return {"agent_response": response.json()}

