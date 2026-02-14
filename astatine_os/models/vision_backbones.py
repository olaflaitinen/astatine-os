# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Configurable vision encoders."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class VisionBackboneConfig:
    """Vision backbone configuration."""

    name: str = "vit_tiny_patch16_224"
    pretrained: bool = False
    in_chans: int = 3


def create_vision_backbone(config: VisionBackboneConfig) -> Any:
    """Create a timm vision model, with fallback tiny CNN."""
    try:
        import timm  # type: ignore[import-not-found]
        import torch.nn as nn
    except Exception:
        import torch.nn as nn  # type: ignore[import-not-found]

        return nn.Sequential(
            nn.Conv2d(config.in_chans, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(16, 128),
        )

    model = timm.create_model(
        config.name,
        pretrained=config.pretrained,
        in_chans=config.in_chans,
        num_classes=0,
        global_pool="avg",
    )
    return model
