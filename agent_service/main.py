from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
import os

from app.kafka.consumer import consume_kafka_messages

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Agent Service] Lifespan started WITH Kafka.", flush=True)
    loop = asyncio.get_event_loop()
    loop.create_task(consume_kafka_messages())
    yield
    print("[Agent Service] Lifespan shutdown complete.", flush=True)

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health_check():
    return {"status": "agent_service is healthy"}
