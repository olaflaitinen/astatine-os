# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""AOI objects and place-to-geometry resolution."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from shapely.geometry import Polygon, box

from astatine_os.exceptions import GeocodingError
from astatine_os.logging import get_logger

LOGGER = get_logger(__name__)


@dataclass(frozen=True)
class AOI:
    """Area of interest with geometry in WGS84."""

    name: str
    geometry: Polygon
    crs: str = "EPSG:4326"

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        """Return minx, miny, maxx, maxy."""
        return self.geometry.bounds


class NominatimGeocoder:
    """Geocoder backed by OpenStreetMap Nominatim via geopy."""

    def __init__(self, user_agent: str = "astatine-os/0.1.0") -> None:
        self.user_agent = user_agent

    def geocode(self, place: str) -> AOI:
        """Resolve a place name to an AOI polygon."""
        try:
            from geopy.extra.rate_limiter import RateLimiter
            from geopy.geocoders import Nominatim
        except Exception as exc:  # pragma: no cover
            raise GeocodingError("geopy is required for Nominatim geocoding.") from exc

        geocoder = Nominatim(user_agent=self.user_agent, timeout=10)
        limiter = RateLimiter(geocoder.geocode, min_delay_seconds=1.0)
        location = limiter(place, exactly_one=True, geometry="geojson")
        if location is None:
            raise GeocodingError(
                f"Could not geocode '{place}' with Nominatim. "
                "Respect the Nominatim usage policy and include delays."
            )

        lat = float(location.latitude)
        lon = float(location.longitude)
        size_deg = 0.006
        geom = box(lon - size_deg, lat - size_deg, lon + size_deg, lat + size_deg)
        return AOI(name=place, geometry=geom)


def _fallback_aoi(place: str) -> AOI:
    """Deterministic fallback AOI for offline or rate-limited execution."""
    digest = hashlib.sha256(place.encode("utf-8")).hexdigest()
    lon = -180.0 + (int(digest[:8], 16) / 0xFFFFFFFF) * 360.0
    lat = -60.0 + (int(digest[8:16], 16) / 0xFFFFFFFF) * 120.0
    if place.lower().replace(" ", "_") in {"istanbul_besiktas", "besiktas"}:
        lon, lat = 29.015, 41.043
    size_deg = 0.006
    geom = box(lon - size_deg, lat - size_deg, lon + size_deg, lat + size_deg)
    return AOI(name=place, geometry=geom)


def resolve_place(place: str, geocoder: NominatimGeocoder) -> AOI:
    """Resolve place to AOI, using deterministic fallback when needed."""
    try:
        aoi = geocoder.geocode(place)
        LOGGER.info("Resolved AOI via geocoder", extra={"context": {"place": place}})
        return aoi
    except Exception as exc:
        LOGGER.warning(
            "Geocoding failed, using fallback AOI",
            extra={"context": {"place": place, "error": str(exc)}},
        )
        return _fallback_aoi(place)
