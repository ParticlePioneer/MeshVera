# MeshVera — Product and implementation PRD

Version 2.0 · 19 October 2026 · Status: proposed implementation baseline

## 1. Product decision

**Build an AI experiment copilot that helps users design, run, explain, and improve reproducible experiments on decentralized learning networks.**

The core question is: under a fixed communication budget, when does locally adaptive neighbor selection help or hurt compared with fixed, random, and reliability-only policies?

The product has two different forms of AI:

- **Numerical learning:** each simulated node trains a logistic classifier; an adaptive policy learns neighbor usefulness from local observations.
- **LLM assistance:** a research copilot proposes controlled experiments, interprets measured evidence, and recommends follow-up tests. It does not manufacture metrics or decide truth by consensus.

The supplied Node/Firebase answer-service instructions conflict with the supplied simulator specification. This PRD uses the simulator as the working direction because it matches the current request. `docs/adr/0001-product-direction.md` records that assumption. The original documents remain unchanged.

## 2. Users and jobs

| User | Job | Successful outcome |
| --- | --- | --- |
| Student / researcher | Test communication strategies without building infrastructure | A reproducible comparison with inspectable configuration and measured results |
| Demonstrator / reviewer | Understand what the algorithm and AI actually contribute | A short walkthrough showing real simulation, evidence-linked AI analysis, and limitations |
| Developer / coding agent | Implement the product incrementally | Small features with explicit contracts, failure behavior, and verification evidence |

Primary use case: “Does selecting useful neighbors reduce communication without damaging prediction quality when some peers send corrupted updates?”

## 3. Core journey

1. Register, verify the account as configured, sign in, and enroll/verify TOTP MFA.
2. Describe a research goal, or choose a manual preset.
3. AI proposes a hypothesis, baseline comparison, parameters, seeds, controlled variables, and assumptions.
4. Review an editable plan with a configuration diff, simulation work estimate, and AI-call allowance; approve a particular plan revision.
5. Execute the immutable approved experiment asynchronously; inspect progress or cancel.
6. View real metric charts, uncertainty across seeds, and trust/selection behavior.
7. Ask AI to explain the result. Open the metric references behind each quantitative finding.
8. Review one suggested follow-up experiment. Approval creates a new linked experiment; it never rewrites the old result.
9. Sign out and back in, retrieve the same result, and download its reproducibility bundle.

Manual setup and numerical execution remain usable if the AI provider is unavailable. An AI failure must not mark a completed simulation as failed.

## 4. Release boundaries and feasibility

| Release | Scope | Exit condition |
| --- | --- | --- |
| Four-day demonstration | F00–F04 foundation; F05 fixed/random only; F06 adaptive; F07 execution; F08 basic charts; F09 planner; F10 one evidence-based analysis; essential F11 save/export; F12 smoke checks | One small end-to-end scenario works, MFA and isolation are checked, and a real AI call is disclosed |
| P0 complete MVP | All F00–F12 requirements, including reliability baseline, failure paths, repeated seeds, recovery tests, and AI eval fixtures | Every P0 acceptance criterion passes with evidence |
| P1 research extensions | F13–F16, after the P0 gates | Each extension evaluated against its specified comparator |

Four days is a tightly limited demonstration target, not a promise that the full release fits that time. Plan roughly 10–15 focused engineering days for P0 with one experienced developer and an AI coding agent, subject to integration and review; this is a planning estimate, not measured throughput. Freeze scope after the first end-to-end slice. If time runs short, show documented omissions instead of calling the demo a complete MVP.

Do not implement in P0: real device deployment, distributed consensus, arbitrary uploaded code, LLM-written executable policies, external browsing, vector search, foundation-model training, adaptive historical model reputation, billing, organizations, real private datasets, or autonomous unbounded experiment loops. Partition/reconnection and changing reliability schedules belong to P1.

## 5. Product success and release targets

Targets below are requirements to verify, not achieved metrics:

