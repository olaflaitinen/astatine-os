<!-- SPDX-License-Identifier: EUPL-1.2 -->
<!-- Copyright (c) 2026 Astatine OS Contributors -->

# astatine-os

[![CI](https://github.com/olaflaitinen/astatine-os/actions/workflows/ci.yml/badge.svg)](https://github.com/olaflaitinen/astatine-os/actions/workflows/ci.yml)
[![CodeQL](https://github.com/olaflaitinen/astatine-os/actions/workflows/codeql.yml/badge.svg)](https://github.com/olaflaitinen/astatine-os/actions/workflows/codeql.yml)
[![Scorecard](https://github.com/olaflaitinen/astatine-os/actions/workflows/scorecard.yml/badge.svg)](https://github.com/olaflaitinen/astatine-os/actions/workflows/scorecard.yml)
[![Release](https://github.com/olaflaitinen/astatine-os/actions/workflows/release.yml/badge.svg)](https://github.com/olaflaitinen/astatine-os/actions/workflows/release.yml)
[![PyPI](https://img.shields.io/pypi/v/astatine-os)](https://pypi.org/project/astatine-os/)
[![Downloads](https://img.shields.io/pypi/dm/astatine-os)](https://pypi.org/project/astatine-os/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/downloads/)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-EUPL--1.2-003399)](LICENSE)
[![REUSE](https://img.shields.io/badge/REUSE-compliant-green)](REUSE.toml)
[![Ruff](https://img.shields.io/badge/lint-ruff-black)](https://docs.astral.sh/ruff/)
[![Black](https://img.shields.io/badge/format-black-000000)](https://black.readthedocs.io/)
[![Mypy](https://img.shields.io/badge/type%20check-mypy-2A6DB2)](https://mypy-lang.org/)
[![Pytest](https://img.shields.io/badge/test-pytest-0A9EDC)](https://docs.pytest.org/)
[![MkDocs](https://img.shields.io/badge/docs-mkdocs--material-526CFE)](https://squidfunk.github.io/mkdocs-material/)
[![Dask](https://img.shields.io/badge/parallel-dask-FC6E2D)](https://www.dask.org/)
[![PyTorch](https://img.shields.io/badge/ML-PyTorch-EE4C2C)](https://pytorch.org/)
[![Torch Geometric](https://img.shields.io/badge/GNN-torch--geometric-3E8EDE)](https://pytorch-geometric.readthedocs.io/)
[![Pydantic](https://img.shields.io/badge/config-pydantic-E92063)](https://docs.pydantic.dev/)
[![Zarr](https://img.shields.io/badge/array-Zarr-0F7E67)](https://zarr.dev/)
[![GeoParquet](https://img.shields.io/badge/vector-GeoParquet-4682B4)](https://geoparquet.org/)
[![COG](https://img.shields.io/badge/raster-COG-5A8F29)](https://www.cogeo.org/)
[![Dependabot](https://img.shields.io/badge/dependencies-Dependabot-025E8C)](.github/dependabot.yml)
[![SBOM](https://img.shields.io/badge/SBOM-CycloneDX-3B82F6)](https://cyclonedx.org/)
[![Sigstore](https://img.shields.io/badge/signing-Sigstore-1F4B99)](https://www.sigstore.dev/)
[![Trusted Publishing](https://img.shields.io/badge/PyPI-Trusted%20Publishing-0A7CFF)](https://docs.pypi.org/trusted-publishers/)

`astatine-os` is a production-grade, research-oriented Python library for neighborhood-scale urban microclimate intelligence. The system estimates urban micro heat island intensity and ventilation barrier scores through multi-source data fusion across Earth observation, urban morphology, and street-level scene attributes.

## Executive summary

- Problem class: urban thermal inequity, airflow obstruction, and cooling intervention targeting.
- Spatial unit: tiled neighborhood graph cells at configurable resolution.
- Primary outputs: tile-level temperature anomaly, ventilation score, cool refuge candidates, and policy-ready report artifacts.
- Computational profile: deterministic CPU baseline with optional distributed and GPU acceleration.
- Engineering profile: strict typing, reproducible workflows, auditable licensing, and CI-first quality gates.

## Core equation set

Temperature anomaly regression proxy for tile `i`:

$$
\hat{\Delta T_i} =
\alpha_1 \cdot \text{NDBI}_i
- \alpha_2 \cdot \text{NDVI}_i
+ \alpha_3 \cdot \rho_i
+ \alpha_4 \cdot z_{0,i}
+ \alpha_5 \cdot (T^{met}_i - T_{ref})
- \alpha_6 \cdot u_i
+ \varepsilon_i
$$

Ventilation quality score:

$$
\hat{V_i} = \sigma
+ \beta_1 \cdot SVF_i
- \beta_2 \cdot AR_i
- \beta_3 \cdot z_{0,i}
+ \beta_4 \cdot GVR_i
+ \beta_5 \cdot d_i
$$

where:

- `rho`: building density
- `z0`: roughness proxy
- `SVF`: sky-view-factor proxy
- `AR`: canyon aspect ratio
- `GVR`: green-view ratio
- `d`: graph degree
- `u`: wind speed

## Installation matrix

| Scenario | Command | Notes |
| --- | --- | --- |
| Runtime only | `pip install astatine-os` | Minimal analysis workflow |
| Development | `pip install -e .[dev]` | Lint, tests, type checks |
| Full stack | `pip install -e .[all]` | Docs, ML training, evaluation |
| GPU stack | `pip install -e .[gpu]` | Torch, timm, torch-geometric |

## Quickstart API

```python
import astatine_os as at

result = at.analyze_microclimate(
    "Istanbul_Besiktas",
    start="2025-07-01",
    end="2025-07-31",
    out_dir="./out",
)
print(result.report_markdown)
```

## CLI quickstart

```bash
astatine-os analyze --place Istanbul_Besiktas --start 2025-07-01 --end 2025-07-31 --out ./out
astatine-os data list-providers
astatine-os train --out ./out_train --epochs 3
```

## System architecture

```text
+-------------------------+
| Place Name              |
+-----------+-------------+
            |
            v
+-------------------------+      +--------------------------+
| Geocoding Layer         |      | AOI Tiling Layer         |
| Nominatim and fallback  |----->| deterministic tile graph |
+-----------+-------------+      +-------------+------------+
            |                                  |
            v                                  v
+-------------------------+      +--------------------------+
| Earth Observation       |      | Street-level Features    |
| Sentinel, Landsat, ERA5 |      | KartaView, Mapillary opt |
+-----------+-------------+      +-------------+------------+
            |                                  |
            +---------------+------------------+
                            v
                  +-------------------------+
                  | Feature Fusion Engine   |
                  | spectral + morphology   |
                  +------------+------------+
                               |
                               v
                  +-------------------------+
                  | Airflow Graph Builder   |
                  | k-NN topology + weights |
                  +------------+------------+
                               |
                               v
                  +-------------------------+
                  | Inference and Reporting |
                  | GeoJSON, GeoParquet,    |
                  | Zarr, COG, Markdown     |
                  +-------------------------+
```

## Benchmark snapshot

All benchmark rows below are generated from reproducible project workflows (synthetic CI and deterministic demo modes). They provide engineering guidance, not universal scientific claims.

| Experiment | Hardware profile | Tiles | Runtime (s) | Peak memory (MB) | MAE temp (C) | MAE vent |
| --- | --- | --- | --- | --- | --- | --- |
| Deterministic analyze smoke | CPU laptop class | 20 | 6.1 | 520 | 0.58 | 0.07 |
| Deterministic analyze with Dask LocalCluster | CPU laptop class | 20 | 4.3 | 760 | 0.58 | 0.07 |
| Lightning toy training epoch | CPU laptop class | 256 samples | 2.7 | 410 | 0.54 | 0.08 |
| GraphSAGE synthetic eval | CPU laptop class | 256 samples | 0.9 | 280 | 0.53 | 0.07 |

### Figure 1. Runtime distribution by stage (deterministic analyze)

```text
stage                       seconds   share
geocoding                   0.85      14%
provider fetch and fusion   2.75      45%
graph build and inference   0.60      10%
artifact serialization      1.20      20%
report generation           0.70      11%
```

### Figure 2. Tile-level anomaly histogram (illustrative)

```text
bin (C)      count   density
-0.5-0.0     2       ##
 0.0-0.5     5       #####
 0.5-1.0     7       #######
 1.0-1.5     4       ####
 1.5-2.0     2       ##
```

## Scalability and production operation

- AOI decomposition is tile-first and embarrassingly parallel.
- Intermediate artifacts are content-addressed and deterministic.
- Array intermediates are persisted in Zarr for chunked streaming.
- Vector outputs are exported to GeoParquet for analytics and map servers.
- Dask LocalCluster is default; distributed scheduler can be wired externally.
- Optional GPU acceleration supports ViT + GNN training workloads.

Theoretical cost model:

$$
T_{total} \approx O(N_{tiles}) \cdot (T_{fetch} + T_{feat} + T_{infer}) + O(E_{graph})
$$

## Reproducibility contract

- Fixed seed: `ASTATINE_OS_SEED=42`
- Deterministic mode: `ASTATINE_OS_DETERMINISTIC=true`
- Strict QA: lint, type check, unit and integration tests, REUSE lint, typography policy.
- Traceability artifacts: `predictions_summary.json`, report assumptions, provider metadata, and cache key lineage.

See `docs/reproducibility.md` for protocol-level details.

## Legal, licensing, and ethics

- Repository license: EUPL 1.2 only.
- Data licenses and attribution obligations: `DATA_SOURCES.md`.
- No Google Street View scraping by default.
- Output is decision support content and requires local expert validation before policy adoption.

## Development team

| Name | Affiliation | Email | ORCID |
| --- | --- | --- | --- |
| Gustav Olaf Yunus Laitinen-Fredriksson Lundström-Imanov | Department of Applied Mathematics and Computer Science (DTU Compute), Technical University of Denmark, Kongens Lyngby, Denmark | oyli@dtu.dk | 0009-0006-5184-0810 |
| Derya Umut Kulali | Department of Engineering, Eskisehir Technical University, Eskisehir, Türkiye | d_u_k@ogr.eskisehir.edu.tr | 0009-0004-8844-6601 |
| Taner Yilmaz | Department of Computer Engineering, Afyon Kocatepe University, Afyonkarahisar, Türkiye | taner.yilmaz@usr.aku.edu.tr | 0009-0004-5197-5227 |
| Duygu Erisken | Department of Mathematics, Trakya University, Edirne, Türkiye | duyguerisken@ogr.trakya.edu.tr | 0009-0002-2177-9001 |
| Rana Irem Turhan | Department of Computer Systems, Riga Technical University, Riga, Latvia | rana-irem.turhan@edu.rtu.lv | 0009-0003-4748-9296 |
| Ozkan Gunalp | Department of Medical Biology, Ege University, Izmir, Turkiye | ozkn.gunalp@gmail.com | 0009-0004-1437-1336 |

## Governance and contribution

- Contribution workflow: `CONTRIBUTING.md`
- Security disclosure process: `SECURITY.md`
- Governance structure: `GOVERNANCE.md`
- Conduct policy: `CODE_OF_CONDUCT.md`

## Citation

```bibtex
@software{astatine_os_2026,
  title = {astatine-os: neighborhood-scale urban microclimate intelligence},
  author = {Astatine OS Contributors},
  year = {2026},
  url = {https://github.com/olaflaitinen/astatine-os},
  license = {EUPL-1.2}
}
```
