<!-- SPDX-License-Identifier: EUPL-1.2 -->
<!-- Copyright (c) 2026 Astatine OS Contributors -->

# Contributing

## 1. Contribution principles

The project targets scientific credibility and production reliability. Each change should improve at least one of:

- methodological correctness
- reproducibility
- runtime scalability
- software quality

## 2. Development environment

```bash
python -m venv .venv
. .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -e .[all]
pre-commit install
```

## 3. Mandatory local quality gates

```bash
python -m ruff check .
python -m mypy astatine_os tests
python -m pytest
python tools/policy_check.py
python -m reuse lint
```

## 4. Pull request acceptance matrix

| Criterion | Requirement |
| --- | --- |
| Functional correctness | tests must pass |
| Style and type integrity | lint and mypy must pass |
| License compliance | REUSE must pass |
| Typography policy | no emoji and no U+2014 |
| Documentation | user-facing changes documented |

## 5. Scientific change requirements

For model or methodology changes include:

1. motivation statement
2. expected metric impact
3. benchmark comparison table
4. risk and limitation discussion

Recommended metric delta table:

| Metric | baseline | proposed | delta |
| --- | --- | --- | --- |
| MAE temp (C) | x | y | y-x |
| MAE vent | x | y | y-x |
| Runtime (s) | x | y | y-x |

## 6. Code style conventions

- Follow Google Python style where compatible with automation.
- Keep public APIs typed and documented.
- Prefer deterministic defaults for tests and demos.
- Keep provider connectors modular and auditable.

## 7. Provider contribution checklist

| Item | Required |
| --- | --- |
| Implements provider contract methods | yes |
| Documents license and attribution | yes |
| Includes deterministic fallback behavior | yes |
| Includes unit tests with mocks | yes |
| Updates data source docs | yes |

## 8. Commit and branch guidance

- Branch naming: `feature/<topic>` or `fix/<topic>`.
- Commit messages: imperative and scoped.
- Keep PR scope focused and reviewable.

## 9. License policy

Every commentable file must include:

- SPDX identifier value: `EUPL-1.2`
- copyright notice

No alternate license text is allowed in repository source.
