# Data, API, and execution contract

## 1. Storage model

Use UUIDs, UTC timestamps, foreign keys, explicit status enums, JSONB only for versioned bounded structures, and SQL migrations. `owner_id` is always derived from verified auth. Denormalize owner IDs into child tables and enforce composite foreign keys to prevent mismatched ownership.

| Table | Main fields / constraints |
| --- | --- |
| `experiments` | id, owner_id, name, description, revision, draft_config_json, approved_revision/hash nullable, archived_at; unique(id, owner_id) |
| `experiment_revisions` | experiment_id, owner_id, revision, canonical_config_json, config_hash, approved_at; unique(experiment_id, revision), immutable after approval |
| `runs` | id, owner_id, experiment_id, revision, config_hash, status, cancel_requested_at, parent_run_id nullable, manifest_json, created_at, completed_at; unique(id,owner_id) |
| `trials` | id, owner_id, run_id, seed, strategy, status, attempt_generation, metrics_manifest; unique(run_id,seed,strategy) |
| `round_metrics` | trial_id, owner_id, attempt_generation, round_number, validation/test macro loss/accuracy, honest-node diagnostic, communication counters; unique(trial_id,attempt_generation,round_number) |
| `trust_traces` | trial_id, owner_id, attempt_generation, round_number, receiver_id, neighbor_id, selected, usable, utility_g, utility_ema, delivery_estimate; unique trace key |
| `evidence_items` | id, owner_id, run_id, snapshot_hash, metric_key, dimensions_json, value/unit, source_keys_json; immutable |
| `ai_operations` | id, owner_id, kind, run_id/experiment_id nullable, status, mode, model/prompt/schema versions, evidence_hash, input_hash, output_json, usage_json, validation_json, error_code |
| `jobs` | id, owner_id, kind, target_id, status, lease_until, fencing_token, attempts, next_attempt_at, timestamps; server-only |
| `run_events` | run_id, owner_id, seq, event_type, bounded_safe_payload, created_at; unique(run_id,seq) |
| `idempotency_keys` | owner_id, route_scope, key_hash, request_hash, target_id, expires_at; unique(owner_id,route_scope,key_hash) |
| `usage_reservations` | id, owner_id, operation_id, reserved_calls/tokens, used_calls/tokens, state, quota_date; server-only |

Indexes: `(owner_id,created_at,id)` for history, `(run_id,seq)` for events, `(status,next_attempt_at,lease_until)` for claimable jobs, `(run_id,seed,strategy)` for trials, `(trial_id,attempt_generation,round_number)` for series. Retain only requested trace nodes, recording all their current neighbor estimates each round so unselected neighbors remain inspectable. Initial run event cap 2,000; coalesce repeated heartbeat events. Do not store raw datasets per round; regenerate from versioned seeds. Cap published round rows at 4,000 and estimated trace rows at 200,000 per run; reject excessive trace requests or let the user explicitly reduce trace nodes. Count trace bound conservatively as seeds × strategies × rounds × trace-node-count × (agents−1). Prune abandoned attempt generations after recovery. API results use bounded series pages (maximum 1,000 rows) and cursor metadata; list/evidence/events use the ordinary 100-item maximum. Full exports remain authenticated and bounded by stored run limits.

Approval hashes use canonical sorted-key JSON over the full validated config plus schema and numerical algorithm/data/scenario versions; exclude timestamps and display names. Include exact approved revision in run creation. Store approval as an application event, not an inference from a user's natural-language prompt.

## 2. Authorization and DB roles

Choose an API-owned application data path: users authenticate through Supabase Auth; all experiment operations go through FastAPI. Revoke direct `anon`/`authenticated` access to application tables in the exposed API schema; place application tables in a private schema and still enable RLS. Do not inadvertently expose writable views or functions.

