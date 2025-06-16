"""
CLI entry point to train the autoencoder on a sample of Pinecone vectors.

Example:
    python -m agent_service.app.pytorch.train_autoencoder --sample-size 5000 --epochs 3
"""
import argparse
import logging
import random
import torch
from torch.utils.data import DataLoader

from app.pytorch.model import Autoencoder
from app.pytorch.dataset import AutoencoderDataset
from app.pytorch.trainer import train
from app.vector_db.vector_db import init_pinecone, get_index

log = logging.getLogger(__name__)


def fetch_vectors_from_pinecone(max_samples: int = 1000):
    """
    Return up to `max_samples` answer vectors from the 768-dim index.
    Works even when the corpus is small.
    """
    init_pinecone()
    index = get_index("agent-knowledge-base")

    res = index.query(
        vector=[0.0] * 768,          # dummy query
        top_k=max_samples,
        include_values=True,
        include_metadata=True,
        filter={"type": "answer"},
    )
    vectors = [m.values for m in res.matches if m.values]

    if not vectors:
        raise RuntimeError("No answer vectors found in the index.")

    print(f"[Autoencoder] Fetched {len(vectors)} vectors for training")
    return vectors




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-size", type=int, default=5000)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=1e-3)
    args = parser.parse_args()

    log.info(f"[Autoencoder] Fetching {args.sample_size} vectors from Pinecone…")
    vectors = fetch_vectors_from_pinecone(args.sample_size)
    if not vectors:
        log.error("No vectors fetched—aborting.")
        return

    dataset = AutoencoderDataset(vectors)
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)

    model = Autoencoder()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    criterion = torch.nn.MSELoss()

    train(model, loader, optimizer, criterion, epochs=args.epochs)
    torch.save(model.state_dict(), "autoencoder.pt")
    log.info("[Autoencoder] Saved model to autoencoder.pt")


if __name__ == "__main__":
    main()
