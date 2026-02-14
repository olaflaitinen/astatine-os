# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Open Buildings provider with deterministic fallback geometry."""

from __future__ import annotations

import hashlib
from typing import Any

from shapely.geometry import box, mapping

from astatine_os.data.aoi import AOI
from astatine_os.data.providers.base import Provider, ProviderPayload, TimeRange


class OpenBuildingsProvider(Provider):
    """Open Buildings footprint provider.

    The default implementation generates deterministic synthetic footprints
    when direct Open Buildings access is unavailable.
    """

    def authenticate(self) -> None:
        return None

    def fetch(
        self,
        aoi: AOI,
        time_range: TimeRange,
        resolution: int,
        bands: list[str] | None = None,
    ) -> ProviderPayload:
        minx, miny, maxx, maxy = aoi.bounds
        seed_material = f"open-buildings-{aoi.bounds}-{time_range.iso_interval()}"
        seed = int(hashlib.sha256(seed_material.encode("utf-8")).hexdigest()[:8], 16)
        step_x = (maxx - minx) / 5.0
        step_y = (maxy - miny) / 5.0
        vectors: list[dict[str, Any]] = []
        for i in range(4):
            for j in range(4):
                jitter = ((seed + i * 17 + j * 13) % 1000) / 1_000_000.0
                geom = box(
                    minx + i * step_x + jitter,
                    miny + j * step_y + jitter,
                    minx + i * step_x + step_x * 0.55 + jitter,
                    miny + j * step_y + step_y * 0.55 + jitter,
                )
                vectors.append(
                    {
                        "type": "Feature",
                        "geometry": mapping(geom),
                        "properties": {
                            "height_m": 8.0 + ((i + j) % 6) * 4.0,
                            "provider": "open_buildings_fallback",
                        },
                    }
                )
        return ProviderPayload(
            source="open_buildings",
            arrays={},
            vectors=vectors,
            metadata={"seed": seed, "footprint_count": len(vectors)},
        )

    def attribution(self) -> str:
        return "Google Open Buildings and derivative fallback geometries by astatine_os."

    def license(self) -> str:
        return "Open Buildings data license where used; fallback geometry under EUPL-1.2."
