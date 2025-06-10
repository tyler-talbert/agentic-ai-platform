from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from app.kafka.consumer import consume_kafka_messages
from app.config import init_pinecone, get_vector_index, INDEX_NAME

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Agent Service] Initializing Pinecone...", flush=True)
    init_pinecone()
    vector_index = get_vector_index()
    app.state.vector_index = vector_index
    print(f"[Agent Service] Pinecone index '{INDEX_NAME}' ready.", flush=True)

    print("[Agent Service] Starting Kafka consumer...", flush=True)
    loop = asyncio.get_event_loop()
    loop.create_task(consume_kafka_messages())

    yield

    print("[Agent Service] Lifespan shutdown complete.", flush=True)


app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health_check():
    return {"status": "agent_service is healthy"}
