# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Simple deterministic hyperparameter sweep utility."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from astatine_os.training.train import TrainConfig, run_training


def run_small_sweep(output_dir: Path) -> list[Path]:
    """Run a tiny sweep over hidden sizes and return checkpoint paths."""
    checkpoints: list[Path] = []
    base = TrainConfig(output_dir=output_dir)
    for hidden_dim in (32, 64):
        cfg = replace(base, hidden_dim=hidden_dim)
        checkpoints.append(run_training(cfg))
    return checkpoints
