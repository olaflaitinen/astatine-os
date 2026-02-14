# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Markdown report generation."""

from __future__ import annotations

from pathlib import Path

from astatine_os.graph.schemas import GraphPrediction, TileFeature
from astatine_os.reporting.recommendations import tree_planting_recommendations


def write_markdown_report(
    path: Path,
    place: str,
    start_date: str,
    end_date: str,
    tile_features: list[TileFeature],
    predictions: list[GraphPrediction],
    assumptions: list[str],
) -> Path:
    """Render analysis output to a human-readable markdown report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    recs = tree_planting_recommendations(tile_features, predictions)
    avg_temp = sum(item.temperature_anomaly_c for item in predictions) / max(len(predictions), 1)
    avg_vent = sum(item.ventilation_score for item in predictions) / max(len(predictions), 1)
    lines = [
        f"# Microclimate Report: {place}",
        "",
        "## Scope",
        f"- Time window: {start_date} to {end_date}",
        f"- Tiles analyzed: {len(tile_features)}",
        "",
        "## Key Results",
        f"- Mean predicted temperature anomaly: {avg_temp:.2f} C",
        f"- Mean ventilation score: {avg_vent:.2f} (0 to 1)",
        "",
        "## Methodology",
        "- Sentinel-2 reflectance-derived indices: NDVI, NDBI, albedo proxy.",
        "- Urban morphology from footprint geometry and street scene ratios.",
        "- Graph-based neighborhood representation with deterministic baseline inference.",
        "",
        "## Assumptions and Limitations",
    ]
    lines.extend(f"- {item}" for item in assumptions)
    lines.append("")
    lines.append("## Tree Planting Recommendations")
    if not recs:
        lines.append("- No high-priority planting zones were detected in this run.")
    else:
        for rec in recs:
            lines.append(
                f"- {rec['tile_id']}: priority={rec['priority']}, "
                f"trees={rec['recommended_tree_count']}. {rec['rationale']}"
            )
    lines.append("")
    lines.append("## Attribution")
    lines.append("- Open data providers are listed in DATA_SOURCES.md.")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
