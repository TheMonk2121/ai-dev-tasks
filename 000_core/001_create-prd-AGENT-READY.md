# Product Requirements Document (PRD) — Evaluation & RAG System (Repo‑Aligned, Agent‑Ready)

> This PRD replaces prior versions. It encodes our run‑of‑record for retrieval/reader/evals so a **stateless agent** can implement end‑to‑end without tribal knowledge.

---

## 0) How to use this template

- Keep it concise but **never omit gates** or provenance.
- Everything under **Definition of Done** must be objectively verifiable in CI.
- Copy to your feature folder as `001_create-prd.md`, fill bracketed fields, and commit.

### 0.1 Stateless Agent Bootstrap Contrac

A stateless agent **MUST** be able to ship this PRD from scratch by following these steps strictly and non‑interactively:

1. **Environment** — set `UV_PROJECT_ENVIRONMENT` (local: `.venv`, docker: `/opt/venv`), then `uv sync` (local: `--extra dev`; CI/Docker: `--frozen`).
2. **Profile guard** — `uv run python scripts/ci_verify_profiles.py` (fail if `mock` used for gates).
3. **DB readiness** — `uv run python scripts/db_readiness_check.py` (extensions/version/tables).
4. **Provider smoke** — `uv run python scripts/provider_smoke.py --provider $EVAL_PROVIDER --model $MODEL --mode meta`.
5. **Determinism** — set `SEED`, persist it in the run summary.
6. **Execute** — use Make targets / explicit `uv run` commands defined here.
7. **Provenance** — write JSON to `metrics/` per §4.5; non‑zero exit on failure.
8. **Docs** — if behavior changed, run the **doclets pipeline** to fold content into `400_*/` slots (no new guides).

---

## 1) Context and Goals

### 1.1 Why this change
[Problem/Objective. E.g., “Improve reader F1 on gold cases; stabilize gates in CI; codify artifact policy.”]

### 1.2 Target outcomes
- Primary metric: **Reader F1 on gold** [from X → Y].
- Guardrails: **Retrieval micro ≥ 0.85**, **macro ≥ 0.75**, **latency p95 ≤ 800 ms**.
- Operational: single‑command repro; JSON result; dataset hashing; provenance.

### 1.3 Current stack (authoritative)
- **Runtime**: Python 3.12 (pinned via `pyproject.toml` + `uv.lock`)
- **Env**: `uv` for sync/run; Make targets as single entry surface
- **Config**: `pydantic-settings` + layered `.env` files; typed `Settings`
- **RAG/Evals**: DSPy programs, PydanticAI, Pydantic Evals, custom eval harness
- **Data store**: Postgres (pgvector installed; Timescale optional)
- **Indexing**: Hybrid BM25 + vector; entity‑aware retrieval
- **Logs/Obs**: Pydantic Logfire (optional) + structured stdou
- **QA**: pytest (+ markers), Hypothesis, Ruff (with `pyupgrade`), Black, (based)Pyrigh
- **CI**: GitHub Actions (qa, eval gates, profile guard, readiness checks, doclets)

### 1.4 Entry Points (Agent Cheat Sheet)
- **Gold cases** → edit `evals/gold_cases.jsonl` / `datasets/dev_gold.jsonl`; validate with Pydantic; re‑run gates.
- **Retrieval features/fusion** → `src/dspy_modules/retriever/*` (feature schema, scorers, fusion); add unit + property tests; run gold gates.
- **Reader program** → `src/dspy_modules/reader/*`; update typed contracts; add reader F1 tests.
- **DB schema/index** → migration script + `scripts/db_readiness_check.py`; idempotent DDL; transaction‑wrapped backfills.
- **Provider/timeouts** → `src/common/settings.py` + `configs/<profile>.env`; doclets + env table updates.
- **Eval thresholds** → §4.1 + CI; update dataset hash in summary JSON.
- **Artifacts** → Git LFS + `artifact.json` (sha256, dataset_hash, git_sha).

> **Search‑first rule**: prefer existing patterns; **do not** invent new envs or folders without updating `Settings` and env tables.

### 1.5 Key Development Guidelines (RAG/Evals)
- **Typed boundaries**: Pydantic v2 models (`extra='forbid'`); treat `ValidationError` as CI‑hard‑fail.
- **Idempotent DB**: `CREATE/ALTER/INDEX IF NOT EXISTS`; transaction for multi‑write backfills.
- **Avoid N+1**: batch queries; index with **evidence** (pg_stat_statements).
- **Provider safety**: PR gates use local provider (Ollama/synthetic); cloud in nightly only with budgets.
- **Determinism**: seed `random`, `numpy`, `torch` (if present); record `SEED` & `dataset_hash`.
- **Docs**: comment doclets + slot updates in `400_*/`; **no new guides**.

