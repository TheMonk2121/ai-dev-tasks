# Product Requirements Document: B-1026 Closed‑Loop Lessons & Backlog Integration
<!-- parent_backlog: B-1026 -->

> Auto-Skip Note: Points ≥5; PRD required.

## 0. Context
- Build on B‑1025 to capture scratchpad/decisions/lessons, link to PRDs/backlog, and close the loop.

## 1. Problem
Reasoning and insights are lost; lessons don’t inform prioritization.

## 2. Solution
- Proxy (FastAPI) in front of local models; log OpenAI‑compatible JSON with masking
- Cursor Rules: require `<scratchpad>` for local models; store structured thought
- DB: runs, steps, artifacts (light); lessons, decisions tables; link edges to PRDs/backlog
- Importers to suggest backlog candidates tagged lesson‑derived
- Flags: FEATURE_PROXY_LOGS, FEATURE_SCRATCHPAD, FEATURE_LESSONS (default off)

## 3. Acceptance
- Coverage: ≥95% local requests logged; ≥80% runs include scratchpad
- Knowledge: ≥20 lessons, ≥10 decisions linked; ≥5 backlog candidates auto‑suggested
- Latency: no change to B‑1025 when flags off; ≤ +50ms p50 when on (local only)
- Queries: PRD→lessons; backlog item→supporting lessons

## 4. Technical Approach
- Middleware forwarding with redact; schema creation; importers; linkers; views
- Keep vendor observability optional (Langfuse/Phoenix)

## 5. Risks
- PII → strict masks + tests
- Bloat → rotation + summarization

## 6. Tests
- Logging coverage
- Link integrity
- Importer suggestions

## 7. Plan
1) Flags & contracts
2) Proxy & logging
3) Minimal schema
4) Cursor rules & emission
5) Backlog integration
6) Evaluation & accept

## Rollback
- Flags off → capture disabled; tables inert; retrieval unaffected
