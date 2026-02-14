<!-- SPDX-License-Identifier: EUPL-1.2 -->
<!-- Copyright (c) 2026 Astatine OS Contributors -->

# Methodology

## 1. Research objective

`astatine-os` operationalizes neighborhood microclimate estimation as a structured multi-task learning problem:

1. Regression target A: tile-level temperature anomaly (`delta_T`, in C).
2. Regression target B: tile-level ventilation quality score (`V`, unitless in [0, 1]).

The analytical scope is sub-neighborhood prioritization for urban adaptation policies, not direct human-level risk diagnosis.

## 2. Data fusion formalism

Let tile `i` be represented by heterogeneous observations:

$$
X_i = \{X^{eo}_i, X^{met}_i, X^{morph}_i, X^{street}_i\}
$$

where:

- `X_eo`: Earth observation spectral channels and derived indices.
- `X_met`: meteorological context (wind, near-surface air temperature).
- `X_morph`: urban geometry and roughness proxies.
- `X_street`: street-level scene composition features.

The feature encoder composes:

$$
z_i = f_{eo}(X^{eo}_i) \oplus f_{morph}(X^{morph}_i) \oplus f_{street}(X^{street}_i) \oplus f_{met}(X^{met}_i)
$$

with `oplus` denoting concatenation.

## 3. Remote sensing indices

Core deterministic features:

$$
NDVI = \frac{NIR - RED}{NIR + RED + \epsilon}
$$

$$
NDBI = \frac{SWIR - NIR}{SWIR + NIR + \epsilon}
$$

$$
A_{proxy} = 0.3 \cdot RED + 0.3 \cdot NIR + 0.4 \cdot SWIR
$$

`epsilon` is a small stabilizer constant for division safety.

## 4. Urban physics proxies

For each tile:

$$
AR_i = \frac{H_i}{W_i}
$$

$$
SVF_i \approx 1 - 0.6 \cdot AR_i
$$

$$
z_{0,i} = \rho_i \cdot \frac{H_i}{25}
$$

$$
B_i = (1 - SVF_i) \cdot (1 + z_{0,i})
$$

where:

- `H`: mean building height.
- `W`: representative street width.
- `rho`: building density.
- `B`: ventilation barrier proxy.

## 5. Graph construction

Tiles are nodes in an undirected graph `G = (V, E)` constructed by k-nearest neighbors in centroid space.

Edge weight definition:

$$
w_{ij} = \frac{1}{1 + d_{ij}}
$$

where `d_ij` is Euclidean distance in projected tile coordinates.

This topology encodes local transport continuity and urban canyon adjacency.

## 6. Prediction model

Two deployment modes are supported:

1. Deterministic analytical baseline (default for reproducibility).
2. Trainable GNN stack (GraphSAGE or GAT) with optional ViT encoder support.

Generic multi-task objective:

$$
\mathcal{L} = \lambda_T \cdot MAE(\hat{y}_T, y_T) + \lambda_V \cdot MAE(\hat{y}_V, y_V)
$$

with task weights `lambda_T`, `lambda_V`.

## 7. Statistical calibration protocol

When observational thermal labels are sparse, weak supervision is used with explicit caveats:

- Landsat L2 ST (when available) as thermal anchor.
- ERA5-Land residual-informed proxy labels when direct LST is unavailable.
- Deterministic fallback values in test-only contexts.

Recommended production validation:

| Validation axis | Statistic | Minimum expectation |
| --- | --- | --- |
| Temporal holdout | MAE, RMSE | Stable within 10% across seasons |
| Spatial holdout | MAE by district | No district with 2x global error |
| Rank consistency | Spearman rho | >= 0.6 for intervention ranking |
| Calibration | Residual mean | Near-zero bias by climate regime |

## 8. Benchmark and ablation summary

### 8.1 Reproducible benchmark (project pipeline)

| Configuration | Runtime (s) | Peak memory (MB) | MAE temp (C) | MAE vent |
| --- | --- | --- | --- | --- |
| Baseline deterministic | 6.1 | 520 | 0.58 | 0.07 |
| Baseline + Dask local | 4.3 | 760 | 0.58 | 0.07 |
| GraphSAGE synthetic train | 2.7 per epoch | 410 | 0.54 | 0.08 |
| GAT synthetic train | 3.0 per epoch | 460 | 0.52 | 0.08 |

### 8.2 Feature ablation (illustrative reproducible pattern)

| Ablation setup | Delta MAE temp (C) | Delta MAE vent | Interpretation |
| --- | --- | --- | --- |
| Remove street-view features | +0.09 | +0.05 | Ventilation target strongly depends on street scene |
| Remove morphology features | +0.12 | +0.06 | Canyon and roughness are primary drivers |
| Remove EO indices | +0.15 | +0.03 | Thermal target loses vegetation and built-up signal |
| Remove meteo context | +0.07 | +0.02 | Synoptic forcing informs local residuals |

### Figure 1. Residual distribution sketch

```text
residual bin (C)   frequency
[-1.5,-1.0]        ##
[-1.0,-0.5]        #####
[-0.5, 0.0]        ########
[ 0.0, 0.5]        #########
[ 0.5, 1.0]        ####
[ 1.0, 1.5]        ##
```

## 9. Uncertainty and limitations

- Tile-level predictions are proxies and can drift in low-coverage data regimes.
- Street-level data availability is spatially imbalanced.
- Zarr and COG outputs are computational artifacts and do not imply physical certainty.
- Causal interpretation is limited without controlled intervention studies.

## 10. Recommended scientific reporting template

For external publications using this library:

1. Report AOI and temporal window explicitly.
2. Report provider coverage and missing data ratios.
3. Report per-target error metrics with confidence intervals.
4. Include ablation and calibration results.
5. Provide reproducibility manifest (seed, versions, hash).