The API uses a dedicated PostgreSQL role with no BYPASSRLS and no table ownership. In each short DB transaction it sets the verified request actor as a transaction-local parameter (e.g. `app.actor_id`) through a parameterized `set_config(..., true)` call. RLS uses that transaction-local UUID with `USING` and `WITH CHECK`. Missing actor means deny. Never derive actor from a request body. Do not keep actor settings on a pooled connection after transaction completion. This is a backend-managed RLS context, not a claim that a direct SQL connection automatically receives Supabase JWT claims.

Ownership clauses in repositories remain mandatory. The worker has a separate narrowly granted server role that can claim jobs and write the associated records; it validates the target/owner relationship and fencing token for every commit. Worker credentials and migration-owner credentials are never available to UI or prompts. A Supabase service-role key or table-owner connection can bypass RLS; do not use it as the ordinary API connection and then claim RLS isolates API users.

All protected API operations require verified `aal2`. Direct application-table access is denied even to authenticated browser clients, so they cannot bypass this API MFA gate. Integration tests cover role grants, RLS behavior with a non-owner role, connection-pool context reset, API ownership, and service/worker boundaries separately.

Return 404 for nonexistent or not-owned resources; use 403 for an authenticated actor lacking required MFA. GET and list/export/AI evidence endpoints receive the same ownership treatment as writes.

## 3. Public API v1

Use a common error envelope: `{error:{code,message,field_errors?,request_id}}`. Do not expose stack traces, SQL, tokens, or provider payloads. Bound text and JSON lengths. IDs must parse as UUIDs. APIs return ISO-8601 UTC timestamps.

| Method / route | Request / behavior | Response |
| --- | --- | --- |
| GET `/health`, `/ready` | Public liveness/readiness | 200; readiness 503 if required dependency unavailable |
| GET `/v1/me` | Valid authenticated token; aal1 permitted here | 200 safe identity + current assurance |
| GET `/v1/capabilities` | aal2 | 200 schemas, limits, supported strategies, safe AI availability |
| POST `/v1/experiments` | name, description, complete config | 201 draft, revision=1 |
| GET `/v1/experiments` | owner-scoped cursor/limit; optional archived flag | 200 items + next_cursor |
| GET `/v1/experiments/{id}` | owner lookup | 200 draft + revisions + runs summary |
| PATCH `/v1/experiments/{id}` | expected_revision, optional name/description/config/archive | 200 new revision for config edits; clear approval |
| POST `/v1/experiments/{id}/approve` | expected_revision + config_hash shown in UI | 200 immutable approved revision |
| POST `/v1/experiments/{id}/runs` | approved_revision, config_hash; Idempotency-Key header | 202 run_id, status_url; same request returns original resource |
| GET `/v1/runs/{id}` | owner lookup | 200 state, trial counts, progress, timestamps, safe error |
| GET `/v1/runs/{id}/events` | after_seq, limit | 200 bounded persisted events + next_seq |
| GET `/v1/runs/{id}/results` | optional strategy/seed filters within run | 200 completed/partial series; 409 RESULTS_NOT_READY before any publishable trial |
| GET `/v1/runs/{id}/evidence` | cursor/limit | 200 authorized immutable evidence |
| POST `/v1/runs/{id}/cancel` | Idempotency-Key | 202 cancellation requested; terminal cancel repeat 200; other terminal state 409 |
| POST `/v1/runs/{id}/retry` | failed/partial/cancelled source, approved snapshot; Idempotency-Key | 202 new full run linked to source; original remains immutable |
| GET `/v1/runs/{id}/export` | format=json/csv-bundle | 200 authorized attachment; partial label where relevant |
| DELETE `/v1/experiments/{id}` | owner, no active jobs or AI operations | 204; 409 ACTIVE_WORK otherwise |
| POST `/v1/ai/plans` | prompt ≤4,000 chars, optional owned experiment revision; Idempotency-Key | 202 ai_operation_id + status_url |
| GET `/v1/ai/operations/{id}` | owner lookup | 200 status/output/validation summary |
| POST `/v1/ai/operations/{id}/cancel` | owned nonterminal operation | 202; same terminal semantics as runs |
| POST `/v1/runs/{id}/analyses` | terminal complete/partial run, evidence_snapshot_hash; Idempotency-Key | 202 AI operation; 409 if evidence unavailable |

