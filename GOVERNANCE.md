<!-- SPDX-License-Identifier: EUPL-1.2 -->
<!-- Copyright (c) 2026 Astatine OS Contributors -->

# Governance

## 1. Governance model

`astatine-os` follows a maintainer-led, transparent governance model optimized for technical rigor and release discipline.

## 2. Roles

| Role | Primary responsibility |
| --- | --- |
| Maintainer | architecture stewardship, merge rights, release approval |
| Reviewer | technical review, QA verification, documentation review |
| Contributor | implementation and proposal submission |
| Security contact | vulnerability coordination and disclosure management |

## 3. Current development team

| Name | Institutional affiliation | Governance assignment |
| --- | --- | --- |
| Gustav Olaf Yunus Laitinen-Fredriksson Lundström-Imanov | Department of Applied Mathematics and Computer Science (DTU Compute), Technical University of Denmark | Maintainer |
| Derya Umut Kulali | Department of Engineering, Eskisehir Technical University | Reviewer |
| Taner Yilmaz | Department of Computer Engineering, Afyon Kocatepe University | Reviewer |
| Duygu Erisken | Department of Mathematics, Trakya University | Contributor |
| Rana Irem Turhan | Department of Computer Systems, Riga Technical University | Contributor |
| Ozkan Gunalp | Department of Medical Biology, Ege University | Security contact |

## 4. Decision policy

1. Seek consensus for substantive technical changes.
2. If consensus is not reached, majority maintainer vote decides.
3. Security matters may use expedited maintainer decision.

## 5. RACI matrix

| Activity | Maintainer | Reviewer | Contributor | Security contact |
| --- | --- | --- | --- | --- |
| API change approval | A | R | C | I |
| Model architecture changes | A | R | C | I |
| Release publication | A | C | I | C |
| Vulnerability response | C | I | I | A |
| Documentation quality | A | R | C | I |

Legend:

- `A`: accountable
- `R`: responsible
- `C`: consulted
- `I`: informed

## 6. Release governance

| Stage | Governance gate |
| --- | --- |
| pre-release | CI green and compliance gates pass |
| release candidate | maintainer sign-off |
| publication | signed artifacts and release notes |
| post-release | issue triage and regression monitoring |

## 7. Conflict resolution

When disagreement persists:

1. open a design issue with explicit alternatives
2. collect written arguments and evidence
3. resolve with maintainer vote and archived rationale

## 8. Amendment process

Governance policy updates require:

- issue proposal
- maintainer review
- explicit merge approval by maintainer quorum
