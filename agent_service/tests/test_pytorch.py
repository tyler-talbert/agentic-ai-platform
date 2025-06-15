import unittest
import torch
from torch.utils.data import DataLoader

from agent_service.app.pytorch.model import Autoencoder
from agent_service.app.pytorch.trainer import train


class TestPyTorchModule(unittest.TestCase):
    def test_autoencoder_forward(self):
        # Use the new Autoencoder; input = output = 768 by default
        batch_size = 4
        input_dim = 768
        model = Autoencoder(input_dim=input_dim, hidden_dim=256)

        # Create a dummy batch of random vectors
        x = torch.randn(batch_size, input_dim)
        out = model(x)

        # Assert output shape matches input
        self.assertEqual(out.shape, (batch_size, input_dim))

    def test_trainer_smoke(self):
        # Tiny dataset of 8 random vectors
        input_dim = 768
        data = [torch.randn(input_dim) for _ in range(8)]
        loader = DataLoader(data, batch_size=2)

        # Initialize autoencoder, optimizer, and loss
        model = Autoencoder(input_dim=input_dim, hidden_dim=256)
        optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
        criterion = torch.nn.MSELoss()

        # Run training for 1 epoch; should complete without error
        return_value = train(model, loader, optimizer, criterion, epochs=1)
        self.assertIsNone(return_value)


if __name__ == "__main__":
    unittest.main()
