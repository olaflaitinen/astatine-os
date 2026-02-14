# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Raster output helpers, including optional COG export."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from astatine_os.logging import get_logger

LOGGER = get_logger(__name__)


def write_optional_cog(path: Path, raster: np.ndarray) -> Path | None:
    """Write a COG GeoTIFF when rasterio is available, else return None."""
    try:
        import rasterio
        from rasterio.enums import Resampling
        from rasterio.shutil import copy as rio_copy
        from rasterio.transform import from_origin
    except Exception:
        LOGGER.warning("rasterio is unavailable; skipping COG export.")
        return None

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp.tif")
    profile = {
        "driver": "GTiff",
        "height": raster.shape[0],
        "width": raster.shape[1],
        "count": 1,
        "dtype": str(raster.dtype),
        "crs": "EPSG:4326",
        "transform": from_origin(0, 0, 1, 1),
        "compress": "DEFLATE",
        "tiled": True,
        "blockxsize": 256,
        "blockysize": 256,
    }
    with rasterio.open(tmp, "w", **profile) as dst:
        dst.write(raster, 1)
        dst.build_overviews([2, 4, 8], Resampling.average)
        dst.update_tags(ns="rio_overview", resampling="average")
    rio_copy(tmp, path, driver="COG")
    tmp.unlink(missing_ok=True)
    return path
