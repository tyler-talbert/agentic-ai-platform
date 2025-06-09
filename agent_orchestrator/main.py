from fastapi import FastAPI
import sys
import os
import asyncio
from contextlib import asynccontextmanager

from app.vector_db.vector_db import (
    init_pinecone,
    create_index,
    get_index,
)
from app.orchestrator.agent_router import router as agent_router
from app.kafka.consumer import consume_kafka_results
from app.kafka.producer import init_kafka_producer
import httpx

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

TOPIC_IN = os.getenv("TOPIC_IN", "agent-tasks-inbound")

producer = None

INDEX_NAME = "agent-knowledge-base"
INDEX_DIMENSION = 768


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Orchestrator] Initializing Pinecone...")
    init_pinecone()
    create_index(INDEX_NAME, INDEX_DIMENSION)
    index = get_index(INDEX_NAME)

    if index:
        app.state.vector_index = index
        print(f"[Orchestrator] Pinecone index '{INDEX_NAME}' attached to app state.")
    else:
        print(f"[Orchestrator] Warning: failed to load Pinecone index '{INDEX_NAME}'.")

    global producer
    print("[Orchestrator] Initializing producer...")
    producer = init_kafka_producer()

    asyncio.create_task(consume_kafka_results())

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
