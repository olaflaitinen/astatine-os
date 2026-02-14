# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Spectral index computations."""

from __future__ import annotations

import numpy as np


def _safe_ratio(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray:
    denom = np.where(np.abs(denominator) < 1e-6, 1e-6, denominator)
    return numerator / denom


def compute_ndvi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
    """Normalized Difference Vegetation Index."""
    return _safe_ratio(nir - red, nir + red)


def compute_ndbi(swir: np.ndarray, nir: np.ndarray) -> np.ndarray:
    """Normalized Difference Built-up Index."""
    return _safe_ratio(swir - nir, swir + nir)


def compute_albedo_proxy(red: np.ndarray, nir: np.ndarray, swir: np.ndarray) -> np.ndarray:
    """Simple broad-band albedo proxy."""
    return np.clip(0.3 * red + 0.3 * nir + 0.4 * swir, 0.0, 1.0)
