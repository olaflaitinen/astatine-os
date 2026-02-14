# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Inference orchestrator for graph predictions."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import networkx as nx

from astatine_os.graph.schemas import GraphPrediction, TileFeature


@dataclass
class InferenceEngine:
    """Run deterministic baseline inference for CI and demo stability."""

    deterministic: bool = True

    def predict(
        self,
        graph: nx.Graph,
        tile_features: Iterable[TileFeature],
    ) -> list[GraphPrediction]:
        """Predict micro heat anomaly and ventilation score for each tile."""
        feature_list = list(tile_features)
        by_tile = {feature.tile_id: feature for feature in feature_list}
        predictions: list[GraphPrediction] = []

        for tile_id, feature in by_tile.items():
            degree = graph.degree(tile_id) if graph.has_node(tile_id) else 0
            temp = (
                2.2 * feature.ndbi
                - 1.6 * feature.ndvi
                + 1.2 * feature.building_density
                + 0.8 * feature.roughness_proxy
                + 0.03 * (feature.meteo_air_temp_c - 25.0)
                - 0.15 * feature.meteo_wind_m_s
            )
            vent = (
                0.5
                + 0.4 * feature.street_sky_ratio
                - 0.35 * feature.canyon_aspect_ratio
                - 0.25 * feature.roughness_proxy
                + 0.20 * feature.green_view_ratio
                + 0.03 * degree
            )
            vent = max(0.0, min(1.0, vent))
            predictions.append(
                GraphPrediction(
                    tile_id=tile_id,
                    temperature_anomaly_c=float(temp),
                    ventilation_score=float(vent),
                )
            )
        return predictions
