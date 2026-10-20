# Architecture and repository structure

Status: proposed structure; paths and commands are not claims about existing code.

## Stack decisions

| Layer | Choice | Reason |
| --- | --- | --- |
| Runtime | Python, supported compatible version pinned at F00 | One numerical/application language |
| Simulation | NumPy; independent metric cross-checks with scikit-learn | Explicit optimizer and deterministic control |
| UI | Streamlit + Plotly | Small research interface aligned with the original spec |
| API | FastAPI + Pydantic | One validation/security boundary reusable by another UI |
| Persistence | Supabase PostgreSQL, SQL migrations, psycopg repositories | Relational experiment data and transactional jobs |
| Identity | Supabase Auth with TOTP MFA | Managed identity rather than custom passwords |
| Jobs | PostgreSQL queue + separate Python worker | Durable execution without adding Redis to P0 |
| AI | One official provider SDK behind an adapter, plus fixtures | Swappable provider without multi-provider complexity |
| Quality | pytest, Ruff, mypy, integration database tests | Scientific invariants plus application checks |

Streamlit talks to FastAPI for application data. Auth uses the configured Supabase Auth flow, with tokens scoped to the current Streamlit session; never place user tokens in global caches. The API and worker share only documented contracts and PostgreSQL records. AI tasks run in the worker, with their own state and budget.

FastAPI documents that heavy computation may need a separate worker system. PostgreSQL documents `SKIP LOCKED` as suitable for queue-like consumers; it does not itself provide a complete job system. The claim, lease, fencing, retry, and cancellation protocol must be implemented and tested. Sources are linked in PRD.

## Dependency direction

`ui → API routes → application services → repositories / job submission`

`worker → simulation engine / AI service → normalized result contracts → repositories`

`simulation engine → NumPy + pure domain contracts` only.

LLM adapters may consume summarized validation evidence. They cannot import database credentials into prompts, execute SQL/code, or directly mutate experiment metrics. The simulation package must remain callable from a CLI with no UI, provider, or database dependency.

## Proposed file map

| Path | Ownership / contents |
| --- | --- |
| `AGENTS.md` | Canonical coding-agent rules |
| `AGENT.md`, `CLAUDE.md` | Compatibility pointers to AGENTS.md |
| `SKILL.md`, `TASKS.md` | Explicit workflows and verified task status |
| `pyproject.toml`, dependency lockfile | Package metadata, scripts, pinned environment |
| `.env.example`, `.gitignore` | Placeholder settings and excluded local secrets |
| `src/meshvera/config.py` | Strict startup settings and resource limits |
| `src/meshvera/domain/` | Config, job, evidence, and result types |
| `src/meshvera/api/main.py` | App factory, health/readiness |
| `src/meshvera/api/auth.py` | Token validation and assurance level |
| `src/meshvera/api/routes/` | Experiments, runs, evidence, AI operations, exports |
| `src/meshvera/services/` | Owner-aware use cases and approval logic |
| `src/meshvera/db/repositories/` | Scoped SQL, transactions, read/write boundaries |
| `src/meshvera/worker/main.py` | Job polling and lifecycle |
| `src/meshvera/worker/leases.py` | Atomic claims, heartbeat, fencing |
| `src/meshvera/sim/data.py` | Synthetic dataset generation and splits |
| `src/meshvera/sim/model.py` | Logistic forward pass, loss, gradient update |
| `src/meshvera/sim/topology.py` | Seeded graph construction |
| `src/meshvera/sim/scenario.py` | Bad-peer mask and keyed exogenous events |
| `src/meshvera/sim/network.py` | Attempt/delivery ledger and budgets |
| `src/meshvera/sim/policies/` | Fixed, random, reliability, adaptive selectors |
| `src/meshvera/sim/engine.py` | Synchronous round protocol |
| `src/meshvera/sim/aggregation.py` | Common blend rule |
| `src/meshvera/sim/metrics.py` | Validation/test metrics and counters |
| `src/meshvera/analysis/` | Aggregates, paired deltas, evidence registry |
| `src/meshvera/ai/providers/` | Mock/live adapter, timeouts, normalized errors |
| `src/meshvera/ai/prompts/` | Versioned planner/analyst templates |
| `src/meshvera/ai/validators.py` | Schema, evidence, comparison, and bounds checks |
| `src/meshvera/ai/service.py` | Plans/analyses and bounded repair |
| `ui/app.py`, `ui/pages/`, `ui/components/` | Thin presentation and user session handling |
| `supabase/migrations/`, `supabase/tests/` | Tables, roles, grants, RLS, database assertions |
| `tests/{unit,sim,api,integration,e2e}/` | Behavioral and failure-path tests |
| `evals/{cases,fixtures,reports}/` | AI eval inputs and generated reports |
| `scripts/` | Seed, benchmark, replay, smoke-test helpers |
| `docs/adr/`, `docs/features/` | Decisions and completed feature evidence |
| `.github/workflows/ci.yml` | No-secret default checks and isolated integration jobs |

No empty directory is considered an implemented feature. Bootstrap only what F00 needs; grow the structure with the feature tickets.

## Environment contract

Implement validated settings for `APP_ENV`, `SUPABASE_URL`, public auth key, `AUTH_ISSUER`, `AUTH_AUDIENCE`, `AUTH_JWKS_URL`, `API_DATABASE_URL`, `WORKER_DATABASE_URL`, `LLM_MODE`, `LLM_PROVIDER`, `LLM_MODEL`, provider secret, API origin, and per-run resource limits. Exact provider key names belong to the chosen adapter. Separate migration credentials from runtime credentials. Use development-only local URLs for fixtures; production must reject mock-auth overrides.

`LLM_MODE=mock` is explicit in local setup and recorded in AI operation metadata. Real numerical simulation is still real simulation when the language model is mocked. Never label fixture-generated AI analysis as live.

## Target commands to implement in F00

| Command contract | Required behavior |
| --- | --- |
| `python -m meshvera.api` | Start API with validated settings |
| `python -m meshvera.worker` | Start durable worker |
| `streamlit run ui/app.py` | Start UI |
| `python -m meshvera.cli simulate --config examples/experiment.v1.json` | Run pure engine and export local metrics |
| `python -m pytest tests/unit tests/sim` | Deterministic no-network tests |
| `python -m pytest tests/api tests/integration` | Local Auth/Postgres integration tests |
| `python -m pytest tests/e2e` | Main journey with mock AI |
| `python -m ruff check .` / `python -m mypy src` | Lint and type checks |
| `python -m meshvera.evals --mode mock` | Deterministic AI contract/grounding checks |
| `python -m meshvera.evals --mode live --max-calls 3` | Explicit, capped provider verification |

These are target interfaces, not commands executed during document creation. Pin a compatible runtime and dependencies; document installer commands for the chosen package manager. Do not invent a working command when its module is missing.