---

## 2) Operating Environments and Profiles

### 2.1 Runtime profiles (evaluation)
- **real** — full retrieval + reader (production‑like)
- **gold** — curated gold cases (baselines/gates)
- **mock** — plumbing only (**forbidden** on mainline gates)

Each profile has an env file in `configs/`:
`real_rag_evaluation.env`, `repo_gold_evaluation.env`, `mock_evaluation.env`

### 2.2 Settings precedence (`pydantic-settings`)
1. Environment variables (CI/shell)
2. `configs/<profile>.env` (explicitly loaded)
3. `.env.local` (git‑ignored)
4. Defaults in `Settings` classes

### 2.3 Environment creation & execution (`uv`)
- First‑time: `uv sync` (local `--extra dev`; Docker/CI `--frozen`)
- Always run via `uv run <cmd>` (never bare `python` in docs/CI)

### 2.4 Dual environments (local macOS vs Docker Linux)
- **Local**: `UV_PROJECT_ENVIRONMENT=.venv` (with dev extras)
- **Docker/CI**: `UV_PROJECT_ENVIRONMENT=/opt/venv` (install from lockfile)

### 2.5 LLM providers & evaluation runtime
- `EVAL_PROVIDER={bedrock|ollama|openai|synthetic}`
- Models: `BEDROCK_MODEL_ID` | `OLLAMA_MODEL`/`OLLAMA_HOST` | `OPENAI_MODEL`
- **PR gates**: local provider only; **Nightly** adds cloud runs
- All runs log `provider`, `model_id`, `seed`, token usage (if available)

### 2.6 Documentation governance (`400_` only)
- **No new guide .md files**. Fold content into existing `400_*/` docs using anchors (`ANCHOR_KEY`, etc.).
- Update cross‑links and any 400_ index/TOC. Follow `200_naming_conventions`.
- For exceptions, open a docs‑governance issue; block until approved.

### 2.7 Cross‑Link: Comment‑Driven Doclets
- Add `DOCLET:` blocks in code; run extract→render to update 400_ slots. See `000_core/025_comment-doclets.md`.

---

## 3) Data, Schemas, and Artifacts

### 3.1 Postgres
- Required extensions: `vector` (pgvector **≥ 0.8**), `pg_trgm` (text similarity), `pg_stat_statements` (evidence)
- Migrations: idempotent DDL; safe retry; transactional backfills

#### 3.1.1 Database specifics
- **Critical tables**: `conversation_sessions`, `conversation_messages`, `conversation_context`, `user_preferences`, `memory_retrieval_cache`, `session_relationships`, `memory_performance_metrics`, legacy: `documents`, `document_chunks`, `conversation_memory`
- **Indexes/columns**:
  - `document_chunks.content_tsv` (tsvector) + **GIN** index
  - `conversation_memory.embedding` vector index — prefer **HNSW**, fallback **IVFFlat**
  - JSONB/BTREE only with query‑evidence
- **DSN**: prefer `DATABASE_URL`, fallback `POSTGRES_DSN` via resolver; tasks do **not** read envs directly
- **Readiness**: `uv run python scripts/db_readiness_check.py` (PR gate)

### 3.2 Datasets and gold cases
- Curated gold under `evals/gold_cases.jsonl` + `datasets/dev_gold.jsonl`
- Each run computes a dataset hash and stores run metadata (`git_sha`, `profile`, `seed`)

### 3.3 Model & run artifacts
- Commit large binaries via **Git LFS** only
- Every artifact must include `artifact.json` with `{git_sha, dataset_hash, profile, created_at, sha256}`

---

## 4) CI/CD and Required Checks

### 4.1 Required PR jobs (names may vary, but behavior is mandatory)
- **profile-guard**: fails if `mock` used for gates
- **db-readiness**: pgvector/version/extensions/tables ok
- **qa-ruff**: `uv run ruff check .` (with pyupgrade)
- **qa-black**: `uv run black --check .`
- **qa-types**: `uv run basedpyright || uv run pyright` (strict)
- **qa-tests**: `uv run pytest -q -m "unit or smoke"` (+ any fast integration)
- **eval-gates**: gold profile only → retrieval micro ≥ 0.85, macro ≥ 0.75; reader F1 ≥ 0.60 (or waiver)
- **doclets-fresh**: extract/render; fail on drift/missing slots

### 4.2 Nightly jobs (non‑blocking on PRs)
- Test‑signal collection & triage
- Provider smoke (cloud) in **inference** mode
- Eval baselines with pinned seeds; delta repor

