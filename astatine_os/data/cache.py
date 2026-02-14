# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Content-addressed local cache utilities."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import orjson


class CacheStore:
    """Filesystem cache with SHA256 content keys."""

    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def _key_to_path(self, key: str, suffix: str) -> Path:
        prefix = key[:2]
        folder = self.root_dir / prefix
        folder.mkdir(parents=True, exist_ok=True)
        return folder / f"{key}{suffix}"

    @staticmethod
    def make_key(payload: dict[str, Any]) -> str:
        """Create deterministic key from a JSON-serializable payload."""
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def save_json(self, key: str, payload: dict[str, Any]) -> Path:
        """Persist JSON payload under key."""
        path = self._key_to_path(key, ".json")
        path.write_bytes(orjson.dumps(payload, option=orjson.OPT_INDENT_2))
        return path

    def load_json(self, key: str) -> dict[str, Any] | None:
        """Load JSON payload by key if available."""
        path = self._key_to_path(key, ".json")
        if not path.exists():
            return None
        return orjson.loads(path.read_bytes())
