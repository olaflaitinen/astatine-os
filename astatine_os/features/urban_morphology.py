# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Urban morphology feature extraction."""

from __future__ import annotations

import math
from typing import Any

from shapely.geometry import Polygon, shape

from astatine_os.data.aoi import AOI


def morphology_features(aoi: AOI, building_features: list[dict[str, Any]]) -> dict[str, float]:
    """Compute compact morphology features from footprint vectors."""
    tile_area = max(1e-9, aoi.geometry.area)
    building_area = 0.0
    heights: list[float] = []
    orientations: list[float] = []

    for feature in building_features:
        geom_obj = feature.get("geometry")
        if not isinstance(geom_obj, dict):
            continue
        geom = shape(geom_obj)
        if geom.geom_type == "MultiPolygon":
            geom = max(geom.geoms, key=lambda g: g.area)
        if not isinstance(geom, Polygon):
            continue
        building_area += geom.area
        minx, miny, maxx, maxy = geom.bounds
        dx = maxx - minx
        dy = maxy - miny
        angle = math.degrees(math.atan2(dy, max(dx, 1e-9)))
        orientations.append(angle)
        height = float(feature.get("properties", {}).get("height_m", 10.0))
        heights.append(height)

    density = min(0.98, building_area / tile_area)
    mean_height = sum(heights) / len(heights) if heights else 8.0
    orientation_mean = sum(orientations) / len(orientations) if orientations else 45.0
    roughness_proxy = density * mean_height / 20.0

    return {
        "building_density": float(density),
        "mean_building_height_m": float(mean_height),
        "street_orientation_deg": float(orientation_mean),
        "roughness_proxy": float(roughness_proxy),
    }