### 4.3 Provider smoke tests (required)
- `provider_smoke.py` must pass for declared provider/model. PRs run **local** provider; nightly runs cloud.

### 4.4 QA Tooling policy (lint, format, types, tests)

**Ruff (lint)** — `uv run ruff check .` (enable `UP` / pyupgrade)
```toml
[tool.ruff]
line-length = 100
target-version = "py312"
select = ["E","F","UP","I","B"]
fix = true

[tool.ruff.lint.isort]
known-first-party = ["src"]
```

**Black (format)** — `uv run black --check .`
```toml
[tool.black]
line-length = 100
target-version = ["py312"]
```

**Type checking ((based)Pyright)** — `uv run basedpyright || uv run pyright`
```toml
[tool.basedpyright]
typeCheckingMode = "strict"
pythonVersion = "3.12"
venvPath = "."
venv = ".venv"
ignore = ["tests/**/fixtures/**"]

[tool.pyright]
typeCheckingMode = "strict"
pythonVersion = "3.12"
venvPath = "."
venv = ".venv"
```

**pytest & Hypothesis**
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
markers = [
  "unit: fast-running tests with no external I/O",
  "integration: DB, network, or multi-component paths",
  "smoke: minimal end-to-end confidence checks",
  "e2e: full system behavior (nightly)",
  "property: Hypothesis-based property tests",
  "slow: long-running tests (nightly only)",
  "flaky: unstable tests (quarantined)",
]
```

**Hypothesis CI defaults**
```python
from hypothesis import settings, HealthCheck
settings.register_profile("ci", max_examples=100, deadline=500, suppress_health_check=[HealthCheck.too_slow])
settings.load_profile("ci")
```

### 4.5 JSON Result Schema & Exit Codes (required)

All long‑running scripts MUST support `--json` and print one JSON object. Exit codes:
- `0` success | `2` invalid config | `3` readiness failure | `4` gate failure | `5` unexpected error

```json
{
  "run_id": "uuid",
  "git_sha": "string",
  "profile": "gold",
  "provider": "ollama",
  "model_id": "llama3.1:8b-instruct",
  "seed": 42,
  "dataset_hash": "sha256",
  "started_at": "2025-09-10T19:20:30Z",
  "finished_at": "2025-09-10T19:21:00Z",
  "status": "success",
  "error": null,
  "metrics": {
    "retrieval_micro": 0.88,
    "retrieval_macro": 0.81,
    "reader_f1": 0.61
  }
}
```

---

## 5) Local Developmen

### 5.1 One‑time setup
- Install Postgres + required extensions
- `uv sync` (local with dev extras; Docker/CI frozen)
- Create `.env.local` (git‑ignored) with developer DSN and defaults

### 5.2 Useful Make targets (examples)
- `make dev-up` — migrations + sanity checks
- `make eval-gold` — `uv run python scripts/ragchecker_official_evaluation.py --profile gold`
- `make eval-real` — real pipeline on project data
- `make ci-verify-profiles` — validate environment/profile configuration
- `make test` — run pytest with budgets/markers
- `make docs-render` — doclets extract→render→verify

### 5.3 Concurrency
Default local `MAX_WORKERS=2..3` (limited for stability); CI may override.

### 5.4 Determinism & Seeding
See §5.5. All scripts accept `--seed` and default to `SEED` setting; CI pins a seed.

### 5.5 Randomness & Seeding (standard)
```python
import os, random, numpy as np
SEED = int(os.getenv("SEED", "42"))
random.seed(SEED); np.random.seed(SEED)
try:
    import torch
    torch.manual_seed(SEED); torch.cuda.manual_seed_all(SEED)
    torch.use_deterministic_algorithms(True)
except Exception:
    pass
