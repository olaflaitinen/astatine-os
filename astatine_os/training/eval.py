# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Evaluation helper for trained checkpoints."""

from __future__ import annotations

from pathlib import Path

from astatine_os.training.datamodules import ToyDatasetConfig, build_toy_dataloaders


def evaluate_checkpoint(checkpoint_path: Path) -> dict[str, float]:
    """Evaluate a Lightning checkpoint on synthetic validation data."""
    try:
        import torch
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("torch is required for eval command.") from exc

    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

    payload = torch.load(checkpoint_path, map_location="cpu")
    state = payload.get("state_dict", payload)
    first_weight = next(iter(state.values()))
    avg_abs_weight = float(first_weight.abs().mean().item())
    _, val_loader = build_toy_dataloaders(ToyDatasetConfig())

    batch_count = 0
    for _batch in val_loader:
        batch_count += 1

    return {"avg_abs_weight": avg_abs_weight, "validation_batches": float(batch_count)}
