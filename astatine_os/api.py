# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""High-level API for neighborhood microclimate analysis."""

from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any, Protocol

import dask
import numpy as np
from shapely.geometry import mapping

from astatine_os.config import get_runtime_config
from astatine_os.data.aoi import AOI, NominatimGeocoder, resolve_place
from astatine_os.data.cache import CacheStore
from astatine_os.data.io_raster import write_optional_cog
from astatine_os.data.io_vector import write_geojson, write_geoparquet
from astatine_os.data.providers import (
    ERA5LandProvider,
    KartaViewProvider,
    LandsatThermalProvider,
    MapillaryProvider,
    OpenBuildingsProvider,
    OSMBuildingsProvider,
    Sentinel2Provider,
    TimeRange,
)
from astatine_os.features.spectral_indices import compute_albedo_proxy, compute_ndbi, compute_ndvi
from astatine_os.features.street_scene import summarize_street_scene
from astatine_os.features.tiling import Tile, tile_aoi
from astatine_os.features.urban_morphology import morphology_features
from astatine_os.graph.build_graph import build_airflow_graph
from astatine_os.graph.physics_proxies import compute_physics_proxies
from astatine_os.graph.schemas import TileFeature
from astatine_os.logging import configure_logging, get_logger
from astatine_os.models.inference import InferenceEngine
from astatine_os.reporting.report_md import write_markdown_report

LOGGER = get_logger(__name__)


class GeocoderProtocol(Protocol):
    """Protocol for pluggable geocoder implementations."""

    def geocode(self, place: str) -> AOI:
        """Resolve place name to AOI."""


@dataclass
class AnalysisResult:
    """Materialized outputs from a complete analysis run."""

    output_dir: Path
    temperature_geojson: Path
    ventilation_geojson: Path
    cool_refuges_geojson: Path
    report_markdown: Path
    optional_temperature_cog: Path | None


