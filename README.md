# MeshVera — Development handoff

Version 2.0 · 19 October 2026 · Planning documents, not implemented software

MeshVera is an AI experiment copilot for studying adaptive communication in simulated decentralized learning networks.

## Important scope decision

The supplied files conflict. `SPEC(1).md` describes a Python simulation platform, while `AGENT(1).md` and `SKILL.md` describe a Node/Firebase multi-model answer service and explicitly exclude simulation. This pack deliberately selects the **simulation platform**, because the current request refers to the AI that converts natural-language prompts into experiment criteria. The original files are preserved; this is a proposed replacement handoff, not a silent edit of them.

Do not combine these two products. If the answer-service pivot is actually intended, resolve that product decision before implementation. This pack has not inspected the linked GitHub repository, run application tests, or verified existing implementation. All proposed commands and source paths are targets to create or adapt.

## Start here

1. Read `PRD.md` for product scope, feature dependencies, and acceptance criteria.
2. Read `AGENTS.md` and the relevant workflow in `SKILL.md` before coding.
3. Read `docs/ARCHITECTURE.md`, `docs/SIMULATION_SPEC.md`, `docs/AI_SPEC.md`, and `docs/DATA_API.md` for implementation contracts.
4. Work through `TASKS.md` one feature at a time. Everything starts as planned.
5. Use `START_HERE.md` as the opening instruction for your coding agent.

## Files

| File | Purpose |
| --- | --- |
| `PRD.md` | Feature-by-feature requirements, priorities, release gates |
| `AGENTS.md` | Canonical project instructions for coding agents |
| `AGENT.md`, `CLAUDE.md` | Small entry-point pointers; no duplicated policy |
| `SKILL.md` | Explicitly loaded project development playbook |
| `TASKS.md` | Ordered backlog and completion evidence |
| `START_HERE.md` | Copyable first coding-agent task |
| `docs/ARCHITECTURE.md` | Stack, directory structure, boundaries, execution |
| `docs/SIMULATION_SPEC.md` | Exact data, learning, communication, and policy rules |
| `docs/AI_SPEC.md` | AI contracts, evidence checks, ideas, budgets, evaluation |
| `docs/DATA_API.md` | Persistence, authorization, routes, state transitions |
| `docs/EVALUATION.md` | Scientific comparison and AI quality release gates |
| `docs/adr/0001-product-direction.md` | Why the simulation scope was selected |
| `docs/templates/FEATURE_TASK.md` | Reusable implementation ticket |
| `examples/experiment.v1.json` | Complete proposed configuration example |

This is a repository handoff, not an installed ChatGPT skill and not an application scaffold. The root `SKILL.md` is a project playbook; tool-native auto-discovery is not assumed. Commit the selected documents into the actual application repository during bootstrap, preserving existing unrelated work. No remote repository changes are made by this delivery.
