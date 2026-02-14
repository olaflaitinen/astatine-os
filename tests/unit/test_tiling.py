# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Unit tests for AOI tiling."""

from __future__ import annotations

from shapely.geometry import box

from astatine_os.data.aoi import AOI
from astatine_os.features.tiling import tile_aoi


def test_tiling_produces_multiple_tiles() -> None:
    aoi = AOI(name="test", geometry=box(29.0, 41.0, 29.02, 41.02))
    tiles = tile_aoi(aoi, tile_size_m=300)
    assert len(tiles) >= 4
    assert all(tile.geometry.area > 0 for tile in tiles)
