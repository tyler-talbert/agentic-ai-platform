import unittest
import torch
from torch.utils.data import DataLoader

from agent_service.app.pytorch.model import Autoencoder
from agent_service.app.pytorch.dataset import AutoencoderDataset
from agent_service.app.pytorch.trainer import train


class TestAutoencoder(unittest.TestCase):
    def test_training_reduces_loss(self):
        # Synthetic dataset of 100 random 768-dim vectors
        vectors = torch.randn(100, 768).tolist()
        dataset = AutoencoderDataset(vectors)
        loader = DataLoader(dataset, batch_size=16, shuffle=True)

        model = Autoencoder()
        optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
        criterion = torch.nn.MSELoss()

        # Measure loss before training
        with torch.no_grad():
            batch = next(iter(loader))
            before = criterion(model(batch["input"]), batch["target"]).item()

        # Train one epoch
        train(model, loader, optimizer, criterion, epochs=1)

        # Measure loss after training
        with torch.no_grad():
            after = criterion(model(batch["input"]), batch["target"]).item()

        self.assertLess(after, before, "loss did not decrease")


if __name__ == "__main__":
    unittest.main()