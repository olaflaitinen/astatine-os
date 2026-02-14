# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Optional live connectivity test guarded by environment variable."""

from __future__ import annotations

import os

import pytest

from astatine_os.data.stac import query_stac_items


@pytest.mark.skipif(
    os.getenv("ASTATINE_OS_RUN_LIVE_TESTS") != "1",
    reason="Set ASTATINE_OS_RUN_LIVE_TESTS=1 to run live provider test.",
)
def test_live_stac_query() -> None:
    items = query_stac_items(
        stac_url="https://planetarycomputer.microsoft.com/api/stac/v1",
        collection="sentinel-2-l2a",
        bbox=(29.0, 41.0, 29.02, 41.02),
        datetime_range="2025-07-01T00:00:00Z/2025-07-05T23:59:59Z",
        limit=1,
    )
    assert isinstance(items, list)
