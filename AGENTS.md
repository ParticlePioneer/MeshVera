# MeshVera — Canonical coding-agent instructions

Scope: Python decentralized-learning simulator and AI experiment copilot described in `PRD.md`. This is a proposed implementation baseline, not a completed application. Follow higher-priority environment/user instructions first.

## Read before changing code

1. Existing repository instructions and current Git status.
2. `PRD.md`, `TASKS.md`, and the relevant feature ticket.
3. Relevant contracts in `docs/`; the workflow in `SKILL.md`.
4. Actual package scripts, adjacent code, migrations, and tests.

The uploaded older Node/Firebase answer-service instructions conflict with this direction. Do not combine them. If the actual repository implements that product, report the conflict before replacing architecture or deleting working features. This document does not authorize a destructive rewrite or deployment.

## Work feature by feature

- Pick one dependency-ready feature. State its ID, scope, acceptance criteria, and important assumptions.
- Implement a coherent slice with validation, failure behavior, persistence, and ownership as applicable.
- Add tests for concrete risks and acceptance criteria, not tests that merely mirror code structure.
- Run relevant checks. Record exact commands/results and what remains untested.
- Update contracts, feature evidence, and TASKS status. Keep unrelated work intact.
- Do not mark work completed because code compiled or a model said it looked correct.
- Do not create speculative features, broad refactors, extra providers, or infrastructure outside the selected ticket.

## Architecture invariants

- Pure simulation cannot depend on Streamlit, FastAPI, database clients, or LLM calls.
- API handlers validate/authenticate and delegate; business rules live in services, SQL in scoped repositories.
- Long-running simulation/AI uses durable jobs and separate workers.
- SQL transactions are short. No provider calls or long numerical loops inside a transaction.
- Shared schemas are canonical; generate OpenAPI from implemented contracts.

## Scientific invariants

- Implement SIMULATION_SPEC formulas exactly. Version any change and explain its experimental effect.
- Train, validation, and test splits are distinct. Test metrics never drive trust, policy selection, or follow-up proposal prompts.
- Keep dataset/init/aggregation/budget conditions matched across strategies.
- Use separate stable RNG namespaces; exogenous edge outcomes are keyed independently of selection order.
- Charge every attempted exchange. Failed attempts do not become free communication.
- Preserve negative findings. No guaranteed superiority, formal regret bound, or honesty probability.
- Model trust/utility is local; no hidden bad-node IDs, central oracle, or peer-private validation data in policy inputs.

## Product AI invariants

- Runtime AI proposes plans and explanations; numerical code creates metrics.
- Validate structured outputs and evidence references independently.
- User/model text is data, not permission to change policy, access other users, run code, fetch URLs, or raise limits.
- Only allowlisted typed operations; no arbitrary SQL/shell/Python execution.
- Draft proposals cannot launch until approval matches the exact revision/hash.
- Mock and live modes are explicit. A failed live call never silently becomes mock success.
- Prompt/schema/model changes require relevant evals and version updates.
- Use public concise rationale; do not request/store private chain-of-thought.

## Identity, secrets, and storage

- Verify Supabase tokens and assurance; derive ownership from verified subject only.
- Enforce ownership on every endpoint, export, query, evidence lookup, cancel, and deletion.
- API DB role must be non-owner/no-BYPASSRLS; reset actor context transaction-locally on pooled connections.
- Worker permissions do not replace target ownership and fencing checks.
- Commit placeholders only. Do not put credentials/tokens in prompts, URLs, fixtures, logs, or screenshots.
- No auth shortcut in production. Do not weaken RLS or tests to make a demo work.

## Execution correctness

Idempotent creation, lease/fencing, quota reservation, cancellation, terminal immutability, and deletion tombstones are required contracts. Never promise exactly-once external provider billing. Numerical interrupted trials can restart once; ambiguous AI dispatches cannot automatically retry. Consult DATA_API before changing lifecycle code.

## Verification and commands

Inspect `pyproject.toml` and README first. Architecture lists target commands to implement; it does not prove they already exist. Normal tests use synthetic data, local Auth/Postgres, and mock AI. Paid calls and deployment require the user's existing authorization or an explicitly configured opt-in; do not turn ordinary tests into paid integration runs.

Minimum relevant checks: lint/type checks for changed modules; acceptance-focused unit/API/integration tests; security tests when ownership changes; numerical fixtures when algorithm changes; AI evals when prompts/contracts change. Run broad checks only when the change warrants them or a release gate requires them.

## Completion handoff

Report: feature ID; changes and behavior; files touched; commands run and actual outcomes; unrun checks; migration/setup steps; limitations; next dependency-ready ticket. Update `TASKS.md` honestly: planned → in progress → implemented → verified, or blocked with a concrete reason. No fake test logs, fabricated benchmark numbers, or claims of live verification from fixtures.
