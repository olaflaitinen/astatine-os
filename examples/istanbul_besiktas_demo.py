# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""End-to-end demo for Istanbul Besiktas."""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import requests

import astatine_os as at

PUBLIC_SAMPLE_URL = "https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a"


def _download_public_sample(out_dir: Path) -> Path | None:
    """Download a tiny public metadata sample to document data provenance."""
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "public_sample_sentinel2_collection.json"
    try:
        response = requests.get(PUBLIC_SAMPLE_URL, timeout=20)
        response.raise_for_status()
        target.write_text(json.dumps(response.json(), indent=2), encoding="utf-8")
        return target
    except Exception:
        return None


def main() -> None:
    warnings.filterwarnings("ignore", message=".*Zarr V3 specification.*")
    warnings.filterwarnings("ignore", message=".*Consolidated metadata.*")
    try:
        import rasterio.errors as rio_errors
    except Exception:
        not_georef_warning = Warning
    else:
        not_georef_warning = getattr(rio_errors, "NotGeoreferencedWarning", Warning)
    warnings.filterwarnings("ignore", category=not_georef_warning)

    out_dir = Path("./out").resolve()
    sample = _download_public_sample(out_dir)
    if sample is not None:
        print(f"Downloaded public sample metadata: {sample}")
    else:
        print("Public sample download skipped due to connectivity or provider limits.")

    result = at.analyze_microclimate(
        "Istanbul_Besiktas",
        start="2025-07-01",
        end="2025-07-31",
        out_dir=out_dir,
        config_overrides={"use_dask_distributed": False, "dask_workers": 1},
    )
    print("Analysis complete.")
    print(f"Output directory: {result.output_dir}")
    print(f"Temperature layer: {result.temperature_geojson}")
    print(f"Ventilation layer: {result.ventilation_geojson}")
    print(f"Cool refuges layer: {result.cool_refuges_geojson}")
    print(f"Report: {result.report_markdown}")
    if result.optional_temperature_cog:
        print(f"COG raster: {result.optional_temperature_cog}")
    else:
        print("COG raster: skipped (rasterio unavailable)")


if __name__ == "__main__":
    main()
