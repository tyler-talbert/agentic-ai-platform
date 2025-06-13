import unittest
import torch
from torch.utils.data import DataLoader

from agent_service.app.pytorch.model import SimpleModel
from agent_service.app.pytorch.trainer import train

class TestPyTorchModule(unittest.TestCase):
    def test_model_forward(self):
        # Define a small model
        input_dim = 10
        hidden_dim = 5
        output_dim = 10
        model = SimpleModel(input_dim=input_dim, hidden_dim=hidden_dim, output_dim=output_dim)

        # Create a dummy batch of 4 samples
        x = torch.randn(4, input_dim)
        out = model(x)

        # Assert output shape
        self.assertEqual(out.shape, (4, output_dim))

    def test_trainer_smoke(self):
        # Small dummy dataset: list of input tensors
        input_dim = 10
        data = [torch.randn(input_dim) for _ in range(6)]
        loader = DataLoader(data, batch_size=2)

        # Initialize model, optimizer, and loss
        model = SimpleModel(input_dim=input_dim, hidden_dim=5, output_dim=input_dim)
        optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
        criterion = torch.nn.MSELoss()

        # Run training for 1 epoch
        return_value = train(model, loader, optimizer, criterion, epochs=1)

        # Ensure the function returns None (i.e., completes without error)
        self.assertIsNone(return_value)

if __name__ == '__main__':
    unittest.main()