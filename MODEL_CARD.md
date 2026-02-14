<!-- SPDX-License-Identifier: EUPL-1.2 -->
<!-- Copyright (c) 2026 Astatine OS Contributors -->

# Model Card

## 1. Model identity

- Name: Astatine OS Microclimate Multi-Task Regressor
- Version: repository release version
- Task family: geospatial multi-task regression
- Outputs:
  - `temperature_anomaly_c`
  - `ventilation_score`

## 2. Intended use

Primary use cases:

- Neighborhood-scale thermal burden screening.
- Ventilation obstruction mapping.
- Candidate tree-planting and cooling refuge prioritization.

Not intended:

- Individual health diagnostics.
- Emergency dispatch decisions.
- Legal compliance adjudication without independent review.

## 3. Model architecture families

| Family | Purpose | Runtime profile |
| --- | --- | --- |
| Deterministic baseline | reproducible inference and CI | CPU-first |
| GraphSAGE | trainable graph regression | CPU or GPU |
| GAT | attention-based graph regression | CPU or GPU |
| Optional ViT encoder | richer EO feature encoding | GPU-recommended |

## 4. Input feature taxonomy

| Group | Representative variables | Typical role |
| --- | --- | --- |
| EO spectral | NDVI, NDBI, albedo proxy | thermal signal decomposition |
| Morphology | density, height, orientation, roughness | airflow and heat retention |
| Street scene | green-view ratio, sky-view ratio | human-scale urban texture |
| Meteorology | air temperature, wind speed | macro-to-local forcing |

## 5. Objective and loss

Joint optimization:

$$
\mathcal{L} = \lambda_T \cdot MAE(\hat{y}_T, y_T) + \lambda_V \cdot MAE(\hat{y}_V, y_V)
$$

Evaluation metrics:

- MAE
- RMSE
- Spearman rank correlation for intervention ranking stability

## 6. Training data and supervision strategy

| Supervision source | Availability | Notes |
| --- | --- | --- |
| Landsat L2 ST | partial | thermal anchor when scene coverage exists |
| ERA5-Land residual proxy | broad | weak supervision fallback |
| Synthetic CI data | always | deterministic test and pipeline validation |

## 7. Performance summary

The following values are representative engineering benchmarks for reproducible project workflows.

| Configuration | MAE temp (C) | MAE vent | Runtime profile |
| --- | --- | --- | --- |
| Deterministic baseline | 0.58 | 0.07 | lowest operational complexity |
| GraphSAGE synthetic | 0.54 | 0.08 | balanced complexity |
| GAT synthetic | 0.52 | 0.08 | highest expressiveness in toy setup |

## 8. Error and uncertainty analysis

Primary error sources:

1. Temporal mismatch across provider streams.
2. Sparse street-level imagery coverage.
3. Weak thermal supervision in data-sparse settings.

Suggested uncertainty quantification:

$$
CI_{95\%} = \bar{e} \pm 1.96 \cdot \frac{s_e}{\sqrt{n}}
$$

where `e` denotes tile-level error sample.

## 9. Fairness, bias, and representational risk

- Coverage bias may occur in under-imaged districts.
- Building proxy quality can vary across geographic regions.
- The model should be validated against locally measured station and survey data before policy deployment.

## 10. Safety and governance controls

- Deterministic mode for reproducible review.
- Structured report with explicit assumptions.
- Data attribution and licensing traceability.
- CI policy gates for lint, type, tests, REUSE, and typography constraints.

## 11. Recommended deployment validation checklist

| Check | Status expectation |
| --- | --- |
| AOI calibration against local stations | required |
| Seasonal holdout benchmark | required |
| Intervention ranking sanity review | required |
| Data license and attribution compliance | required |

## 12. Lifecycle and maintenance

- Retraining cadence: quarterly or after major provider schema changes.
- Drift monitoring: track MAE deltas and rank correlation over time.
- Rollback policy: maintain previous signed checkpoints for reproducible rollback.
