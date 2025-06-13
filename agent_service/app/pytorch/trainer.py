import logging
import torch
from torch.utils.data import DataLoader

from .model import SimpleModel

log = logging.getLogger(__name__)

def train(
    model: torch.nn.Module,
    data_loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: torch.nn.Module,
    epochs: int = 1,
    device: torch.device = None,
) -> None:
    """
    Basic training loop for a PyTorch model.

    Args:
        model: The PyTorch model to train.
        data_loader: DataLoader that yields input tensors or dicts with 'input' and 'target'.
        optimizer: Optimizer for training.
        criterion: Loss function.
        epochs: Number of training epochs.
        device: Device to train on (defaults to CUDA if available, else CPU).
    """
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    model.train()

    for epoch in range(epochs):
        running_loss = 0.0
        for batch in data_loader:
            # Support both plain Tensor batches and dicts
            if isinstance(batch, dict):
                inputs = batch['input'].to(device)
                targets = batch['target'].to(device)
            else:
                inputs = batch.to(device)
                targets = batch.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        avg_loss = running_loss / len(data_loader)
        log.info(f"[PyTorch] Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")

