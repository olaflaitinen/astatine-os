# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Street scene feature utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


def summarize_street_scene(
    green_view_ratio: np.ndarray,
    sky_view_ratio: np.ndarray,
    facade_ratio: np.ndarray,
) -> dict[str, float]:
    """Aggregate street-level segmentation-like ratios."""
    gvr = float(np.mean(green_view_ratio))
    svr = float(np.mean(sky_view_ratio))
    fcr = float(np.mean(facade_ratio))
    return {
        "green_view_ratio": gvr,
        "street_sky_ratio": svr,
        "street_facade_ratio": fcr,
    }


@dataclass(frozen=True)
class StreetSegmentationConfig:
    """Configuration for optional semantic segmentation inference."""

    model_name: str = "lraspp_mobilenet_v3_large"
    checkpoint_path: Path | None = None


def extract_scene_ratios_from_tensor(
    image_tensor,
    config: StreetSegmentationConfig | None = None,
) -> dict[str, float]:
    """Estimate scene class ratios from a torch image tensor.

    The tensor should be shaped as [C, H, W] with values in [0, 1].
    If segmentation dependencies are not installed, this function raises.
    """
    cfg = config or StreetSegmentationConfig()
    try:
        import torch
        import torchvision
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "torch and torchvision are required for street-level semantic segmentation."
        ) from exc

    if cfg.model_name != "lraspp_mobilenet_v3_large":
        raise ValueError(f"Unsupported model_name: {cfg.model_name}")

    model = torchvision.models.segmentation.lraspp_mobilenet_v3_large(weights="DEFAULT")
    model.eval()
    if cfg.checkpoint_path is not None and cfg.checkpoint_path.exists():
        state = torch.load(cfg.checkpoint_path, map_location="cpu")
        model.load_state_dict(state, strict=False)

    with torch.no_grad():
        logits = model(image_tensor.unsqueeze(0))["out"][0]
    probs = torch.softmax(logits, dim=0)
    # Approximate mappings:
    # 0 background, 2 vegetation-like, 10 sky-like (dataset dependent).
    green_ratio = float(probs[2].mean().item()) if probs.shape[0] > 2 else 0.2
    sky_ratio = float(probs[10].mean().item()) if probs.shape[0] > 10 else 0.4
    facade_ratio = float(max(0.0, min(1.0, 1.0 - green_ratio - sky_ratio)))
    return {
        "green_view_ratio": green_ratio,
        "street_sky_ratio": sky_ratio,
        "street_facade_ratio": facade_ratio,
    }