- All official demo result values originate in the simulation/evaluation pipeline.
- Every displayed quantitative AI claim resolves to a server-computed evidence item.
- No cross-user access in the authorization test matrix, including exports and AI evidence.
- Same configuration, seed, algorithm version, and pinned numerical environment reproduce metrics within declared tolerances.
- A user can finish the main journey and retrieve results after a new login.
- The default small comparison should complete within 120 seconds on a declared 4-vCPU / 8-GB reference environment, excluding provider latency; benchmark during F12. If unmet, optimize or revise the preset before release.
- Run creation should return within one second at the reference load; UI polling every two seconds must not launch duplicate work.
- No requirement that the adaptive policy beats baselines. Negative and inconclusive results are valid outcomes.

## 6. Feature implementation tickets

Each feature is a vertical slice: behavior, contract, implementation, failure handling, tests, and documentation. Source paths below are proposed destinations. Detailed shared contracts live in the companion documents.

### F00 — Repository foundation and executable contracts [P0]

**Depends on:** none. **Outcome:** local developers can start the UI/API/worker and process a deterministic fixture job without LLM credentials. The numerical engine arrives in F03–F06.

**Build:** inspect the existing repository; record what exists and conflicts. Create the Python package, typed settings, FastAPI app factory, separate worker entry point, Streamlit entry point, lockfile, lint/type/test tooling, local Supabase setup, placeholder-only environment file, and CI skeleton. Add the new canonical agent instructions. Keep simulation independent of UI, network, auth, and LLM imports.

**Files:** `pyproject.toml`, lockfile, `src/meshvera/{api,worker,sim,ai,db}`, `ui/`, `tests/`, `supabase/`, `.github/workflows/ci.yml`.

**Accept:** a fresh setup can follow README commands; `/health` returns liveness and `/ready` checks required dependencies without exposing secrets; test mode refuses live LLM calls by default; startup validates required production settings; all documented commands actually exist.

**Failure:** missing settings produce actionable startup errors; missing optional LLM key disables live AI only, not simulation.

### F01 — Identity, MFA, and ownership [P0]

**Depends on:** F00. **Outcome:** each user accesses only their own experiments and evidence.

**Build:** Supabase Auth registration/login/logout, email verification where configured, TOTP enrollment/challenge/verification, expiry/refresh handling, and `/v1/me`. FastAPI verifies signature, issuer, audience, expiry, subject, and required assurance level. Require `aal2` for experiment and AI operations; permit `aal1` only for identity/enrollment flow. Do not implement a second password/JWT system. Add RLS and separate server roles as defined in DATA_API.

**Files:** `ui/pages/account.py`, `api/auth.py`, `db/repositories/`, SQL migrations and isolation tests.

**Accept:** two actual test users cannot read, modify, cancel, export, or supply each other's IDs to AI endpoints. An `aal1` token cannot reach protected application operations by bypassing the UI. Expired, tampered, wrong-issuer tokens fail. Logout clears per-session tokens and user-scoped UI caches.

**Failure:** provider errors and invalid TOTP codes are safe and actionable; no token is placed in URLs/logs. Document provider-supported account recovery; do not add an authentication bypass for lost factors.

### F02 — Experiment configuration and revisioned approval [P0]

**Depends on:** F00, F01. **Outcome:** manual and AI plans use one validated configuration contract.

**Build:** strict Pydantic models, versioned JSON schema, defaults, manual editor, presets, plan revision/hash, ownership, and workload estimation. A draft can be edited; approval pins the precise revision. An edit invalidates prior approval. Display assumed values explicitly. Store name/description separately from numerical config.

**Contract:** `ExperimentConfigV1` in SIMULATION_SPEC; `POST /v1/experiments`, `PATCH .../{id}`, `POST .../{id}/approve`.

