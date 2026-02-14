# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Lightweight data module for graph regression experiments."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ToyDatasetConfig:
    """Configuration for deterministic synthetic training data."""

    n_samples: int = 256
    input_dim: int = 12
    seed: int = 42
    batch_size: int = 32


def build_toy_dataloaders(config: ToyDatasetConfig):
    """Return train and validation data loaders."""
    try:
        import torch
        from torch.utils.data import DataLoader, TensorDataset
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("torch is required for training data modules.") from exc

    generator = torch.Generator().manual_seed(config.seed)
    x = torch.randn(config.n_samples, config.input_dim, generator=generator)
    temp = 0.4 * x[:, 0] - 0.2 * x[:, 1] + 0.1 * x[:, 2]
    vent = 0.6 * torch.sigmoid(x[:, 3]) - 0.3 * torch.relu(x[:, 4])
    y = torch.stack([temp, vent], dim=1)

    split = int(config.n_samples * 0.8)
    train_ds = TensorDataset(x[:split], y[:split])
    val_ds = TensorDataset(x[split:], y[split:])
    train_loader = DataLoader(train_ds, batch_size=config.batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=config.batch_size, shuffle=False)
    return train_loader, val_loader
