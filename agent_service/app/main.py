import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from .kafka_consumer import consume_kafka_messages

@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer_task = asyncio.create_task(consume_kafka_messages())
    yield
    consumer_task.cancel()

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health_check():
    return {"status": "agent_service is healthy"}


