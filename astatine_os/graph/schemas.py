# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Typed schemas for graph learning and outputs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TileFeature:
    """Feature vector for one neighborhood tile."""

    tile_id: str
    lon: float
    lat: float
    ndvi: float
    ndbi: float
    albedo: float
    building_density: float
    mean_building_height_m: float
    green_view_ratio: float
    street_sky_ratio: float
    roughness_proxy: float
    canyon_aspect_ratio: float
    orientation_deg: float
    meteo_air_temp_c: float
    meteo_wind_m_s: float


@dataclass
class GraphPrediction:
    """Model output for one tile."""

    tile_id: str
    temperature_anomaly_c: float
    ventilation_score: float
