# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Loss functions for multi-task regression."""

from __future__ import annotations


def multitask_l1_loss(
    predictions, targets, temperature_weight: float = 1.0, ventilation_weight: float = 1.0
):
    """Compute weighted L1 loss for temperature and ventilation outputs."""
    try:
        import torch
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("torch is required for loss computation.") from exc

    temp_loss = torch.nn.functional.l1_loss(predictions[:, 0], targets[:, 0])
    vent_loss = torch.nn.functional.l1_loss(predictions[:, 1], targets[:, 1])
    return temperature_weight * temp_loss + ventilation_weight * vent_loss
