# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Unit tests for provider contracts with mocked provider."""

from __future__ import annotations

from datetime import date

from shapely.geometry import box

from astatine_os.data.aoi import AOI
from astatine_os.data.providers.base import Provider, ProviderPayload, TimeRange


class MockProvider(Provider):
    def authenticate(self) -> None:
        return None

    def fetch(
        self,
        aoi: AOI,
        time_range: TimeRange,
        resolution: int,
        bands: list[str] | None = None,
    ) -> ProviderPayload:
        return ProviderPayload(
            source="mock",
            arrays={"x": 1},
            vectors=[],
            metadata={
                "bounds": aoi.bounds,
                "time": time_range.iso_interval(),
                "resolution": resolution,
            },
        )

    def attribution(self) -> str:
        return "mock-attribution"

    def license(self) -> str:
        return "mock-license"


def test_provider_contract() -> None:
    provider = MockProvider()
    aoi = AOI(name="test", geometry=box(0.0, 0.0, 1.0, 1.0))
    payload = provider.fetch(aoi, TimeRange(start=date(2025, 1, 1), end=date(2025, 1, 2)), 10)
    assert payload.source == "mock"
    assert provider.attribution() == "mock-attribution"
