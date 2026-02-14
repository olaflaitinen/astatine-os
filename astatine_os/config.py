# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Configuration models and environment helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_CACHE_DIR = Path.home() / ".cache" / "astatine_os"


class RuntimeConfig(BaseSettings):
    """Runtime configuration for analysis and training."""

    model_config = SettingsConfigDict(
        env_prefix="ASTATINE_OS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    cache_dir: Path = Field(default=DEFAULT_CACHE_DIR)
    out_dir: Path = Field(default=Path("./out"))
    seed: int = Field(default=42, ge=0)
    deterministic: bool = Field(default=True)
    tile_size_m: int = Field(default=300, ge=50, le=2000)
    resolution_m: int = Field(default=10, ge=1, le=250)
    dask_workers: int = Field(default=2, ge=1, le=64)
    dask_threads_per_worker: int = Field(default=1, ge=1, le=8)
    use_dask_distributed: bool = Field(default=True)
    geocoder_user_agent: str = Field(default="astatine-os/0.1.0")
    era5_cds_url: str = Field(default="https://cds.climate.copernicus.eu/api")
    era5_cds_key: str | None = Field(default=None)
    mapillary_access_token: str | None = Field(default=None)
    enable_optional_live_calls: bool = Field(default=False)

    @field_validator("cache_dir", "out_dir")
    @classmethod
    def _expand_path(cls, value: Path) -> Path:
        return value.expanduser().resolve()


def get_runtime_config(**overrides: Any) -> RuntimeConfig:
    """Build runtime config from environment variables and direct overrides."""
    return RuntimeConfig.model_validate(overrides)
