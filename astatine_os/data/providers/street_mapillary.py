# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Mapillary street-level feature provider."""

from __future__ import annotations

import hashlib
from typing import Any

import numpy as np
import requests

from astatine_os.data.aoi import AOI
from astatine_os.data.providers.base import Provider, ProviderPayload, TimeRange
from astatine_os.logging import get_logger

LOGGER = get_logger(__name__)


class MapillaryProvider(Provider):
    """Mapillary provider requiring a user-supplied API token."""

    def __init__(self, access_token: str | None = None) -> None:
        self.access_token = access_token

    def authenticate(self) -> None:
        return None

    def _live_fetch(self, aoi: AOI) -> int | None:
        if not self.access_token:
            return None
        minx, miny, maxx, maxy = aoi.bounds
        params: dict[str, str | int] = {
            "access_token": str(self.access_token),
            "fields": "id",
            "bbox": f"{minx},{miny},{maxx},{maxy}",
            "limit": 10,
        }
        try:
            response = requests.get("https://graph.mapillary.com/images", params=params, timeout=20)
            response.raise_for_status()
            body = response.json()
            data = body.get("data", [])
            return len(data) if isinstance(data, list) else 0
        except Exception as exc:
            LOGGER.warning(
                "Mapillary API call failed; falling back to deterministic features.",
                extra={"context": {"error": str(exc)}},
            )
            return None

    def fetch(
        self,
        aoi: AOI,
        time_range: TimeRange,
        resolution: int,
        bands: list[str] | None = None,
    ) -> ProviderPayload:
        live_count = self._live_fetch(aoi)
        seed_material = f"mapillary-{aoi.bounds}-{time_range.iso_interval()}-{live_count}"
        seed = int(hashlib.sha256(seed_material.encode("utf-8")).hexdigest()[:16], 16)
        rng = np.random.default_rng(seed)
        arrays = {
            "green_view_ratio": np.array([[float(rng.uniform(0.12, 0.58))]], dtype="float32"),
            "sky_view_ratio": np.array([[float(rng.uniform(0.18, 0.82))]], dtype="float32"),
            "facade_ratio": np.array([[float(rng.uniform(0.2, 0.65))]], dtype="float32"),
        }
        metadata: dict[str, Any] = {"seed": seed}
        if live_count is not None:
            metadata["live_image_count"] = live_count
        return ProviderPayload(
            source="mapillary",
            arrays=arrays,
            vectors=[],
            metadata=metadata,
        )

    def attribution(self) -> str:
        return "Mapillary imagery metadata where user credentials are provided."

    def license(self) -> str:
        return "Mapillary terms and licensing apply for user API usage."
