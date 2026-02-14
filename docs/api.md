<!-- SPDX-License-Identifier: EUPL-1.2 -->
<!-- Copyright (c) 2026 Astatine OS Contributors -->

# API reference

## 1. High-level Python API

```python
import astatine_os as at

result = at.analyze_microclimate(
    place="Istanbul_Besiktas",
    start="2025-07-01",
    end="2025-07-31",
    out_dir="./out",
    config_overrides={"dask_workers": 2},
)
```

## 2. `analyze_microclimate` parameter schema

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `place` | `str` | yes | none | place name for AOI resolution |
| `start` | `str` | no | `2025-07-01` | ISO start date |
| `end` | `str` | no | `2025-07-31` | ISO end date |
| `out_dir` | `str | Path` | no | `./out` | output directory |
| `geocoder` | protocol | no | Nominatim | pluggable geocoder |
| `config_overrides` | `dict` | no | `{}` | runtime settings override |

## 3. Analysis result object

| Field | Type | Meaning |
| --- | --- | --- |
| `output_dir` | `Path` | root output folder |
| `temperature_geojson` | `Path` | tile anomaly layer |
| `ventilation_geojson` | `Path` | tile ventilation layer |
| `cool_refuges_geojson` | `Path` | candidate cool refuges |
| `report_markdown` | `Path` | human-readable report |
| `optional_temperature_cog` | `Path | None` | COG raster if rasterio is available |

## 4. CLI command contracts

### 4.1 `analyze`

```bash
astatine-os analyze --place Istanbul_Besiktas --start 2025-07-01 --end 2025-07-31 --out ./out
```

### 4.2 `data list-providers`

```bash
astatine-os data list-providers
```

### 4.3 `data fetch`

```bash
astatine-os data fetch --place Istanbul_Besiktas --start 2025-07-01 --end 2025-07-03 --out ./out_fetch
```

### 4.4 `train`

```bash
astatine-os train --out ./out_train --epochs 3
```

### 4.5 `eval`

```bash
astatine-os eval --checkpoint ./out_train/example.ckpt
```

### 4.6 `report`

```bash
astatine-os report --place Istanbul_Besiktas --start 2025-07-01 --end 2025-07-03 --out ./out
```

## 5. Provider interface

All data providers implement:

| Method | Signature | Responsibility |
| --- | --- | --- |
| `authenticate` | `() -> None` | initialize credentials if needed |
| `fetch` | `(aoi, time_range, resolution, bands) -> ProviderPayload` | retrieve arrays and vectors |
| `attribution` | `() -> str` | expose attribution text |
| `license` | `() -> str` | expose licensing text |

## 6. Output schema highlights

### 6.1 Tile prediction properties

| Property | Type | Definition |
| --- | --- | --- |
| `temperature_anomaly_c` | float | relative heat anomaly |
| `ventilation_score` | float | normalized ventilation indicator |
| `tile_id` | string | deterministic tile identifier |

### 6.2 Summary JSON

`predictions_summary.json` stores:

- AOI bounds
- tile feature vectors
- predictions
- assumptions
- provider metadata
- attribution strings