**Accept:** invalid types, unknown fields, incompatible parameters, duplicate seeds, excessive work, and stale revisions fail with field-level errors. An example config round-trips without loss. Prompt input and manual input cannot bypass limits. Every run references an approved immutable snapshot.

**Failure:** 409 for revision conflict, 422 for invalid config, 429 for exhausted admission quota. Never silently clamp AI output or silently reduce requested seeds.

### F03 — Seeded data, local models, and measurement [P0]

**Depends on:** F00, F02. **Outcome:** a single node learns from a reproducible synthetic classification task.

**Build:** class-conditional non-IID data generator; disjoint local train/validation/test splits; fixed-step NumPy logistic regression; deterministic initialization; loss/accuracy functions; data/algorithm versioning. Use scikit-learn only where useful for independently checking metrics, not to hide optimizer defaults.

**Files:** `sim/data.py`, `sim/model.py`, `sim/metrics.py`, `tests/sim/`.

**Accept:** same seed reproduces generated arrays in a pinned environment; no split overlap; parameters remain finite or the trial fails explicitly; validation data alone is used for neighbor utility, and test data never enters policy/planner feedback. On a separable test fixture, learning reduces train loss.

**Failure:** any non-finite honest model update or impossible dataset configuration fails the trial with diagnostics; corrupted incoming peer updates follow F04/F06 rules instead.

### F04 — Topology, transmissions, and unreliable peers [P0]

**Depends on:** F03. **Outcome:** communication costs and failures are real simulation events.

**Build:** static ring, seeded undirected random graph, fully connected graph; directed request/response exchanges over those edges; packet loss; fixed bad-peer selection; missing-response and sign-flip behavior. Apply same exogenous conditions across compared strategies using keyed random streams. Count attempts even when delivery fails. Treat bad-peer identity as hidden from all policies.

**Files:** `sim/topology.py`, `sim/network.py`, `sim/scenario.py`.

**Accept:** no self-neighbors; valid symmetric edges; no messaging to non-neighbors; no budget overflow; packet-loss extremes behave correctly; isolated nodes continue local training; attempted and delivered byte counters match the documented ledger; same edge/round/seed gets the same exogenous outcome across strategies.

**Failure:** malformed or non-finite payloads are rejected, counted, and never used in aggregation. No infinite retry of a failed exchange.

### F05 — Fixed, random, and reliability-only baselines [P0]

**Depends on:** F04. **Outcome:** the adaptive policy has meaningful comparators.

**Build:** pure selection interfaces plus fixed-order, uniform-random, and observed-delivery policies. All receive the same allowed local state, budget, model initialization, dataset splits, and aggregation rule. Fixed and reliability policies break ties deterministically. Each strategy starts fresh; state is never carried from an earlier comparison.

**Files:** `sim/policies/{base,fixed,random,reliability}.py`.

**Accept:** `select()` returns unique current neighbors only, within remaining budget. Reliability estimates update only from observed attempts. Changing strategy evaluation order does not change numerical results. All three baselines are available in full P0; the four-day slice may show two and label the missing third.

**Failure:** policy output outside the interface fails validation and the trial, rather than being silently treated as a valid baseline.

### F06 — Local adaptive trust policy [P0]

**Depends on:** F05. **Outcome:** nodes learn which neighbors are useful under limited communication.

**Build:** the exact EWMA utility + smoothed delivery estimate + epsilon exploration policy in SIMULATION_SPEC. Measure usefulness on the receiver's local validation split, using each candidate independently against the same local-model snapshot. Separate delivery reliability from learning utility. Log selection, utility, and estimate updates for chosen trace nodes.

**Files:** `sim/policies/adaptive.py`, `sim/aggregation.py`, policy arithmetic/property tests.

**Accept:** initial values, failed-attempt updates, exploration, tie breaking, candidate loss, and aggregation match hand-calculated fixtures. Utility is receiver-specific. No policy reads global truth, hidden bad-node labels, other nodes' private validation data, or test metrics. Zero budget yields exactly the local-only path.

