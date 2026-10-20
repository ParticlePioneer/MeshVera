# Implementation backlog

All rows are initially **planned**. This pack provides specifications only; no application feature or test has been executed by creating these documents.

Status vocabulary: planned / in progress / implemented / verified / blocked. “Implemented” is not “verified.” Add commit ID, check commands, and evidence path when advancing status.

| Order | Feature | Dependencies | Status | Evidence |
| --- | --- | --- | --- | --- |
| 1 | F00 Foundation | — | planned | — |
| 2 | F01 Identity, MFA, isolation | F00 | planned | — |
| 3 | F02 Configuration and approval | F00, F01 | planned | — |
| 4 | F03 Data, learner, metrics | F00, F02 | planned | — |
| 5 | F04 Network and transmission ledger | F03 | planned | — |
| 6 | F05 Baselines | F04 | planned | — |
| 7 | F06 Adaptive selection | F05 | planned | — |
| 8 | F07 Durable execution | F01–F06 | planned | — |
| 9 | F08 Results and evidence | F07 | planned | — |
| 10 | F11 History/export core | F07, F08 | planned | — |
| 11 | F09 AI planner | F02, F05, F06 | planned | — |
| 12 | F10 AI analyst | F08, F09 | planned | — |
| 13 | F11 AI provenance/deletion completion | F09, F10 | planned | — |
| 14 | F12 Release gates | F00–F11 | planned | — |
| Later | F13 Next-experiment loop | F10–F12 | planned P1 | — |
| Later | F14 Stress scenarios | F13 | planned P1 | — |
| Later | F15 Policy adviser | F12 + policy ADR | planned P1 | — |
| Later | F16 Reports/anomalies | F10, F12 | planned P1 | — |

## Milestone gates

- [ ] M0: repository inspected; scope conflicts resolved; auth/MFA and draft isolation verified.
- [ ] M1: tiny numerical fixtures, all baseline policies, accounting, and reproducibility pass.
- [ ] M2: user submits run, polls, retrieves results after new login, exports, and cancels safely.
- [ ] M3: genuine live planning and grounded analysis demonstrated; AI failure fallback verified.
- [ ] M4: evaluation report, clean setup, role/worker tests, limits, and disclosure completed.

## Current next action

Start F00 by inspecting the actual repository. List existing files/stack/tests and material conflicts; do not scaffold over an existing application. Implement only the minimum coherent F00 slice first. Then update this file with exact evidence and choose the next ready feature.
