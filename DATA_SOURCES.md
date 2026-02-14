<!-- SPDX-License-Identifier: EUPL-1.2 -->
<!-- Copyright (c) 2026 Astatine OS Contributors -->

# Data Sources

This document defines the external data catalog used by `astatine-os`, including access modality, licensing constraints, attribution obligations, and operational risk notes.

## 1. Source catalog

| Source | Connector | Typical spatial scale | Temporal cadence | License and terms | Attribution |
| --- | --- | --- | --- | --- | --- |
| Sentinel-2 L2A | STAC query | 10 m (selected bands) | revisit-driven | Copernicus Sentinel terms | Copernicus Programme |
| Landsat C2 L2 | STAC query | 30 m | revisit-driven | USGS public domain terms | USGS and NASA Landsat |
| ERA5-Land | CDS API | coarse meteorological grid | hourly aggregates | Copernicus C3S license | Copernicus C3S |
| Open Buildings | provider connector | building footprint scale | dataset release cadence | provider-specific terms | Google Open Buildings |
| OpenStreetMap | OSMnx fallback | object-level vector | community-updated | ODbL 1.0 | OpenStreetMap contributors |
| KartaView | provider connector | street imagery points | community-updated | provider-specific terms | KartaView |
| Mapillary (optional) | token-auth API | street imagery points | provider-updated | provider-specific terms | Mapillary |

## 2. Access and authentication matrix

| Source | Authentication | Required in demo | Fallback behavior |
| --- | --- | --- | --- |
| Sentinel-2 | no | no | deterministic synthetic EO arrays |
| Landsat | no | no | deterministic thermal proxy |
| ERA5-Land | optional user credential | no | deterministic meteo fallback |
| Open Buildings | no | no | deterministic footprint synthesis |
| OSM | no | no | Open Buildings fallback |
| KartaView | no | no | deterministic scene ratios |
| Mapillary | optional user token | no | deterministic scene ratios |

## 3. Licensing and redistribution notes

1. Repository code and markdown are EUPL-1.2 only.
2. External data remains under each provider's legal regime.
3. Generated derivatives may inherit attribution requirements.
4. Users must validate redistribution rights before publishing derived outputs.

## 4. Data quality dimensions

| Dimension | Sentinel/Landsat | ERA5-Land | Buildings | Street-level |
| --- | --- | --- | --- | --- |
| Coverage completeness | moderate to high | high | medium | variable |
| Temporal freshness | revisit-dependent | high | release-dependent | variable |
| Label directness | medium | low | medium | medium |
| Urban canyon relevance | high | medium | high | high |

## 5. Risk register

| Risk | Probability | Impact | Mitigation |
| --- | --- | --- | --- |
| Missing clear-sky thermal scenes | medium | medium | weak supervision fallback + uncertainty note |
| Provider endpoint changes | medium | high | modular provider abstraction and tests |
| Sparse street-level imagery | high in some regions | medium | deterministic fallback + confidence flags |
| Licensing misinterpretation | low to medium | high | explicit attribution and legal checklist |

## 6. Attribution template for downstream reports

Suggested citation text block:

```text
This analysis integrates Copernicus Sentinel data, Landsat public-domain products,
Copernicus ERA5-Land meteorology, and open community mapping or street-level data
where available. Provider-specific terms and attribution obligations apply.
```

## 7. Demo data policy

- The demo workflow can execute without secrets.
- Public metadata downloads are limited to lightweight catalog objects.
- Deterministic fallback paths are included to ensure reproducible CI execution.
