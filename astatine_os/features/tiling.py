# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""AOI tiling for scalable processing."""

from __future__ import annotations

import math
from dataclasses import dataclass

from shapely.geometry import Polygon, box

from astatine_os.data.aoi import AOI


@dataclass(frozen=True)
class Tile:
    """Analysis tile geometry in WGS84."""

    tile_id: str
    geometry: Polygon

    @property
    def centroid_xy(self) -> tuple[float, float]:
        centroid = self.geometry.centroid
        return (float(centroid.x), float(centroid.y))


def _meter_to_degree_lat(tile_size_m: int) -> float:
    return tile_size_m / 111_320.0


def _meter_to_degree_lon(tile_size_m: int, lat: float) -> float:
    return tile_size_m / (111_320.0 * max(math.cos(math.radians(lat)), 0.2))


def tile_aoi(aoi: AOI, tile_size_m: int) -> list[Tile]:
    """Split AOI polygon into approximately square tiles."""
    minx, miny, maxx, maxy = aoi.bounds
    center_lat = (miny + maxy) / 2.0
    step_x = _meter_to_degree_lon(tile_size_m, center_lat)
    step_y = _meter_to_degree_lat(tile_size_m)

    tiles: list[Tile] = []
    idx = 0
    y = miny
    while y < maxy:
        x = minx
        while x < maxx:
            candidate = box(x, y, min(x + step_x, maxx), min(y + step_y, maxy))
            if candidate.intersects(aoi.geometry):
                geom = candidate.intersection(aoi.geometry)
                tiles.append(Tile(tile_id=f"tile_{idx:04d}", geometry=geom))
                idx += 1
            x += step_x
        y += step_y
    return tiles
