# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Provider interfaces for all external data sources."""

from __future__ import annotations

import abc
from dataclasses import dataclass
from datetime import date
from typing import Any

from astatine_os.data.aoi import AOI


@dataclass(frozen=True)
class TimeRange:
    """Time interval inclusive in ISO date format."""

    start: date
    end: date

    def iso_interval(self) -> str:
        """Return STAC-compatible datetime interval."""
        return f"{self.start.isoformat()}T00:00:00Z/{self.end.isoformat()}T23:59:59Z"


@dataclass
class ProviderPayload:
    """Generic provider response payload."""

    source: str
    arrays: dict[str, Any]
    vectors: list[dict[str, Any]]
    metadata: dict[str, Any]


class Provider(abc.ABC):
    """Abstract provider contract."""

    @abc.abstractmethod
    def authenticate(self) -> None:
        """Authenticate provider client if needed."""

    @abc.abstractmethod
    def fetch(
        self,
        aoi: AOI,
        time_range: TimeRange,
        resolution: int,
        bands: list[str] | None = None,
    ) -> ProviderPayload:
        """Fetch arrays and vectors for an AOI and time range."""

    @abc.abstractmethod
    def attribution(self) -> str:
        """Return provider attribution string."""

    @abc.abstractmethod
    def license(self) -> str:
        """Return provider data license string."""
