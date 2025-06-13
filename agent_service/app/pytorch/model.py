import torch
import torch.nn as nn

class SimpleModel(nn.Module):
    def __init__(self, input_dim: int = 768, hidden_dim: int = 256, output_dim: int = 768):
        super(SimpleModel, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, output_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.

        Args:
            x: Input tensor of shape (batch_size, input_dim).

        Returns:
            Output tensor of shape (batch_size, output_dim).
        """
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        return out
