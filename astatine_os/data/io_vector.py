# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Vector file IO for GeoJSON and GeoParquet."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq


def write_geojson(path: Path, features: list[dict[str, Any]]) -> Path:
    """Write a feature collection to GeoJSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    collection = {"type": "FeatureCollection", "features": features}
    path.write_text(json.dumps(collection, indent=2), encoding="utf-8")
    return path


def write_geoparquet(path: Path, records: list[dict[str, Any]]) -> Path:
    """Write records to GeoParquet-style table with WKT geometries."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if records:
        table = pa.Table.from_pylist(records)
    else:
        table = pa.table({"tile_id": pa.array([], type=pa.string())})
    pq.write_table(table, path)
    return path