**Failure:** invalid peer vectors are excluded; valid but harmful finite updates can hurt performance, and the product must show that rather than silently introducing a new robust aggregation algorithm.

### F07 — Durable experiment execution and cancellation [P0]

**Depends on:** F01–F06. **Outcome:** a browser refresh or API restart does not own the simulation's lifetime.

**Build:** PostgreSQL jobs, transactional claim with lease/fencing, per-user admission control, experiment-run trials by seed/strategy, stage/round progress, immutable completed trial results, bounded automatic retry, cancellation, and terminal-state guards. Run simulation in a separate worker process. Restart an interrupted trial deterministically from its beginning in P0; preserve already completed trials.

**Contract:** create run 202; poll status/events; cancel; explicit retry creates a new run. State machine and transaction protocol in DATA_API.

**Accept:** duplicate submit yields one run; same idempotency key/different body returns 409; two workers do not commit the same trial; stale leases cannot write; cancelled jobs cannot become completed through late writes; process crash resumes with at most one automatic interrupted-trial retry. No external provider request happens in a database transaction.

**Failure:** report partial results when some trials succeed and others fail; do not aggregate them as a balanced complete comparison. A manual retry links to the failed run and does not overwrite it.

### F08 — Results, comparison, and trust inspection [P0]

**Depends on:** F07. **Outcome:** users can inspect measured behavior without accepting an AI explanation.

**Build:** Plotly learning curves, cumulative attempted/delivered exchanges and logical bytes, final metric table, per-seed points, mean/sample SD, paired differences, and selected-node trust timeline. Label validation vs held-out test, completed vs partial, mock vs live AI, and uncertainty. Persist machine-readable evidence items used by F10.

**Files:** `ui/pages/results.py`, `ui/components/`, `analysis/summaries.py`, `analysis/evidence.py`.

**Accept:** chart values match stored trial metrics; missing trials are visible; no claim of significance from a single seed; user can open evidence by stable ID; a baseline outperforming adaptive is displayed without euphemism. Trust is labeled a local heuristic estimate, not a probability of honesty.

**Failure:** empty/failed runs display actionable states, not zero-valued success charts; null metrics remain null.

### F09 — AI experiment designer [P0, core AI]

**Depends on:** F02, F05, F06. **Outcome:** users receive a coherent experiment, not just extracted filters.

**Build:** structured LLM output for research question, falsifiable hypothesis, valid configuration, controlled variables, baseline choices, expected comparison, assumptions, and clarification needs. Use one real provider adapter and a deterministic mock. The server computes workload and validates feasibility independently. Require review and explicit approval before launching.

**Contract:** `POST /v1/ai/plans` → AI operation ID; `PlanProposalV1` in AI_SPEC; proposed plan can be imported into an editable draft.

**Accept:** a request about corruption produces a testable comparison with baselines and seeds; ambiguous “strict budget” is an assumption for review or a clarification, not an unexplained magic number; an impossible request yields clarification/rejection; invalid schema cannot create a runnable experiment. A genuine live planning call is demonstrated separately from mock tests.

**Failure:** timeout/rate limit/refusal/malformed output leaves manual configuration available. Missing credentials never silently substitute a mock result labeled live.

### F10 — Evidence-based AI analyst [P0, core AI]

**Depends on:** F08, F09 adapter infrastructure. **Outcome:** users understand what happened, what remains uncertain, and what to test next.

**Build:** an immutable evidence bundle with metric IDs, exact values, round ranges, seed counts, paired deltas, missingness, and configuration metadata. LLM returns findings that reference those IDs, limitations, hypotheses, and one proposed follow-up. Quantitative statements use typed claims rendered from server values, not model-invented numbers. Follow-ups remain drafts.

**Contract:** `POST /v1/runs/{id}/analyses` and analysis operations; `AnalysisV1` in AI_SPEC.

