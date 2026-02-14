<!-- SPDX-License-Identifier: EUPL-1.2 -->
<!-- Copyright (c) 2026 Astatine OS Contributors -->

# Data Sources

This page summarizes operational and scientific characteristics of the source ecosystem. Full legal notes are in root `DATA_SOURCES.md`.

## 1. Comparative source matrix

| Source | Measurement type | Spatial resolution class | Role in model | Primary uncertainty |
| --- | --- | --- | --- | --- |
| Sentinel-2 L2A | multispectral reflectance | high | vegetation and built-up proxies | cloud and atmospheric effects |
| Landsat L2 ST | thermal surface product | medium | thermal supervision anchor | cloud and revisit sparsity |
| ERA5-Land | reanalysis meteorology | coarse | synoptic context | spatial smoothing |
| Open Buildings or OSM | building vectors | object level | canyon and roughness proxies | footprint completeness |
| KartaView or Mapillary | street imagery metadata | point-level | street-view composition | coverage heterogeneity |

## 2. Licensing and attribution quick guide

| Source | License family | Must attribute | Redistributable raw data |
| --- | --- | --- | --- |
| Sentinel | Copernicus terms | yes | provider-specific |
| Landsat | public domain | yes | generally yes |
| ERA5-Land | Copernicus C3S | yes | provider-specific |
| OpenStreetMap | ODbL | yes | governed by ODbL |
| KartaView | provider terms | yes | provider-specific |
| Mapillary | provider terms | yes | provider-specific |

## 3. Data completeness indicators (illustrative)

| Indicator | Definition | Healthy range |
| --- | --- | --- |
| `p_cloud_free` | fraction of usable EO scenes | >= 0.6 |
| `p_footprint_covered` | AOI area with building vectors | >= 0.7 |
| `p_street_scene` | tiles with street-level attributes | >= 0.4 |
| `p_meteo_available` | tiles with meteo context | >= 0.95 |

## 4. Figure: source contribution schematic

```text
EO spectral features      ########################
Morphology features       ###################
Street-level features     ##############
Meteorological context    ###########
```

## 5. Provenance documentation recommendations

For each analysis run, persist:

1. Source endpoint and timestamp.
2. Provider metadata identifiers.
3. License and attribution string.
4. Missing-data percentage per source.
5. Fallback activation flags.
