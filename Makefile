# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

.PHONY: install-dev install-all lint format typecheck test policy reuse docs demo clean

install-dev:
	python -m pip install --upgrade pip
	python -m pip install -e .[dev]

install-all:
	python -m pip install --upgrade pip
	python -m pip install -e .[all]

lint:
	ruff check .

format:
	ruff format .
	black .

typecheck:
	mypy astatine_os tests

test:
	pytest

policy:
	python tools/policy_check.py

reuse:
	python -m reuse lint

docs:
	mkdocs build --strict

demo:
	python examples/istanbul_besiktas_demo.py

clean:
	if exist .pytest_cache rmdir /s /q .pytest_cache
	if exist .ruff_cache rmdir /s /q .ruff_cache
	if exist build rmdir /s /q build
	if exist dist rmdir /s /q dist
	if exist out rmdir /s /q out
