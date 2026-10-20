# MeshVera — Project development playbook

This is a repository-local playbook explicitly loaded by the coding agent, not an installed ChatGPT skill. Read `AGENTS.md` first. Tool-native skill registration, if wanted later, is a separate integration task: verify that tool's current discovery format and keep one authoritative copy of each workflow.

## Workflow selection

| Change | Workflow |
| --- | --- |
| New feature or route | A — Vertical feature |
| Learning, topology, budget, policy, metrics | B — Scientific implementation |
| Prompt, provider, plan, analysis | C — AI feature |
| Auth, DB, jobs, ownership, deletion | D — Persistence and execution |
| Final delivery or pause | E — Review and handoff |

## A — Vertical feature

Inputs: Fxx ticket, dependencies, current code and contracts.

1. Check dependency status and existing repository instructions. Do not infer implementation from a checked box without its evidence.
2. Copy `docs/templates/FEATURE_TASK.md` into `docs/features/Fxx.md`; fill the contract, boundaries, failure cases, and test plan.
3. Implement validation/domain logic first, then persistence/API, then UI. Preserve one shared schema.
4. Cover success, invalid input, unauthorized access, and the primary domain failure with meaningful tests.
5. Run relevant checks; inspect the diff; update OpenAPI/docs/status and handoff.

Done: a user-visible slice meets the ticket's acceptance criteria, with real verification evidence.

## B — Scientific implementation

Inputs: SIMULATION_SPEC version, deterministic fixture, expected arithmetic.

1. Trace train/validation/test data flow. Confirm no held-out leakage.
2. Implement a pure function/interface with explicitly passed RNG/state.
3. Check a tiny hand-computed example before scaling. Test budget conservation, finite outputs, and boundary cases.
4. Compare strategies on identical conditions and RNG namespaces. Change evaluation order to detect accidental RNG/state coupling.
5. Separate numerical correctness from performance superiority. Keep negative/inconclusive results.
6. If semantics change, create an ADR, bump algorithm/scenario version, regenerate affected fixture evidence, and report the change.

Done: exact policy/accounting behavior is verified; no unsupported research claim is introduced.

## C — AI feature

Inputs: AI_SPEC task schema, prompt version, provider contract, eval cases.

1. Verify current official SDK request/output and refusal/timeout behavior for the selected model.
2. Implement deterministic mock success and failures before connecting live API.
3. Delimit untrusted text; pass only authorized bounded evidence; never expose secrets or broad tool access.
4. Validate schema, domain bounds, evidence scope/hash/IDs, and numeric relation checks.
5. Reserve budgets before dispatch; keep retries/repairs inside the same limit.
6. Run frozen fixtures, then explicit opt-in live smoke when authorized. Log model/prompt/schema versions and actual usage.
7. Check that manual simulation/results still work when AI fails.

Done: the feature creates demonstrable assistance with validated provenance; mocks are not reported as live results.

## D — Persistence and execution

Inputs: DATA_API contract, migration, API actor path, worker lifecycle.

1. Use explicit roles, grants, RLS, foreign keys, ownership constraints, and indexes.
2. Test user A/user B/unauthenticated/aal1 access for relevant routes; test pooled actor reset and direct-table denial.
3. Keep submission + idempotency + quota + job creation atomic.
4. Claim under lease; fence every result commit; check terminal/cancel/tombstone state in the same write transaction.
5. Simulate duplicate submissions, two-worker race, crash, stale worker, cancel-versus-complete, and active deletion where applicable.
6. Separate numerical restart from ambiguous live-provider retry; document billing uncertainty.

Done: database and API invariants survive tested failures, not only a happy-path demo.

## E — Review and handoff

1. Review against the Fxx acceptance list and relevant invariants.
2. Run the smallest checks that establish the change; run required release gates at milestones.
3. Inspect for secrets, duplicated instructions, invented results, stale contracts, broken links, and unrelated changes.
4. Record actual commands/output summary in `docs/features/Fxx.md` and TASKS.
5. State what is verified, what remains blocked/untested, and the next task. Never mark deferred P1 scope as completed P0.

Done: another coding agent can resume from the repository without relying on an unseen chat transcript.
