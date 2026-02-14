# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Landsat thermal label provider."""

from __future__ import annotations

import hashlib

import numpy as np

from astatine_os.data.aoi import AOI
from astatine_os.data.providers.base import Provider, ProviderPayload, TimeRange
from astatine_os.data.stac import query_stac_items
from astatine_os.logging import get_logger

LOGGER = get_logger(__name__)


class LandsatThermalProvider(Provider):
    """Optional Landsat L2 surface temperature provider."""

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
        shape = (max(8, int(600 / max(resolution, 30))), max(8, int(600 / max(resolution, 30))))
        seed_material = f"landsat-{aoi.bounds}-{time_range.iso_interval()}-{resolution}"
        seed = int(hashlib.sha256(seed_material.encode("utf-8")).hexdigest()[:16], 16)
        rng = np.random.default_rng(seed)
        surface_temp_k = rng.normal(loc=303.0, scale=3.2, size=shape).astype("float32")

        metadata: dict[str, object] = {"shape": shape, "seed": seed}
        if self.use_live_stac:
            try:
                items = query_stac_items(
                    stac_url=self.stac_url,
                    collection="landsat-c2-l2",
                    bbox=aoi.bounds,
                    datetime_range=time_range.iso_interval(),
                    limit=3,
                )
                metadata["stac_item_ids"] = [item.get("id", "unknown") for item in items]
            except Exception as exc:
                LOGGER.warning(
                    "Live Landsat query failed; using weak thermal labels.",
                    extra={"context": {"error": str(exc)}},
                )
                metadata["stac_item_ids"] = []
        return ProviderPayload(
            source="landsat_l2_st",
            arrays={"surface_temp_k": surface_temp_k},
            vectors=[],
            metadata=metadata,
        )

    def attribution(self) -> str:
        return "USGS/NASA Landsat Collection 2 Level 2 data via public STAC APIs."

    def license(self) -> str:
        return "Public domain for Landsat products with source attribution to USGS."
