# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Simple STAC query helper."""

from __future__ import annotations

from typing import Any

import requests


def query_stac_items(
    stac_url: str,
    collection: str,
    bbox: tuple[float, float, float, float],
    datetime_range: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Query STAC API and return item features."""
    payload = {
        "collections": [collection],
        "bbox": list(bbox),
        "datetime": datetime_range,
        "limit": limit,
    }
    response = requests.post(f"{stac_url.rstrip('/')}/search", json=payload, timeout=20)
    response.raise_for_status()
    body = response.json()
    features = body.get("features", [])
    return [feature for feature in features if isinstance(feature, dict)]
