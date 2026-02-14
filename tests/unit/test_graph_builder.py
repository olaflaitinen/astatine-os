# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Unit tests for airflow graph construction."""

from __future__ import annotations

from astatine_os.graph.build_graph import build_airflow_graph
from astatine_os.graph.schemas import TileFeature


def _feature(tile_id: str, lon: float, lat: float) -> TileFeature:
    return TileFeature(
        tile_id=tile_id,
        lon=lon,
        lat=lat,
        ndvi=0.2,
        ndbi=0.3,
        albedo=0.4,
        building_density=0.3,
        mean_building_height_m=12.0,
        green_view_ratio=0.2,
        street_sky_ratio=0.5,
        roughness_proxy=0.2,
        canyon_aspect_ratio=0.6,
        orientation_deg=40.0,
        meteo_air_temp_c=30.0,
        meteo_wind_m_s=3.0,
    )


def test_graph_has_edges() -> None:
    features = [
        _feature("a", 0.0, 0.0),
        _feature("b", 0.01, 0.0),
        _feature("c", 0.0, 0.01),
        _feature("d", 0.01, 0.01),
    ]
    graph = build_airflow_graph(features, k_neighbors=2)
    assert graph.number_of_nodes() == 4
    assert graph.number_of_edges() >= 4
