<!-- SPDX-License-Identifier: EUPL-1.2 -->
<!-- Copyright (c) 2026 Astatine OS Contributors -->

# Quickstart tutorial

## 1. Environment setup

```bash
python -m venv .venv
. .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -e .[all]
```

## 2. Run end-to-end analysis

```bash
astatine-os analyze --place Istanbul_Besiktas --start 2025-07-01 --end 2025-07-31 --out ./out
```

## 3. Verify generated artifacts

| Artifact | Purpose |
| --- | --- |
| `out/temperature_anomaly.geojson` | tile anomaly layer |
| `out/ventilation_score.geojson` | tile ventilation layer |
| `out/cool_refuges.geojson` | cooling refuge candidates |
| `out/predictions.geoparquet` | analytics-ready table |
| `out/intermediate_tiles.zarr` | chunked intermediate arrays |
| `out/report.md` | human-readable technical summary |

## 4. Run training and evaluation

```bash
astatine-os train --out ./out_train --epochs 1
astatine-os eval --checkpoint ./out_train/<checkpoint>.ckpt
```

## 5. Rebuild report

```bash
astatine-os report --place Istanbul_Besiktas --start 2025-07-01 --end 2025-07-31 --out ./out
```

## 6. Quality checks

```bash
python -m ruff check .
python -m mypy astatine_os tests
python -m pytest
python tools/policy_check.py
python -m reuse lint
```

## 7. Expected benchmark envelope

| Metric | Expected range |
| --- | --- |
| Analyze runtime (20 tiles) | 4 to 8 seconds |
| Memory footprint | 400 to 900 MB |
| Output tile count | deterministic for fixed AOI config |

## 8. Figure: tutorial execution sequence

```text
install -> analyze -> inspect outputs -> train -> eval -> report -> validate
```
