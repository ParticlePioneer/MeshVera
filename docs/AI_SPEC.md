# AI product contracts and development rules

## 1. What makes AI core

The distinctive workflow is **design → measured experiment → grounded explanation → proposed next experiment**. Removing the LLM should remove useful research assistance, while leaving the numerical engine correct and usable. Do not add multiple model calls simply to increase the apparent use of AI.

| Idea | Concrete value | Inputs → outputs | Evaluation / priority |
| --- | --- | --- | --- |
| Experiment designer | Turns a question into a fair, falsifiable comparison | Research goal + allowed schema → hypothesis, controls, baselines, config, assumptions | Feasibility, baseline coverage, human usefulness; P0 |
| Evidence-based analyst | Helps users interpret curves and failures | Authorized validation summaries → cited findings, uncertainty, hypotheses | Claim grounding, direction accuracy, abstention; P0 |
| Next-experiment adviser | Reduces aimless trial-and-error | Prior validation evidence + remaining experiment budget → small approved test plan | Compare with fixed grid/rule recommendations; P1 first |
| Stress-scenario designer | Explores failure modes beyond manual presets | Goal + event DSL → bounded timed scenario | Validity, coverage, redundancy, replay; P1 |
| Bounded local policy adviser | Tests whether contextual advice helps selection | One node's local summaries → allowlisted parameter profile | Against fixed and rule-based profiles, including AI overhead; experimental P1 |
| Research report / anomaly explanation | Turns completed experiments into a reviewable account | Evidence bundle + deterministic event flags → report with hypotheses | Citation coverage, number fidelity, limitation disclosure; P1 |

Defer generic chatbot, multi-model voting, embeddings/vector databases, unrestricted agents, and “AI detects malicious agents” claims. They do not solve a current P0 requirement. Low usefulness may reflect non-IID data or delivery loss, not malicious intent.

## 2. Provider boundary

One interface: `generate(task_kind, system_template, input_payload, output_schema, budget, cancel_signal) → ProviderResult`. Result contains structured output or normalized error, provider/model ID, latency, usage, finish reason, and request ID where available. Provider/model IDs are server-configured and verified at implementation; do not invent a model name in the PRD.

Use structured outputs where supported, followed by independent Pydantic and semantic validation. Schema conformance does not establish truth. Distinguish refusal, truncation, invalid JSON/schema, timeout, transient provider error, and unavailable credentials. Never parse executable Python or let the model choose an endpoint or system policy.

Each user-triggered AI operation permits at most two provider dispatches total: one initial attempt plus either one classified transient retry or one schema/semantic repair. Output ceiling per call 2,000 tokens, input ceiling 12,000 tokens, response bytes 24 KiB, per-call timeout 20 seconds, operation deadline 45 seconds. These are initial settings to benchmark, not latency guarantees. Reserve maxima before dispatch. Maintain one active AI operation per user and a default quota of 20 dispatches per user per day. Provider cost is null when unavailable; estimated cost must identify price-table version. No guessed zero cost.

AI operations are jobs separate from simulations. Persist requested/started/completed times, mode, schema/prompt versions, input hash, output, validation outcome, usage, safe error, evidence snapshot hash, and approval lineage. Default logs exclude prompt/output text. Saved user-owned AI output is deletable with its experiment; raw provider request debugging is opt-in and redacted.

An ambiguous interrupted live call is marked `interrupted_unknown` without automatic redispatch. The user can start a new operation after seeing that the original might have incurred cost. This is distinct from restarting deterministic numerical work. Exactly-once external inference is not promised.

## 3. Planner contract — PlanProposalV1

Strict fields:

| Field | Contract |
| --- | --- |
| `schema_version` | `plan.v1` |
| `status` | `proposed` / `needs_clarification` / `unsupported` |
| `research_question` | ≤500 characters |
| `hypothesis` | ≤1,000 characters; testable, not a claimed outcome |
| `config` | Complete ExperimentConfigV1 when proposed, null otherwise |
| `comparison` | Primary metric enum (validation loss/accuracy or attempted logical bytes), strategy IDs, direction, controlled-field list |
| `assumptions` | ≤8 explicit assumptions, each ≤300 characters |
| `questions` | ≤3 clarifications; empty for a fully proposed plan |
| `rationale_summary` | ≤1,000 characters; concise public explanation |
| `limitations` | ≤5 strings, ≤300 characters each |

Validation rejects unknown strategies, missing baseline, excessive work, mismatched comparison fields, unsupported events, and hidden settings. Approval UI renders all assumptions. The server, not the LLM, calculates work estimates, actual bad-node fraction, approval hash, and remaining budget.

Planner v1 schema is for one comparative experiment. Multiple configurations/scenarios are P1. A user request requiring unsupported dynamic partitions returns `unsupported` with an honest explanation rather than pretending a static config tests a partition.

Illustrative goal: “Under a strict message budget, does trust-aware selection help with corrupted peers?” Proposed comparison includes adaptive plus fixed/random/reliability under identical seeds; it states a hypothesis rather than predicting measured accuracy. “Strict” maps to a visible assumption, e.g. one attempted exchange per node per round.

