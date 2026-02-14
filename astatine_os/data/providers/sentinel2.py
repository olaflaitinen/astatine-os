# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Sentinel-2 provider with public STAC metadata and deterministic arrays."""

from __future__ import annotations

import hashlib
from typing import Any

import numpy as np

from astatine_os.data.aoi import AOI
from astatine_os.data.providers.base import Provider, ProviderPayload, TimeRange
from astatine_os.data.stac import query_stac_items
from astatine_os.logging import get_logger

LOGGER = get_logger(__name__)


class Sentinel2Provider(Provider):
    """Default Sentinel-2 L2A provider."""

    def __init__(
        self,
        stac_url: str = "https://planetarycomputer.microsoft.com/api/stac/v1",
        use_live_stac: bool = False,
    ) -> None:
        self.stac_url = stac_url
        self.use_live_stac = use_live_stac

    def authenticate(self) -> None:
        return None

    def fetch(
        self,
        aoi: AOI,
        time_range: TimeRange,
        resolution: int,
        bands: list[str] | None = None,
    ) -> ProviderPayload:
        wanted_bands = bands or ["B04", "B08", "B11"]
        shape = (max(16, int(600 / resolution)), max(16, int(600 / resolution)))
        seed_material = f"{aoi.bounds}-{time_range.iso_interval()}-{resolution}-{wanted_bands}"
        seed = int(hashlib.sha256(seed_material.encode("utf-8")).hexdigest()[:16], 16)
        rng = np.random.default_rng(seed)

        arrays = {
            band: rng.uniform(0.05, 0.7, size=shape).astype("float32") for band in wanted_bands
        }
        metadata: dict[str, Any] = {"bands": wanted_bands, "shape": shape, "seed": seed}

        if self.use_live_stac:
            try:
                items = query_stac_items(
                    stac_url=self.stac_url,
                    collection="sentinel-2-l2a",
                    bbox=aoi.bounds,
                    datetime_range=time_range.iso_interval(),
                    limit=3,
                )
                metadata["stac_item_ids"] = [item.get("id", "unknown") for item in items]
            except Exception as exc:
                LOGGER.warning(
                    "Live STAC query failed; using deterministic arrays only.",
                    extra={"context": {"error": str(exc)}},
                )
                metadata["stac_item_ids"] = []
        else:
            metadata["stac_item_ids"] = []

        return ProviderPayload(
            source="sentinel2_l2a",
            arrays=arrays,
            vectors=[],
            metadata=metadata,
        )

    def attribution(self) -> str:
        return "Copernicus Sentinel data via Microsoft Planetary Computer STAC API."

    def license(self) -> str:
        return "Copernicus Sentinel data terms and conditions."
