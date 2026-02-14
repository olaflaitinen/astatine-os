# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Repository policy checks for typography and character restrictions."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

EM_DASH = "\u2014"
EMOJI_RE = re.compile(
    "["
    "\U0001f300-\U0001f5ff"
    "\U0001f600-\U0001f64f"
    "\U0001f680-\U0001f6ff"
    "\U0001f700-\U0001f77f"
    "\U0001f780-\U0001f7ff"
    "\U0001f800-\U0001f8ff"
    "\U0001f900-\U0001f9ff"
    "\U0001fa00-\U0001faff"
    "\u2600-\u26ff"
    "\u2700-\u27bf"
    "]",
    flags=re.UNICODE,
)

DEFAULT_EXCLUDES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "build",
    "dist",
    "__pycache__",
    "site",
    "out",
}


def _is_binary(path: Path) -> bool:
    try:
        sample = path.read_bytes()[:2048]
    except Exception:
        return True
    return b"\x00" in sample


def _iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in DEFAULT_EXCLUDES for part in path.parts):
            continue
        if any(part.startswith("out_") for part in path.parts):
            continue
        if _is_binary(path):
            continue
        files.append(path)
    return files


def run(root: Path) -> int:
    violations = 0
    for path in _iter_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for idx, line in enumerate(text.splitlines(), start=1):
            if EM_DASH in line:
                print(f"EM_DASH violation: {path}:{idx}")
                violations += 1
            if EMOJI_RE.search(line):
                print(f"EMOJI violation: {path}:{idx}")
                violations += 1
    if violations > 0:
        print(f"Policy check failed with {violations} violation(s).")
        return 1
    print("Policy check passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check repository typography policy.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    return run(args.root.resolve())


if __name__ == "__main__":
    sys.exit(main())
