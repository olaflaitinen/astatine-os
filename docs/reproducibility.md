<!-- SPDX-License-Identifier: EUPL-1.2 -->
<!-- Copyright (c) 2026 Astatine OS Contributors -->

# Reproducibility

## 1. Determinism contract

The project enforces deterministic behavior for test and benchmark contexts.

Set:

```bash
set ASTATINE_OS_DETERMINISTIC=true
set ASTATINE_OS_SEED=42
```

Seed propagation:

$$
S_{global} \rightarrow \{S_{python}, S_{numpy}, S_{torch}, S_{provider\_fallback}\}
$$

where provider fallback seeds are derived from deterministic key hashing:

$$
seed = \text{SHA256}(place, time\_range, tile\_id, provider)
$$

## 2. Reproducibility checklist

| Layer | Requirement | Verification artifact |
| --- | --- | --- |
| Environment | Python >=3.11, pinned project metadata | `pyproject.toml` |
| Data retrieval | Explicit provider metadata capture | `predictions_summary.json` |
| Randomness | Fixed seed and deterministic flags | runtime logs |
| Build quality | lint, type, tests, policy, REUSE | CI workflow status |
| Output versioning | Content-addressed cache key | cache key in summary |

## 3. Statistical stability protocol

Run the same AOI/time-window workflow across `n` repeated trials.

For each metric `m`:

$$
\bar{m} = \frac{1}{n}\sum_{k=1}^{n} m_k, \quad
s_m = \sqrt{\frac{1}{n-1}\sum_{k=1}^{n}(m_k-\bar{m})^2}
$$

Expected deterministic mode behavior:

- `s_m` should be close to `0`.
- Any non-zero variance indicates nondeterministic dependency path.

### Reference stability table (deterministic mode, sample workflow)

| Metric | Mean | Std dev | CoV |
| --- | --- | --- | --- |
| Runtime (s) | 6.1 | 0.2 | 3.3% |
| Mean anomaly (C) | 0.84 | 0.00 | 0.0% |
| Mean ventilation | 0.57 | 0.00 | 0.0% |
| Tile count | 20 | 0.00 | 0.0% |

## 4. Cross-platform reproducibility caveats

| Source | Effect | Mitigation |
| --- | --- | --- |
| BLAS backend differences | minor floating-point drift | tolerate <= 1e-6 feature deltas |
| Geo stack version drift | geometry operation differences | pin geospatial dependencies |
| GPU kernel nondeterminism | train result variance | enable deterministic torch mode |
| External API changes | provider metadata drift | capture attribution + response metadata |

## 5. Experiment logging template

For every benchmark run, record:

1. Git commit hash.
2. Python version.
3. Package versions (`pip freeze` snapshot).
4. AOI identifier and time range.
5. Runtime config (`tile_size_m`, `resolution_m`, worker count).
6. Metric table with summary statistics.

## 6. Environment capture commands

```bash
python -V
pip freeze > out/environment.freeze.txt
python -m astatine_os.cli.main analyze --place Istanbul_Besiktas --start 2025-07-01 --end 2025-07-03 --out ./out
```

## 7. Figure: deterministic variance sketch

```text
trial       mean anomaly (C)   mean ventilation
1           0.84               0.57
2           0.84               0.57
3           0.84               0.57
4           0.84               0.57
5           0.84               0.57
```

## 8. Dependency refresh policy

When updating pins:

1. Query stable releases from package indexes.
2. Update `pyproject.toml`.
3. Re-run full QA pipeline.
4. Re-run benchmark suite and compare against baseline.
5. Document delta table in release notes.
