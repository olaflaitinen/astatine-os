<!-- SPDX-License-Identifier: EUPL-1.2 -->
<!-- Copyright (c) 2026 Astatine OS Contributors -->

# astatine-os documentation

`astatine-os` provides a full-stack geospatial pipeline for urban microclimate estimation, from AOI geocoding to policy-oriented artifacts.

## 1. Scope

Primary outputs:

- temperature anomaly GeoJSON
- ventilation score GeoJSON
- cool refuge candidate GeoJSON
- report markdown
- GeoParquet analytical export
- optional COG raster

## 2. Scientific framing

The project models local thermal stress and airflow resistance as coupled tasks on a tile graph:

$$
(\hat{\Delta T}, \hat{V}) = F(X^{eo}, X^{morph}, X^{street}, X^{met}, G)
$$

## 3. Operational pipeline

```text
place -> AOI -> tiles -> providers -> features -> graph -> inference -> artifacts
```

## 4. Baseline benchmark summary

| Workflow | Runtime (s) | Tile count | Main artifact set |
| --- | --- | --- | --- |
| Analyze deterministic | 5-8 | 20 | GeoJSON + report + parquet + zarr |
| Train toy epoch | 2-4 | 256 synthetic samples | checkpoint |
| Eval checkpoint | <1 | validation split | metric JSON |

## 5. Documentation map

- `api.md`: API signatures, parameter schema, CLI contracts.
- `methodology.md`: formulas, graph construction, ablations.
- `data_sources.md`: source catalog and licensing.
- `licensing.md`: EUPL and REUSE compliance model.
- `reproducibility.md`: deterministic protocol and experiment controls.
- `tutorials/quickstart.md`: executable end-to-end workflow.
