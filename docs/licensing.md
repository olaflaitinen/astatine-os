<!-- SPDX-License-Identifier: EUPL-1.2 -->
<!-- Copyright (c) 2026 Astatine OS Contributors -->

# Licensing

## 1. Repository license model

All repository code and project documentation are licensed under **EUPL 1.2 only**.

## 2. SPDX and REUSE policy

| Requirement | Rule |
| --- | --- |
| SPDX identifier value | `EUPL-1.2` |
| Copyright | mandatory in each commentable source |
| Canonical license text | `LICENSE` and `LICENSES/EUPL-1.2.txt` |
| Compliance tool | `python -m reuse lint` |

## 3. Generated artifacts and compliance

Generated folders (for example `out`, `out_*`, `site`, caches) are annotated via `REUSE.toml` to keep compliance deterministic in CI and local runs.

## 4. Third-party data legal boundaries

| Domain | Ownership | Rule |
| --- | --- | --- |
| Project source code | repository | EUPL-1.2 |
| External datasets | provider | provider-specific terms |
| Derived outputs | user responsibility | verify redistribution and attribution obligations |

## 5. Practical compliance commands

```bash
python -m reuse lint
python tools/policy_check.py
```

## 6. Distribution note

Publishing artifacts to PyPI or other registries must preserve:

1. EUPL 1.2 licensing statements.
2. SPDX headers in source.
3. Third-party data attribution references where applicable.
