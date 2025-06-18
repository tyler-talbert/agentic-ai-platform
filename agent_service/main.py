import os
import asyncio
import torch
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.kafka_client.consumer import consume_kafka_messages
from app.grpc_server import serve as grpc_serve
from app.agent_runner.agent_runner import set_fastapi_app
from app.vector_db.vector_db import (
    init_pinecone,
    create_index,
    get_index,
    INDEX_NAME,
    INDEX_DIM,
)

COMPRESSED_INDEX_NAME = os.getenv("PINECONE_COMPRESSED_INDEX", f"{INDEX_NAME}-256")
COMPRESSED_DIM = 256
AUTOENCODER_WEIGHTS = os.getenv("AUTOENCODER_WEIGHTS", "autoencoder.pt")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Agent Service] Initializing Pinecone...", flush=True)
    init_pinecone()
    create_index(INDEX_NAME, INDEX_DIM)             # 768-dim index
    create_index(COMPRESSED_INDEX_NAME, COMPRESSED_DIM)

    app.state.vector_index_768 = get_index(INDEX_NAME)
    app.state.vector_index_256 = get_index(COMPRESSED_INDEX_NAME)
    print("[Agent Service] Pinecone indices ready (768 & 256).", flush=True)

    # ---------- Autoencoder ----------
    if os.path.isfile(AUTOENCODER_WEIGHTS):
        from app.pytorch.model import Autoencoder

        _ae = Autoencoder()
        _ae.load_state_dict(torch.load(AUTOENCODER_WEIGHTS, map_location="cpu"))
        _ae.eval()
        app.state.encoder = _ae.encode
        print("[Agent Service] Autoencoder loaded.", flush=True)
    else:
        app.state.encoder = None
        print(f"[Agent Service] Autoencoder weights '{AUTOENCODER_WEIGHTS}' not found.", flush=True)

    print("[Agent Service] Starting Kafka consumer...", flush=True)
    loop = asyncio.get_event_loop()
    loop.create_task(consume_kafka_messages())
    loop.create_task(grpc_serve())

    yield

    print("[Agent Service] Lifespan shutdown complete.", flush=True)


app = FastAPI(lifespan=lifespan)
set_fastapi_app(app)

@app.get("/health")
def health_check():
    return {"status": "agent_service is healthy"}
