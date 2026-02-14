# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""OpenStreetMap building provider using OSMnx when available."""

from __future__ import annotations

from typing import Any

from shapely.geometry import Polygon, mapping, shape

from astatine_os.data.aoi import AOI
from astatine_os.data.providers.base import Provider, ProviderPayload, TimeRange
from astatine_os.data.providers.buildings_open_buildings import OpenBuildingsProvider
from astatine_os.logging import get_logger

LOGGER = get_logger(__name__)


class OSMBuildingsProvider(Provider):
    """Fetch OSM building footprints with fallback to deterministic footprints."""

    def __init__(self) -> None:
        self._fallback = OpenBuildingsProvider()

    def authenticate(self) -> None:
        return None

    def fetch(
        self,
        aoi: AOI,
        time_range: TimeRange,
        resolution: int,
        bands: list[str] | None = None,
    ) -> ProviderPayload:
        try:
            import osmnx as ox  # type: ignore[import-not-found]
        except Exception:
            LOGGER.info("OSMnx unavailable; using building fallback provider.")
            return self._fallback.fetch(aoi, time_range, resolution, bands)

        try:
            gdf = ox.features_from_polygon(aoi.geometry, {"building": True})
        except Exception as exc:
            LOGGER.warning(
                "OSM building fetch failed; using fallback provider.",
                extra={"context": {"error": str(exc)}},
            )
            return self._fallback.fetch(aoi, time_range, resolution, bands)

        vectors: list[dict[str, Any]] = []
        for _, row in gdf.head(100).iterrows():
            geom = row.geometry
            if geom is None:
                continue
            if geom.geom_type == "MultiPolygon":
                geom = max(geom.geoms, key=lambda g: g.area)
            if not isinstance(geom, Polygon):
                geom = shape(mapping(geom))
            vectors.append(
                {
                    "type": "Feature",
                    "geometry": mapping(geom),
                    "properties": {"provider": "osm", "height_m": 12.0},
                }
            )
        return ProviderPayload(
            source="osm_buildings",
            arrays={},
            vectors=vectors,
            metadata={"footprint_count": len(vectors)},
        )

    def attribution(self) -> str:
        return "OpenStreetMap contributors via OSMnx."

    def license(self) -> str:
        return "ODbL 1.0 for OpenStreetMap data."