**Accept:** every displayed numeric finding resolves to authorized evidence; fabricated IDs/wrong direction/wrong comparison are rejected; “adaptive lost” fixtures produce an honest loss finding or abstention; correlation does not become a causal claim; sparse/partial runs state insufficiency. A user can open the underlying chart/table from a finding.

**Failure:** one bounded schema/claim repair is allowed within the same allowance; otherwise show measured results and “AI analysis unavailable.” No generated result is written into simulation metric tables.

### F11 — History, reproducibility, and deletion [P0]

**Depends on:** F07, F08; AI export fields after F09/F10. **Outcome:** a saved result is inspectable and reproducible after a new login.

**Build:** owner-scoped history with pagination, rename/archive, read-only run detail, linked retries, JSON/CSV reproducibility export, and controlled permanent deletion. Export configuration, versions, environment manifest, seeds, actual metrics, AI provenance, and warnings. CSV export must escape spreadsheet-formula prefixes in user text.

**Accept:** logout/login preserves history; export reproduces the same numeric fixture locally; no credentials/raw access tokens in exports; every download is authorized; deletion rejects active runs with 409 and asks the user to cancel/wait first; terminal descendants and AI payloads are removed together. An archived result remains recoverable until deleted.

**Failure:** incomplete runs export as partial with missing trials explicit. Exact regeneration of LLM wording is not promised; retain the original accepted output and hashes.

### F12 — Evaluation, observability, CI, and release [P0]

**Depends on:** F00–F11. **Outcome:** quality claims are backed by repeatable checks.

**Build:** test matrix in EVALUATION, AI fixtures, migration/isolation integration tests, end-to-end mock journey, opt-in capped live smoke test, structured logs without prompt/token content, timing/usage metrics, threat-boundary checks, setup guide, and AI usage disclosure. Store real evaluation reports keyed to commit/config/prompt version.

**Accept:** all critical security/integrity checks pass; a fresh environment completes the demo; recorded benchmark states hardware and limitations; live credentials/model ID are verified against official provider documentation during implementation; release artifacts distinguish tested, untested, and deferred behavior.

**Failure:** a failed integrity/security gate blocks release; poorer adaptive accuracy does not. AI quality below target blocks enabling that AI feature by default, not access to valid manual experiments.

### F13 — Approved next-experiment loop [P1, recommended first extension]

**Depends on:** F10–F12. **Build:** the analyst proposes up to three bounded next experiments using validation evidence, a specified question, and an expected information benefit. The user selects/edits/approves one; the scheduler launches it and links parent/child experiments. No automatic launch in this release. Use fresh held-out evaluation seeds for any claimed improvement after tuning.

**Accept:** approvals bind exact hashes; stale plans cannot launch; duplicate launch is idempotent; every change from the parent is shown; test results are withheld from proposal inputs; compare usefulness with a fixed scenario grid. Cap one approved batch to five experiments and the ordinary per-run work limits.

### F14 — AI stress-scenario designer [P1]

**Depends on:** F13. **Build:** extend scenario schema for timed packet-loss changes, partition/reconnection, and reliability shifts; AI outputs only this DSL, never Python. Validate event times, edge IDs, ordering, bounds, and cost before approval.

**Accept:** generated scenarios replay identically; contradictory events fail validation; compare coverage and nonredundancy against hand-written scenarios. Descriptions cannot declare an agent malicious based on observed trust alone.

### F15 — AI-assisted bounded policy adviser [P1, experimental]

**Depends on:** F12 and separate policy ADR. **Build:** at most two advisory calls per trial at rounds 10 and 20, only when subsequent rounds exist. Send local validation/communication summaries for one nominated node; return an allowlisted profile changing its exploration/utility weights. The deterministic engine enforces the profile and records every decision. Compare with the identical policy using fixed profiles and a rule-based switcher. Replay recorded actions for reproducibility.

**Accept:** equal message budgets and information constraints; no hidden bad labels or test data; no arbitrary code; timeout retains the previous profile; record added inference latency/tokens separately. Include profile/call cost in conclusions. F15 can be rejected if its benefit does not justify its overhead.

