"""
Populate the 256-dim index with encoded copies of every ANSWER vector
in the 768-dim index. Works regardless of Pinecone SDK pagination fields.
Run inside the agent_service container:

    python -m app.vector_db.backfill_encoded_vectors --batch 200
"""
import argparse
import os
import torch
from tqdm import tqdm

from app.vector_db.vector_db import init_pinecone, get_index, INDEX_NAME
from app.pytorch.model import Autoencoder

COMPRESSED_INDEX = f"{INDEX_NAME}-256"
DEFAULT_WEIGHTS = os.getenv("AUTOENCODER_WEIGHTS", "autoencoder.pt")


def batched_vectors(index, batch):
    """
    Yield (id, values, metadata) in chunks of `batch`.
    Uses a sliding window over the entire vector ID space without relying
    on SDK pagination fields.
    """
    offset = ""
    while True:
        res = index.query(
            vector=[0.0] * 768,
            top_k=batch,
            include_values=True,
            include_metadata=True,
            filter={"type": "answer", "id": {"$gt": offset}} if offset else {"type": "answer"},
            sort={"id": 1},  # lexicographic ascending
        )
        if not res.matches:
            break
        for m in res.matches:
            yield m.id, m.values, m.metadata or {}
            offset = m.id
        if len(res.matches) < batch:
            break


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--weights", default=DEFAULT_WEIGHTS)
    p.add_argument("--batch", type=int, default=200)
    args = p.parse_args()

    assert os.path.isfile(args.weights), f"Weights file '{args.weights}' not found."
    enc = Autoencoder()
    enc.load_state_dict(torch.load(args.weights, map_location="cpu"))
    enc.eval()

    init_pinecone()
    src = get_index(INDEX_NAME)
    dst = get_index(COMPRESSED_INDEX)

    batch_size = args.batch
    buffer = []
    total = 0
    print("[Back-fill] Encoding and upserting …")
    for vid, vec, meta in tqdm(batched_vectors(src, batch_size)):
        with torch.no_grad():
            enc_vec = enc.encode(torch.tensor(vec)).tolist()
        buffer.append({"id": vid, "values": enc_vec, "metadata": meta})
        if len(buffer) >= batch_size:
            dst.upsert(vectors=buffer)
            total += len(buffer)
            buffer.clear()
    if buffer:
        dst.upsert(vectors=buffer)
        total += len(buffer)

    print(f"[Back-fill] Complete → {total} vectors upserted to {COMPRESSED_INDEX}")


if __name__ == "__main__":
    main()
