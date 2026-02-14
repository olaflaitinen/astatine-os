# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Unit tests for runtime configuration."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from astatine_os.config import get_runtime_config


def test_config_validates_tile_size() -> None:
    with pytest.raises(ValidationError):
        get_runtime_config(tile_size_m=20)


def test_config_expands_paths(tmp_path: Path) -> None:
    cfg = get_runtime_config(out_dir=tmp_path / "out")
    assert cfg.out_dir.exists() is False
    assert cfg.out_dir.is_absolute()
