# ADR 0001 — Use the simulator as the product baseline

Date: 19 October 2026. Status: proposed working assumption for this handoff.

## Context

The supplied `SPEC(1).md` describes Python/Streamlit/PostgreSQL decentralized-learning experiments with natural-language configuration. `AGENT(1).md` and `SKILL.md` instead describe a Node/Express/Firebase multi-model answer service and forbid simulation. Those documents cannot govern one implementation simultaneously.

The current request says AI only turns a prompt into specific criteria and asks to expand AI into a core feature. That description matches the simulator specification.

## Decision

Use the simulator direction, retain its numerical research question, and add experiment design, evidence-based interpretation, and approved follow-up planning. Use Python/Streamlit/FastAPI/Supabase. Create new consistent handoff documents; preserve originals.

## Consequences

Do not carry over Firebase schemas, answer-review scoring, multi-provider voting, or the backend-only restriction. Keep useful general practices from the older instructions: ownership, explicit mock/live modes, budgets, validation, durable jobs, transparent limitations, and honest test reporting.

The linked repository has not been inspected. F00 must reconcile existing implementation before changing architecture. If the owner confirms the answer-service pivot instead, replace this ADR and PRD rather than trying to merge unrelated products.
