# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Provider implementations."""

from astatine_os.data.providers.base import Provider, ProviderPayload, TimeRange
from astatine_os.data.providers.buildings_open_buildings import OpenBuildingsProvider
from astatine_os.data.providers.buildings_osm import OSMBuildingsProvider
from astatine_os.data.providers.era5_land import ERA5LandProvider
from astatine_os.data.providers.landsat import LandsatThermalProvider
from astatine_os.data.providers.sentinel2 import Sentinel2Provider
from astatine_os.data.providers.street_kartaview import KartaViewProvider
from astatine_os.data.providers.street_mapillary import MapillaryProvider

__all__ = [
    "ERA5LandProvider",
    "KartaViewProvider",
    "LandsatThermalProvider",
    "MapillaryProvider",
    "OpenBuildingsProvider",
    "OSMBuildingsProvider",
    "Provider",
    "ProviderPayload",
    "Sentinel2Provider",
    "TimeRange",
]
