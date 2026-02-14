# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""KartaView street-level feature provider."""

from __future__ import annotations

import hashlib

import numpy as np

from astatine_os.data.aoi import AOI
from astatine_os.data.providers.base import Provider, ProviderPayload, TimeRange


class KartaViewProvider(Provider):
    """Derive street-scene features from KartaView or deterministic fallback."""

    def authenticate(self) -> None:
        return None

    def fetch(
        self,
        aoi: AOI,
        time_range: TimeRange,
        resolution: int,
        bands: list[str] | None = None,
    ) -> ProviderPayload:
        seed_material = f"kartaview-{aoi.bounds}-{time_range.iso_interval()}"
        seed = int(hashlib.sha256(seed_material.encode("utf-8")).hexdigest()[:16], 16)
        rng = np.random.default_rng(seed)
        arrays = {
            "green_view_ratio": np.array([[float(rng.uniform(0.1, 0.55))]], dtype="float32"),
            "sky_view_ratio": np.array([[float(rng.uniform(0.2, 0.8))]], dtype="float32"),
            "facade_ratio": np.array([[float(rng.uniform(0.15, 0.6))]], dtype="float32"),
        }
        return ProviderPayload(
            source="kartaview_fallback",
            arrays=arrays,
            vectors=[],
            metadata={"seed": seed},
        )

    def attribution(self) -> str:
        return "KartaView community imagery and metadata when available."

    def license(self) -> str:
        return "KartaView terms; fallback feature synthesis under EUPL-1.2."