## 4. Evidence registry

Create evidence deterministically after numerical trials finish. Each immutable item has:

`id, run_id, snapshot_hash, metric_key, split, strategy_ids, seed_ids, round_start, round_end, aggregation, value, unit, sample_count, missing_count, source_metric_keys`.

Allowed aggregations are mean, sample SD, paired mean difference, min/max over an explicit round range, and count. The analysis layer performs arithmetic once; models do not calculate unverified deltas. Example ID format is server-created `ev_<uuid>`, not accepted directly as a request to fetch arbitrary data. Evidence fetched for AI is scoped by the authenticated owner and requested run.

Analyst input excludes held-out test metrics for P0 so its follow-up advice cannot use test feedback. UI still shows test results independently. If a future read-only publication analyst receives test metrics, its output must not feed the tuning loop, and final claims after tuning require fresh evaluation seeds.

## 5. Analyst contract — AnalysisV1

| Field | Contract |
| --- | --- |
| `schema_version` | `analysis.v1` |
| `evidence_snapshot_hash` | Exact input snapshot |
| `status` | `supported` / `insufficient_evidence` |
| `findings` | ≤8 typed evidence-backed claims |
| `hypotheses` | ≤5 tentative explanations, with evidence IDs and a test that could distinguish alternatives |
| `limitations` | ≤8 statements; include sample count/missingness limitations where relevant |
| `next_experiment` | Null or one PlanProposalV1-style draft, never executed |

Typed finding fields: `claim_kind`, `metric_key`, `strategy_ids`, `relation`, `evidence_ids`, and `explanation`. Supported claim kinds: `value`, `difference`, `trend`, `missingness`. Relation enum: `higher`, `lower`, `unchanged`, `increased`, `decreased`, `insufficient`. The server resolves values and renders the quantitative sentence from a template. Do not accept a model-authored numeric value field.

For example, a difference finding points to a precomputed paired validation-loss delta and its two strategies; the UI supplies the actual numbers and unit. Direction must match the signed delta with an explicit 1e-8 zero tolerance. A trend claim needs an evidence item containing the requested interval delta; a single final value cannot prove a trend. “Better” requires the metric's declared optimization direction. Unknown/mismatched IDs, wrong split, wrong run, wrong hash, inverted sign, or missing required trial data fail validation.

Free-text explanations must not add uncited quantitative claims. Reject numeric tokens, spelled-out counts/percentages, or novel quantitative comparisons in this field; use a short approved explanatory vocabulary/template in the P0 UI when automatic checks cannot establish compliance. Human quality review still matters: deterministic number/ID checks do not prove semantic correctness. Causal explanations are displayed only under “Hypotheses,” never as measured findings. No chain-of-thought requested or stored.

If there are too few matched trials, return insufficiency or a descriptive finding with its explicit sample count. Do not invent significance or confidence intervals. The dataset can support “loss increased after a corrupted response” as an observation; proving the response caused the change requires a controlled ablation.

## 6. Follow-up controls

P0 supplies a draft recommendation only. In P1 F13, the service shows all configuration differences, controlled variables, expected information benefit, and estimated work. User approval binds exact plan revision/hash and a maximum run count. Editing invalidates approval. The scheduler has no freeform tool-execution loop.

The next-experiment adviser can vary one target factor, or propose an explicitly identified small factorial design in later schema versions. It cannot opportunistically change model initialization, datasets, aggregation, seeds, and message budget then call the outcome a fair policy comparison. Optimizing parameters against validation seeds requires separate evaluation seeds before reporting improvement.

## 7. F15 bounded policy profiles

This is a research extension, not a P0 dependency. For the nominated node only, permit:

- `balanced`: epsilon .10, utility_weight .70.
- `explore`: epsilon .30, utility_weight .70.
- `delivery_first`: epsilon .10, utility_weight .30.

All other parameters, budget, and aggregation remain fixed. Calls at rounds 10 and 20 influence subsequent rounds only and only when they exist. At most two calls per trial and 20 per experiment; reject larger selected trial sets before launch. No repair/retry call that exceeds those dispatch caps. Log profile, summaries supplied, response, and fallback. Policy adviser cannot see other nodes' private data, true bad-node identities, or global test performance. Rule baseline receives the exact same permitted summaries. Full multi-node LLM scheduling is deferred because it multiplies cost and complicates fair comparisons.

## 8. Versioning and AI-assisted development

Every prompt has a version, task schema, input contract, safety boundary, and eval case set. A prompt change is a code change: diff it, run relevant evals, retain the evaluation report, and do not mutate prompts for active operations. Model migrations require the same review. Default CI uses deterministic mocked outputs; an opt-in live smoke verifies the actual provider contract and is explicitly labeled.

Use the project AGENTS/SKILL/TASKS workflow for coding. The AI that helps write code is separate from runtime product AI; disclose both in delivery documentation. Neither model-generated code nor a green model self-review substitutes for executed tests and human review of scientific/security decisions.
