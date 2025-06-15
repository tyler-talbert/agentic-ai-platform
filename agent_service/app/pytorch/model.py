import torch
import torch.nn as nn


class Autoencoder(nn.Module):
    """
    768-»256-»768 autoencoder (encoder + decoder).

    Encoder compresses the embedding; decoder reconstructs it.
    Keep only encoder weights at inference time if you want a 256-dim vector.
    """
    def __init__(self, input_dim: int = 768, hidden_dim: int = 256):
        super().__init__()
        # Encoder
        self.enc_fc1 = nn.Linear(input_dim, hidden_dim)
        self.enc_relu = nn.ReLU()
        # Decoder
        self.dec_fc1 = nn.Linear(hidden_dim, input_dim)

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        z = self.enc_relu(self.enc_fc1(x))
        return z

    def decode(self, z: torch.Tensor) -> torch.Tensor:
        return self.dec_fc1(z)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.decode(self.encode(x))