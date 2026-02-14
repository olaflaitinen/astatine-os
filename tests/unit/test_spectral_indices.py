# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Unit tests for spectral indices."""

from __future__ import annotations

import numpy as np

from astatine_os.features.spectral_indices import compute_albedo_proxy, compute_ndbi, compute_ndvi


def test_ndvi_shape_and_range() -> None:
    nir = np.array([[0.6, 0.8], [0.3, 0.2]], dtype="float32")
    red = np.array([[0.2, 0.3], [0.2, 0.2]], dtype="float32")
    ndvi = compute_ndvi(nir, red)
    assert ndvi.shape == (2, 2)
    assert float(ndvi.max()) <= 1.0
    assert float(ndvi.min()) >= -1.0


def test_ndbi_is_positive_for_high_swir() -> None:
    swir = np.array([[0.7]], dtype="float32")
    nir = np.array([[0.3]], dtype="float32")
    ndbi = compute_ndbi(swir, nir)
    assert float(ndbi[0, 0]) > 0.0


def test_albedo_proxy_is_bounded() -> None:
    red = np.array([[0.2]], dtype="float32")
    nir = np.array([[0.5]], dtype="float32")
    swir = np.array([[0.7]], dtype="float32")
    alb = compute_albedo_proxy(red, nir, swir)
    assert 0.0 <= float(alb[0, 0]) <= 1.0
