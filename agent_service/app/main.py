import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.kafka_consumer import consume_kafka_messages

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer_task = asyncio.create_task(consume_kafka_messages())
    yield
    consumer_task.cancel()

app.router.lifespan_context = lifespan

@app.get("/health")
def health_check():
    return {"status": "agent_service is healthy"}


