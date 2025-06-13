from typing import Sequence

import torch
from torch.utils.data import Dataset


class AutoencoderDataset(Dataset):
    """
    Dataset wrapping a collection of embedding vectors.

    Each sample is returned as a dict with identically-shaped 'input' and 'target'
    tensors so we can use MSE reconstruction loss.
    """

    def __init__(self, vectors: Sequence[Sequence[float]]):
        self._tensors = [torch.tensor(v, dtype=torch.float32) for v in vectors]

    def __len__(self):
        return len(self._tensors)

    def __getitem__(self, idx):
        vec = self._tensors[idx]
        return {"input": vec, "target": vec}