# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Actionable recommendation engine."""

from __future__ import annotations

from astatine_os.graph.schemas import GraphPrediction, TileFeature


def tree_planting_recommendations(
    tile_features: list[TileFeature],
    predictions: list[GraphPrediction],
) -> list[dict[str, object]]:
    """Generate tile-level recommendations from model outputs."""
    by_id = {feature.tile_id: feature for feature in tile_features}
    recommendations: list[dict[str, object]] = []
    for pred in predictions:
        feature = by_id[pred.tile_id]
        if pred.temperature_anomaly_c < 0.5:
            continue
        if feature.green_view_ratio >= 0.25:
            continue
        tree_count = int(max(4, round(12 * pred.temperature_anomaly_c)))
        recommendations.append(
            {
                "tile_id": pred.tile_id,
                "priority": "high" if pred.temperature_anomaly_c > 1.5 else "medium",
                "recommended_tree_count": tree_count,
                "rationale": (
                    "High thermal anomaly and low existing green view indicate"
                    " strong cooling potential from canopy expansion."
                ),
            }
        )
    return recommendations
