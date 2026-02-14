# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Integration test for end-to-end analyze flow with deterministic providers."""

from __future__ import annotations

import json
from pathlib import Path

from astatine_os.api import analyze_microclimate


def test_analyze_microclimate_outputs(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    result = analyze_microclimate(
        "Istanbul_Besiktas",
        start="2025-07-01",
        end="2025-07-03",
        out_dir=out_dir,
        config_overrides={
            "use_dask_distributed": False,
            "dask_workers": 1,
            "enable_optional_live_calls": False,
        },
    )

    assert result.temperature_geojson.exists()
    assert result.ventilation_geojson.exists()
    assert result.cool_refuges_geojson.exists()
    assert result.report_markdown.exists()

    summary_path = out_dir / "predictions_summary.json"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["place"] == "Istanbul_Besiktas"
    assert len(summary["tile_features"]) > 0
    assert len(summary["predictions"]) == len(summary["tile_features"])