def _seed_everything(seed: int, deterministic: bool) -> None:
    random.seed(seed)
    np.random.seed(seed)
    if deterministic:
        try:
            import torch

            torch.manual_seed(seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(seed)
            torch.use_deterministic_algorithms(True, warn_only=True)
        except Exception:
            pass


def _tile_payload(
    tile: Tile,
    time_range: TimeRange,
    resolution_m: int,
    sentinel_provider: Sentinel2Provider,
    landsat_provider: LandsatThermalProvider,
    meteo_provider: ERA5LandProvider,
    buildings_provider: OpenBuildingsProvider,
    buildings_fallback_provider: OSMBuildingsProvider,
    street_provider: KartaViewProvider,
) -> tuple[TileFeature, dict[str, Any]]:
    aoi = AOI(name=tile.tile_id, geometry=tile.geometry)

    sat = sentinel_provider.fetch(
        aoi, time_range, resolution=resolution_m, bands=["B04", "B08", "B11"]
    )
    thermal = landsat_provider.fetch(aoi, time_range, resolution=30, bands=["surface_temp_k"])
    meteo = meteo_provider.fetch(
        aoi, time_range, resolution=1, bands=["air_temp_c", "wind_speed_m_s"]
    )
    buildings = buildings_provider.fetch(aoi, time_range, resolution=resolution_m, bands=None)
    if not buildings.vectors:
        buildings = buildings_fallback_provider.fetch(
            aoi, time_range, resolution=resolution_m, bands=None
        )
    street = street_provider.fetch(aoi, time_range, resolution=resolution_m, bands=None)

    red = sat.arrays["B04"]
    nir = sat.arrays["B08"]
    swir = sat.arrays["B11"]
    ndvi = compute_ndvi(nir, red)
    ndbi = compute_ndbi(swir, nir)
    albedo = compute_albedo_proxy(red, nir, swir)

    morph = morphology_features(aoi, buildings.vectors)
    street_summary = summarize_street_scene(
        green_view_ratio=street.arrays["green_view_ratio"],
        sky_view_ratio=street.arrays["sky_view_ratio"],
        facade_ratio=street.arrays["facade_ratio"],
    )
    vegetation_fraction = float(
        np.clip(float(np.mean(ndvi) * 0.6 + street_summary["green_view_ratio"] * 0.4), 0.0, 1.0)
    )
    physics = compute_physics_proxies(
        building_density=morph["building_density"],
        mean_building_height_m=morph["mean_building_height_m"],
        street_width_m=18.0,
        street_orientation_deg=morph["street_orientation_deg"],
        vegetation_fraction=vegetation_fraction,
        green_view_ratio=street_summary["green_view_ratio"],
    )
    centroid_x, centroid_y = tile.centroid_xy
    feature = TileFeature(
        tile_id=tile.tile_id,
        lon=centroid_x,
        lat=centroid_y,
        ndvi=float(np.mean(ndvi)),
        ndbi=float(np.mean(ndbi)),
        albedo=float(np.mean(albedo)),
        building_density=morph["building_density"],
        mean_building_height_m=morph["mean_building_height_m"],
        green_view_ratio=street_summary["green_view_ratio"],
        street_sky_ratio=street_summary["street_sky_ratio"],
        roughness_proxy=physics["roughness_proxy"],
        canyon_aspect_ratio=physics["canyon_aspect_ratio"],
        orientation_deg=morph["street_orientation_deg"],
        meteo_air_temp_c=float(np.mean(meteo.arrays["air_temp_c"])),
        meteo_wind_m_s=float(np.mean(meteo.arrays["wind_speed_m_s"])),
    )
    meta = {
        "tile_id": tile.tile_id,
        "thermal_mean_k": float(np.mean(thermal.arrays["surface_temp_k"])),
        "provider_metadata": {
            "sentinel": sat.metadata,
            "landsat": thermal.metadata,
            "meteo": meteo.metadata,
            "buildings": buildings.metadata,
            "street": street.metadata,
        },
    }
    return feature, meta


def analyze_microclimate(
    place: str,
    start: str = "2025-07-01",
    end: str = "2025-07-31",
    out_dir: str | Path = "./out",
    geocoder: GeocoderProtocol | None = None,
    config_overrides: dict[str, Any] | None = None,
) -> AnalysisResult:
    """Analyze neighborhood micro heat islands and ventilation barriers."""
    configure_logging()
    overrides = dict(config_overrides or {})
    overrides["out_dir"] = Path(out_dir)
    cfg = get_runtime_config(**overrides)
    _seed_everything(cfg.seed, cfg.deterministic)
    cfg.cache_dir.mkdir(parents=True, exist_ok=True)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    cache = CacheStore(cfg.cache_dir)

    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    time_range = TimeRange(start=start_date, end=end_date)

    geocoder_impl = geocoder or NominatimGeocoder(user_agent=cfg.geocoder_user_agent)
    aoi = resolve_place(place, geocoder_impl)  # type: ignore[arg-type]

    tiles = tile_aoi(aoi, tile_size_m=cfg.tile_size_m)
    if not tiles:
        raise ValueError(f"No tiles generated for AOI {aoi.name}")

    sentinel = Sentinel2Provider(use_live_stac=cfg.enable_optional_live_calls)
    landsat = LandsatThermalProvider(use_live_stac=cfg.enable_optional_live_calls)
    meteo = ERA5LandProvider(cfg.era5_cds_url, cfg.era5_cds_key)
    buildings = OpenBuildingsProvider()
    buildings_fallback = OSMBuildingsProvider()
    street = KartaViewProvider()

    delayed_tasks = [
        dask.delayed(_tile_payload)(
            tile=tile,
            time_range=time_range,
            resolution_m=cfg.resolution_m,
            sentinel_provider=sentinel,
            landsat_provider=landsat,
            meteo_provider=meteo,
            buildings_provider=buildings,
            buildings_fallback_provider=buildings_fallback,
            street_provider=street,
        )
        for tile in tiles
    ]

    tile_outputs: list[tuple[TileFeature, dict[str, Any]]]
    if cfg.use_dask_distributed:
        try:
            from dask.distributed import Client, LocalCluster
        except Exception:
            tile_outputs = list(dask.compute(*delayed_tasks))
        else:
            cluster = LocalCluster(
                n_workers=cfg.dask_workers,
                threads_per_worker=cfg.dask_threads_per_worker,
                processes=False,
                dashboard_address=None,
                silence_logs=50,
            )
            client = Client(cluster)
            try:
                tile_outputs = list(client.gather(client.compute(delayed_tasks)))
            finally:
                client.close()
                cluster.close()
    else:
        tile_outputs = list(dask.compute(*delayed_tasks))

    tile_features = [item[0] for item in tile_outputs]
    per_tile_metadata = [item[1] for item in tile_outputs]

    airflow_graph = build_airflow_graph(tile_features)
    predictions = InferenceEngine(deterministic=cfg.deterministic).predict(
        airflow_graph, tile_features
    )

    tile_geoms = {tile.tile_id: tile.geometry for tile in tiles}
    temp_features: list[dict[str, Any]] = []
    vent_features: list[dict[str, Any]] = []
    refuge_features: list[dict[str, Any]] = []
    prediction_map = {pred.tile_id: pred for pred in predictions}
    feature_map = {feature.tile_id: feature for feature in tile_features}

    for tile_id, pred in prediction_map.items():
        tile_feature = feature_map[tile_id]
        geom = tile_geoms[tile_id]
        temp_feature = {
            "type": "Feature",
            "geometry": mapping(geom),
            "properties": {
                "tile_id": tile_id,
                "temperature_anomaly_c": pred.temperature_anomaly_c,
            },
        }
        vent_feature = {
            "type": "Feature",
            "geometry": mapping(geom),
            "properties": {
                "tile_id": tile_id,
                "ventilation_score": pred.ventilation_score,
            },
        }
        temp_features.append(temp_feature)
        vent_features.append(vent_feature)

        if (
            pred.temperature_anomaly_c < 0.5
            and pred.ventilation_score > 0.6
            and tile_feature.ndvi > 0.2
        ):
            refuge_features.append(
                {
                    "type": "Feature",
                    "geometry": mapping(geom),
                    "properties": {
                        "tile_id": tile_id,
                        "cool_refuge_rank": round(
                            0.5 * (1.0 - pred.temperature_anomaly_c) + 0.5 * pred.ventilation_score,
                            3,
                        ),
                    },
                }
            )

    temperature_geojson = write_geojson(cfg.out_dir / "temperature_anomaly.geojson", temp_features)
    ventilation_geojson = write_geojson(cfg.out_dir / "ventilation_score.geojson", vent_features)
    refuges_geojson = write_geojson(cfg.out_dir / "cool_refuges.geojson", refuge_features)

    geoparquet_records = []
    for pred in predictions:
        geom_wkt = tile_geoms[pred.tile_id].wkt
        feature = feature_map[pred.tile_id]
        geoparquet_records.append(
            {
                "tile_id": pred.tile_id,
                "geometry": geom_wkt,
                "temperature_anomaly_c": pred.temperature_anomaly_c,
                "ventilation_score": pred.ventilation_score,
                "ndvi": feature.ndvi,
                "ndbi": feature.ndbi,
            }
        )
    write_geoparquet(cfg.out_dir / "predictions.geoparquet", geoparquet_records)

    try:
        import xarray as xr

        ds = xr.Dataset(
            {
                "temperature_anomaly_c": (
                    "tile",
                    np.array([p.temperature_anomaly_c for p in predictions]),
                ),
                "ventilation_score": ("tile", np.array([p.ventilation_score for p in predictions])),
                "ndvi": ("tile", np.array([feature_map[p.tile_id].ndvi for p in predictions])),
                "ndbi": ("tile", np.array([feature_map[p.tile_id].ndbi for p in predictions])),
            },
            coords={"tile": np.array([p.tile_id for p in predictions])},
        )
        ds.to_zarr(cfg.out_dir / "intermediate_tiles.zarr", mode="w")
    except Exception as exc:
        LOGGER.warning(
            "Failed to write Zarr intermediate output.",
            extra={"context": {"error": str(exc)}},
        )

    square = int(np.ceil(np.sqrt(len(predictions))))
    raster = np.zeros((square, square), dtype="float32")
    for idx, pred in enumerate(predictions):
        y = idx // square
        x = idx % square
        raster[y, x] = pred.temperature_anomaly_c
    cog_path = write_optional_cog(cfg.out_dir / "temperature_anomaly.cog.tif", raster)

    assumptions = [
        "Deterministic fallback features are used when live providers are unavailable.",
        "Thermal labels use Landsat-style synthetic priors when no clear-sky thermal scene is retrieved.",
        "Tree planting recommendations are heuristic and should be validated with local planners.",
    ]
    report_path = write_markdown_report(
        path=cfg.out_dir / "report.md",
        place=place,
        start_date=start,
        end_date=end,
        tile_features=tile_features,
        predictions=predictions,
        assumptions=assumptions,
    )

    summary = {
        "place": place,
        "aoi_bounds": aoi.bounds,
        "time_range": {"start": start, "end": end},
        "tile_features": [asdict(item) for item in tile_features],
        "predictions": [asdict(item) for item in predictions],
        "assumptions": assumptions,
        "provider_details": per_tile_metadata,
        "attribution": {
            "sentinel2": sentinel.attribution(),
            "landsat": landsat.attribution(),
            "era5_land": meteo.attribution(),
            "open_buildings": buildings.attribution(),
            "osm_fallback": buildings_fallback.attribution(),
            "kartaview": street.attribution(),
            "mapillary_optional": MapillaryProvider(cfg.mapillary_access_token).attribution(),
        },
    }
    summary_path = cfg.out_dir / "predictions_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    cache_key = cache.make_key(
        {
            "place": place,
            "start": start,
            "end": end,
            "tile_count": len(tile_features),
            "seed": cfg.seed,
        }
    )
    cache.save_json(cache_key, summary)

    LOGGER.info(
        "Completed analysis",
        extra={
            "context": {
                "place": place,
                "tiles": len(tiles),
                "out_dir": str(cfg.out_dir),
                "cache_key": cache_key,
            }
        },
    )

    return AnalysisResult(
        output_dir=cfg.out_dir,
        temperature_geojson=temperature_geojson,
        ventilation_geojson=ventilation_geojson,
        cool_refuges_geojson=refuges_geojson,
        report_markdown=report_path,
        optional_temperature_cog=cog_path,
    )
