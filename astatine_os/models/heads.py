# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Prediction heads for thermal and ventilation targets."""

from __future__ import annotations


def build_regression_head(input_dim: int):
    """Build a two-output regression head."""
    try:
        import torch.nn as nn
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("torch is required to build regression heads.") from exc
    return nn.Sequential(
        nn.Linear(input_dim, input_dim),
        nn.ReLU(),
        nn.Linear(input_dim, 2),
    )
