<!-- SPDX-License-Identifier: EUPL-1.2 -->
<!-- Copyright (c) 2026 Astatine OS Contributors -->

# Security Policy

## 1. Supported versions

Security maintenance targets the latest active `0.x` release line.

## 2. Coordinated vulnerability disclosure

Report privately:

- Email: `security@astatine-os.org`
- Subject: `astatine-os security report`

Required report fields:

1. affected component and version
2. impact summary
3. proof-of-concept or reproduction procedure
4. suggested remediation if known

## 3. Triage service levels

| Severity band | Initial response target | Mitigation target |
| --- | --- | --- |
| Critical | 1 business day | 7 calendar days |
| High | 2 business days | 14 calendar days |
| Medium | 3 business days | 30 calendar days |
| Low | 5 business days | next regular release |

## 4. CVSS interpretation guideline

| CVSS range | Internal severity |
| --- | --- |
| 9.0 to 10.0 | Critical |
| 7.0 to 8.9 | High |
| 4.0 to 6.9 | Medium |
| 0.1 to 3.9 | Low |

## 5. Security controls in repository

- CI quality gates (`ruff`, `mypy`, `pytest`)
- CodeQL static analysis workflow
- OpenSSF Scorecard workflow
- SBOM generation (CycloneDX)
- Sigstore-based artifact signing path
- Dependabot updates for Python and GitHub Actions

## 6. Supply-chain integrity model

| Stage | Control |
| --- | --- |
| Dependency resolution | pinned metadata and reviewable updates |
| Build | reproducible workflow steps in CI |
| Artifact | SBOM and signatures |
| Release | Trusted Publishing path |

## 7. Public advisory process

After patch release:

1. publish advisory summary
2. include affected versions
3. provide upgrade guidance
4. credit reporter if permitted

## 8. Out-of-scope policy

The following are usually out of scope unless a direct exploit path is shown:

- theoretical model bias claims without exploitability
- rate-limit behavior expected by upstream public providers
- known provider outages outside project control