Auth registration, verification, MFA enrollment/challenge, refresh, and logout use the provider's supported Auth APIs; do not proxy passwords into application logs or store TOTP secrets in app tables. Generate checked OpenAPI from the FastAPI/Pydantic implementation and snapshot-review changes in CI.

Errors: 400 malformed JSON, 401 missing/invalid auth, 403 MFA required, 404 missing/not-owned, 409 revision/state/idempotency conflict, 422 schema/domain validation, 429 quota exceeded, 503 unavailable dependency. List cursors are opaque owner-scoped sort positions; never accept cursor-embedded identity as authorization.

## 4. Run state machine

| State | Allowed next states |
| --- | --- |
| queued | running, cancel_requested, failed |
| running | completed, partial, failed, cancel_requested |
| cancel_requested | cancelled |
| completed / partial / failed / cancelled | none |

Retry creates a new run. `partial` means at least one trial completed and at least one failed after its allowed retry. All failed means `failed`. Explicit user cancellation ends as `cancelled`, with completed trial artifacts still viewable and labeled. A crashed worker does not reset the run to queued; an expired job lease is reclaimed while run status remains running. A separate recovery sweep finalizes queued cancellations and expired cancel-requested jobs.

AI operation states: queued → running → completed/failed/interrupted_unknown; queued/running → cancel_requested → cancelled. Mode and completion state are separate. No AI failure rewrites a terminal simulation status.

## 5. Atomic submission and idempotency

In one transaction: verify owner and exact approved revision; lock owner quota row; enforce active/queue cap; insert or compare `(owner,route,key)` idempotency record; insert run/trials/job; commit. Hash canonical request bytes after schema normalization. Identical requests return original resource/status; different hash with same key returns 409. Retain keys for at least seven days and document expiry; clients must not reuse expired keys to infer exactly-once semantics.

AI submission uses the same pattern, with its own active/quota reservations. Quota enforcement must remain correct across duplicate API instances.

## 6. Job claim, cancellation, and commit

1. Claim eligible jobs using a short transaction and row lock/`FOR UPDATE SKIP LOCKED`; write a new random fencing token and 60-second lease. Commit before numerical work or external calls.
2. Heartbeat at least every 15 seconds. CPU work must not block lease renewal; use a controlled process/thread boundary or chunked steps and test it. If renewal fails, stop and discard writes.
3. Before any result batch, atomically verify token, live lease, nonterminal/noncancelled target, and matching owner. Every result-writing transaction performs this check. A check followed by an unrelated unfenced commit is insufficient.
4. Each trial attempt uses a generation ID. Store its own provisional rows; publish only a completed generation. Retried numerical trials restart from initial state, not from partially saved optimizer state; increment generation and ignore old provisional rows.
5. Check cancellation between rounds and before publishing. A cancellation transaction locks the same run row; whichever terminal/cancel transition commits first wins. After accepted cancellation, late results cannot publish a completion.
6. On numerical crash, restart only the interrupted trial once. Preserve completed trial generations. On second interruption/failure, mark trial failed and continue remaining trials within run deadline.
7. On AI crash after dispatch with unknown outcome, mark interrupted_unknown; no automatic new dispatch. Explicit retries create a new AI operation with warning metadata.
8. Publish final run summary/evidence only from completed trial generations. Store terminal state and final event atomically. Do not mutate a terminal run when an old worker returns.

Delete rejects all nonterminal associated simulation/AI jobs. Under a parent lock, tombstone the experiment first; worker commits check tombstone before writing. In P0, delete the bounded descendants and parent in the same transaction, including evidence, AI outputs, and traces; return 204 only after commit. Prevent new runs/AI operations during this transaction. If later scale requires asynchronous cleanup, introduce an explicit 202/deletion-status contract before using a cleanup job. No orphaned background work can recreate deleted content.
