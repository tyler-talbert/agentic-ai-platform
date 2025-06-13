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

from agent_service.app.pytorch.model import Autoencoder
from agent_service.app.pytorch.dataset import AutoencoderDataset
from agent_service.app.pytorch.trainer import train
from agent_service.app.vector_db.vector_db import get_index  # existing helper

log = logging.getLogger(__name__)


def fetch_vectors_from_pinecone(sample_size: int = 5000):
    """Pull a random sample of answer vectors from Pinecone."""
    index = get_index("agent-knowledge-base")
    # Pinecone doesn't have a 'list' API in every plan; here we do a dummy vector fetch
    all_ids = [meta["id"] for meta in index.describe_index_stats()["namespaces"][""]["metadata"]]
    sample_ids = random.sample(all_ids, min(sample_size, len(all_ids)))
    vectors = []
    for chunk in [sample_ids[i : i + 100] for i in range(0, len(sample_ids), 100)]:
        response = index.fetch(ids=chunk)
        vectors.extend([v["values"] for v in response.vectors.values()])
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