```

### 5.6 Commit & PR Taxonomy (for agents)
- **[tests-first]** failing tests (TDD Red) → **[make-green]** minimal impl → **[refactor]** behavior‑neutral
- **[docs]** doclets or 400_ updates (no new guides) | **[infra]** CI/locks | **[hotfix]** urgent fix

---

## 6) Definition of Done (gates must be green)

1. CI required checks pass: lint, format, types, tests, profile verifier, DB readiness, doclets fresh.
2. Eval gates on **gold** meet targets: retrieval micro ≥ 0.85; macro ≥ 0.75; reader F1 ≥ 0.60 (or waiver).
3. Reproducible run on fresh clone: `uv sync && make eval-gold` → metrics within ±0.5%.
4. Artifacts via Git LFS with `artifact.json` (sha256, dataset_hash, git_sha).
5. **Docs updated**: this PRD, README deltas, env/profile tables, and **400_ guides** (no new guides; anchors updated; index/TOC refreshed).
6. Observability: logs include run ID and evaluation ID; Logfire fields present if enabled.
7. Security: no secrets in repo; `.env.local` git‑ignored; CI secrets used.

### 6.1 TDD‑first plan (mandatory)
- Write tests **before implementation**: unit + property + minimal integration/smoke where applicable.
- DoD additions: PR includes a `[tests-first]` commit; `ci-require-tests` passes (unless `ALLOW_NO_TESTS=1` with justification).

---

## 7) Non‑Functional Requirements

- **Performance**: throughput/latency goals + test plan.
- **Reliability**: timeouts/retries/backoff; circuit breakers if applicable.
- **Scalability**: index size, DB growth, storage budgets.
- **Resource**: CPU/RAM budgets in CI and on a dev Mac.
- **Dev UX**: single‑command flows; clear failures.

### 7.6 Edge Cases to Consider (RAG/Evals)
- Empty/very long queries; Unicode/code/markdown.
- Zero contexts; missing embeddings; dim mismatch.
- Provider timeouts/rate limits/unavailable models.
- Dataset drift: id mismatch; stale globs; path casing.
- Index churn: partial re‑index; stale `tsvector`.
- Seed unset; nondeterministic reductions; over‑parallelism.
- DB migration races; DDL locks.

---

## 8) Risks and Mitigations

- Miss‑labeled gold → strict gold review gate before merge.
- Non‑deterministic evals → pinned seeds; dataset hash logging.
- Artifact bloat → Git LFS + CI enforcement.
- Env drift → `uv run` everywhere; profile verifier.
- Provider/Network flakiness → local provider for PR; nightly checks for cloud.

---

## 9) Open Questions

- Do we need Timescale hypertables for this feature, or are plain tables sufficient?
- Should new settings extend an existing `Settings` class or create a new module?
- Are the targets realistic given current retrieval ceiling? Provide a dry‑run report.

---

## 10) Appendix: Reference commands

- **Sync & venv**: `uv sync`
- **Eval (gold profile)**: `uv run python scripts/ragchecker_official_evaluation.py --profile gold`
- **Tests/Types**: `uv run pytest -q` · `uv run basedpyright || uv run pyright`
- **Lint/Format**: `uv run ruff check .` · `uv run black --check .`
- **Doclets**: `uv run python scripts/extract_doclets.py && uv run python scripts/render_doclets.py`

### 10.1 Search‑First commands
```bash
rg -n "EVAL_PROFILE|EVAL_PROVIDER|dataset_hash|artifact\.json" src/ scripts/ configs/
rg -n "create index .*hnsw|ivfflat|tsvector" scripts/ src/
```

---

## 11) Appendix: Environment variables (document the ones you use)

| Name                         | Example/Default                                  | Description                                         |
|------------------------------|--------------------------------------------------|-----------------------------------------------------|
| POSTGRES_DSN                 | postgresql://user@localhost:5432/ai_agency       | Primary DB DSN (prefer `DATABASE_URL` when present) |
| DATABASE_URL                 | postgresql://user@localhost:5432/ai_agency       | Preferred DSN env                                   |
| EVAL_PROFILE                 | gold                                             | Eval mode: real, gold, mock                         |
| EVAL_PROVIDER                | ollama                                           | Provider: bedrock, ollama, openai, synthetic        |
| BEDROCK_MODEL_ID             | anthropic.claude-3-5-sonnet-20240620-v1:0       | Bedrock model identifier                            |
| AWS_REGION                   | us-east-1                                        | Required for Bedrock                                |
| OLLAMA_HOST                  | http://localhost:11434                           | Ollama server URL                                   |
| OLLAMA_MODEL                 | llama3.1:70b-instruct                            | Ollama model name                                   |
| OPENAI_MODEL                 | gpt-4o-mini                                      | OpenAI model name                                   |
| RAGCHECKER_USE_REAL_RAG      | 1                                                | Force real RAG path in eval harness                 |
| SEED                         | 42                                               | Seed for determinism                                |
| MAX_WORKERS                  | 3                                                | Concurrency cap for local runs                      |
| LOG_LEVEL                    | INFO                                             | Logging level                                       |
| LOGFIRE_API_KEY              | [set in CI]                                      | Pydantic Logfire key (optional)                     |

---

## 12) Appendix: File/Folder expectations

- `src/` — importable modules (reader, retriever, settings, utils)
- `scripts/` — CLI entrypoints; always run via `uv run`
- `configs/` — profile env files
- `evals/` / `datasets/` — gold/dev cases
- `tests/` — unit/property/integration/smoke; `metrics/` for reports
- `Makefile` — single entry surface for common flows