### F16 — Grounded research report and anomaly explanations [P1]

**Depends on:** F10, F12. **Build:** report export assembled from authoritative tables/charts and AI explanatory text; deterministic anomaly flags for loss spikes and delivery drops with AI-generated hypotheses linked to events. Reuse evidence validation rather than introducing a second truth source.

**Accept:** all numbers match source artifacts; simulation-vs-real-world limitations remain visible; anomaly explanations distinguish observation from cause. Report contains enough config/version/seed detail to reproduce the comparison.

## 7. UX requirements

Pages: Account; Experiments; New experiment; Plan review; Run progress; Results; AI analysis. In P0, the follow-up proposal appears in analysis as a draft recommendation; execution-loop management is P1.

Every long-running page must show a stable ID, status, last update, and clear next action. Review shows parameter changes, assumptions, estimated work, and approval button. Results show charts before AI interpretation. Distinguish “measured,” “hypothesis,” and “insufficient evidence.” Do not make users read internal SDK/prompt details to launch an experiment; place provenance in an expandable technical panel.

## 8. Non-functional requirements

- Authentication/authorization enforced on the server and at database boundaries, not only in Streamlit widgets.
- Separate worker; persistent jobs; bounded resource use; no provider/CPU work inside request-owned background tasks.
- Bounded API bodies (64 KiB), prompts (4,000 characters), provider outputs (24 KiB), and paginated list/event responses (default 25, maximum 100).
- TLS in deployment; secrets server-only; no public CORS wildcard with credentials; private error details in redacted logs only.
- Structured logs include request/run/job IDs, stage, duration, and normalized error class. Default logs exclude prompts, generated text, and authentication material.
- Version configuration, algorithm, scenario, prompts, model identity, schema, and dependencies. Record exact values, not just “latest.”
- P0 supports one API process and one worker for reference benchmarking, with database-level claims safe against accidental duplicate workers. Do not advertise horizontal scale before load tests.

## 9. Delivery sequence

| Milestone | Features | Reviewable evidence |
| --- | --- | --- |
| M0 foundations | F00, F01, F02 | Fresh setup, MFA test, isolated drafts |
| M1 numerical engine | F03–F06 | Deterministic tiny fixtures and baseline comparison |
| M2 runnable product | F07, F08, F11 core | Submit → poll → results → login again → export |
| M3 meaningful AI | F09, F10 | Real planning call and verified evidence-linked interpretation |
| M4 release gates | F11 complete, F12 | Eval report, recovery/security tests, walkthrough |
| M5 extensions | F13 then selected F14–F16 | Measured value against the declared comparator |

Build one feature per coherent change. Do not mark a feature done solely because files exist. `TASKS.md` records acceptance evidence and limitations. Every coding-agent handoff includes commands actually run, results, and the next dependency-ready task.

## 10. Outstanding decisions and safe defaults

No need to block document preparation on these choices. During F00, verify existing repository compatibility, deployment capacity, provider/model availability, SDK versions, and MFA setup. Default to Python + Streamlit + FastAPI + PostgreSQL/Supabase and one LLM provider. Keep version/model selection in validated settings. Any decision to switch back to the multi-model answer product requires a new scope ADR and replacement requirements, not mixed instructions.

## 11. Documentation basis

This product/algorithm design is a proposal. Current implementation guidance was checked against official documentation on 19 October 2026: [FastAPI background tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/), [Supabase RLS](https://supabase.com/docs/guides/database/postgres/row-level-security), [Supabase MFA](https://supabase.com/docs/guides/auth/auth-mfa), [OpenAI structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs), and [PostgreSQL SELECT/locking](https://www.postgresql.org/docs/current/sql-select.html). Verify exact SDK interfaces when implementing. No source establishes that this proposed policy is novel, optimal, or empirically superior.
