# Verification and release gates

All metrics and thresholds in this file are proposed tests/targets. No application, live provider, or numerical benchmark was executed while authoring this pack.

## 1. Numerical correctness

| Check | Required assertion |
| --- | --- |
| Hand policy fixture | First score .128 and second score .0224 under the SIMULATION_SPEC example |
| RNG replay | Same seed/config/environment reproduces arrays, events, selections, and metrics within declared tolerance |
| Strategy ordering | Reordering strategy execution changes no trial result |
| Independent states | A finished trial cannot affect initial parameters/trust of another trial |
| Zero communication | All strategies equal local-only results; counters zero |
| All-neighbor equivalence | With nonbinding budgets and all neighbors selected, all strategies match under common aggregation |
| Full packet loss | No usable responses; attempted budget/bytes still increase; learning remains local |
| No neighbors | Random p=0 graph continues learning without communication |
| Bad fraction | `floor(N*ratio)` identities selected reproducibly; reported actual ratio correct |
| Non-finite payload | Counted as delivered if applicable, rejected as unusable, never aggregated |
| Candidate scoring | All candidates compared against the same local snapshot |
| Split isolation | Policies/AI proposal code cannot access held-out test arrays or hidden bad-node labels |
| Metrics | Independent small fixtures verify loss, accuracy, sample SD, paired differences, and units |
| Budget ledger | Exact attempt/response/byte counters; no per-round or total overflow |

Prefer property checks over broad snapshots of implementation internals. Never make “adaptive always wins” a test.

## 2. Controlled experiments

Start with the default ring, one exchange per round, 30 rounds, 12 agents, and all four strategies. Keep training data, initialization, exogenous randomness, aggregation, and communication allowances identical within each seed.

P0 scientific evaluation includes four predeclared conditions: clean network; packet loss .3 with no bad peers; sign-flip ratio .25 with packet loss .1; missing-response ratio .25 with packet loss .1. Change only the declared network condition between configurations. Record actual rounded bad-peer count. Run five fixed development seeds for diagnostics and ten separate predeclared evaluation seeds for final comparison, with each run under its work cap.

Do not tune after inspecting evaluation results and continue calling those seeds held out. If tuning is needed, record it and create a new holdout seed set. Report final validation/test macro loss and accuracy, attempted/delivered/usable communication, and seed-level paired adaptive-minus-baseline differences. Show mean and sample SD; P0 does not promise statistical significance. A single seed is a demonstration, not strong evidence of superiority.

Required ablations: epsilon=0; utility_weight=0; zero communication; all-neighbor/nonbinding budget. These test exploration, usefulness feedback, local-only behavior, and selector equivalence. Version any changed parameter and keep all other conditions matched.

P1 optional claims need their own comparisons: next-experiment recommendations versus fixed grid; policy adviser versus identical fixed profile and rule-based switcher; stress generation versus predefined scenarios. Report LLM calls, tokens, elapsed time, and available cost separately from simulated communication cost. Never compare real API dollars with simulated bytes as if they were one metric.

## 3. AI contract fixtures

Create at least 30 versioned cases under `evals/cases/`:

| Group | Cases | Required coverage |
| --- | --- | --- |
| Planner | 10 | Clear goal, vague budget, unsupported partition, impossible size, duplicate seeds, missing comparator, zero budget, contradictory constraints, out-of-scope request, prompt injection |
| Analyst | 12 | Adaptive wins, adaptive loses, tie, one seed, failed trial, missing evidence, fabricated ID, wrong sign, wrong unit, wrong snapshot, unsupported causal claim, test-data exclusion |
| Provider/lifecycle | 8 | Timeout, rate limit, refusal, malformed JSON, truncated response, absent credentials, exhausted allowance, interrupted unknown dispatch |

For deterministic mock outputs, all contract/integrity cases must pass before merge. Fixtures include invalid model outputs to prove rejection; do not count rejection as an AI reasoning success.

For a candidate live model/prompt, run a separately approved capped evaluation against frozen prompt/evidence cases and store actual outputs/usage. The ordinary three-call live smoke verifies connectivity/contracts only; it is **not** the quality benchmark. A larger quality run requires an explicit per-run allowance and isolated evaluation quota, recorded separately from ordinary user quotas. No default CI paid calls.

Proposed activation targets: ≥90% of in-scope planner cases yield a feasible plan or appropriate clarification within the allowed calls; 100% of displayed numeric/evidence claims resolve correctly; 100% of security/ownership rejection cases block prohibited action. Analyst interpretation is manually scored 0–2 each on evidence consistency, uncertainty, useful explanation, and follow-up relevance; mean target ≥6/8 with no accepted invented metric or hidden-data leak. Small benchmark sizes and model nondeterminism limit generalization; publish numerator/denominator, not just a rounded percentage.

Regression gate: a prompt/model change cannot introduce a critical failure or unexplained drop below the activation targets. Store versioned reports, don't replace failures with cherry-picked successful runs.

## 4. Security and lifecycle matrix

Test every relevant route as unauthenticated, user A aal1, user A aal2, and user B aal2. Include list/detail/mutate/cancel/retry/export/AI-plan-context/analysis/evidence/delete. Verify forged owner fields, foreign child IDs, mixed-owner composite references, and cursor manipulations fail.

Database tests run under actual non-owner runtime roles, not only migration-owner/service-role credentials. Test missing actor denies access, transaction-local actor resets with pooled reuse, direct client table grants are denied, views/functions do not reopen access, and worker writes require the current job token.

Execution tests: identical duplicate create; same key/different payload; two-worker claim; lease expiry; stale commit; API restart; worker crash mid-trial; cancellation during a round; cancel-vs-finalize; quota race; deletion while active; tombstone-vs-late-write; ambiguous AI dispatch. Confirm completed trials are not recomputed during interrupted-trial recovery, and provisional rows never enter final statistics.

## 5. End-to-end demo script

1. Create user A; sign in; enroll/verify MFA.
2. Ask the planner for a corruption/budget comparison using a real provider; show disclosed model identity and approved assumptions.
3. Review one-exchange-per-round ring plan and approve exact revision.
4. Submit once, refresh UI, and confirm one run exists.
5. Watch completed trials populate measured charts; inspect a seed and trace node.
6. Generate analysis; open a finding's source evidence; show limitations and a follow-up draft.
7. Sign out/in with MFA and recover the same run/export.
8. Sign in as user B and show that user A's direct result/export URLs return 404.
9. Demonstrate AI unavailable behavior and cancellation using separate small runs.

If a step is omitted, label it unverified. Screenshots of charts are not proof that rows persisted or access controls worked.

## 6. CI and release evidence

On pull requests: dependency-lock consistency; lint/type checks; unit/numerical tests; mock AI evals; local database migrations/security tests; API tests; OpenAPI diff. Run the main mock E2E journey at the release gate. Keep network/live tests opt-in. Pin CI dependencies and review permission scopes; do not run untrusted PR code with provider or deployment secrets.

Release report must include commit/environment, feature status, exact check commands/results, numerical/AI versions, benchmark scenario/hardware/time, known omissions, live-call verification versus mock verification, and AI usage disclosure. A human reviews scientific interpretation, auth/data access, and migrations before a production release.
