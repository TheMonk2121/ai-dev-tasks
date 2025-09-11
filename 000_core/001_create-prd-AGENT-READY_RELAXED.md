# Product Requirements Document (PRD) — Evaluation & RAG System (Agent‑Ready, **Relaxed Mode**)

> **Relaxed Mode:** evaluation runs are **report‑only**. No performance thresholds or regressions are enforced until you decide to enable gates. This PRD focuses on *where to go, what tools to use, and how to execute deterministically* so a stateless agent can work end‑to‑end without tribal knowledge.

---

## 0) How to use this template

- Keep it concise but **never omit wiring or provenance** (JSON outputs, seeds, paths).
- Everything in **Definition of Done** must be objectively verifiable (but not performance‑gated).
- Copy to your feature folder as `001_create-prd.md`, fill bracketed fields, and commit.

### 0.1 Stateless Agent Bootstrap (non‑interactive contract)

1. **Environment** — set `UV_PROJECT_ENVIRONMENT` (local: `.venv`; docker/CI: `/opt/venv`) and run:
   - Local: `uv sync --extra dev`
   - Docker/CI: `uv sync --frozen`
2. **Profile guard** — `uv run python scripts/ci_verify_profiles.py` (fail if `mock` used for mainline commands).
3. **DB readiness** — `uv run python scripts/db_readiness_check.py` (pgvector/version/extensions/tables).
4. **Provider smoke** — `uv run python scripts/provider_smoke.py --provider $EVAL_PROVIDER --model $MODEL --mode meta`.
5. **Determinism** — set `SEED` and persist it in run summaries.
6. **Execute** — use Make targets or the explicit `uv run` commands defined in this PRD.
7. **Provenance** — write a single JSON summary to `metrics/` per §4.5; **do not** fail on metrics in relaxed mode.
8. **Docs** — if behavior changed, run doclets extract→render to fold content into `400_*/` slots (no new guides).

---

## 1) Context & Goals

### 1.1 Why this change
[Problem/Objective. E.g., “Make evals reproducible, typed, and observable while we iterate on quality.”]

### 1.2 Target outcomes (no gates yet)
- Deterministic, single‑command runs with JSON results.
- Agents know exactly **where to edit** and **which scripts** to use.
- Zero “it worked locally” failures: seeds, readiness, and smoke tests are mandatory.

### 1.3 Current stack (authoritative)
- **Runtime**: Python 3.12 (`pyproject.toml` + `uv.lock`)
- **Env**: `uv` for sync/run; Make targets as single entry surface
- **Config**: `pydantic-settings` + layered `.env` files; typed `Settings`
- **RAG/Evals**: DSPy programs, PydanticAI, Pydantic Evals, custom harness
- **Data store**: Postgres (pgvector installed; Timescale optional)
- **Indexing**: Hybrid BM25 + vector; entity‑aware retrieval
- **Logs/Obs**: Pydantic Logfire (optional) + structured stdou
- **QA**: pytest (+ markers), Hypothesis, Ruff (pyupgrade), Black, (based)Pyrigh
- **CI**: GitHub Actions (qa, profile guard, readiness checks, doclets, **eval report‑only**)

### 1.4 Entry Points (Agent Cheat Sheet)
- **Gold data** → `evals/gold_cases.jsonl` / `datasets/dev_gold.jsonl`; validate; run eval with `--json`.
- **Retrieval** → `src/dspy_modules/retriever/*` (feature schema, scorers, fusion); add unit + property tests.
- **Reader** → `src/dspy_modules/reader/*`; update typed contracts; add reader tests (report‑only for now).
- **DB schema/index** → migration + `scripts/db_readiness_check.py`; idempotent DDL; transactional backfills.
- **Provider defaults/timeouts** → `src/common/settings.py` + `configs/<profile>.env`; doclets + env tables.
- **Artifacts** → Git LFS + `artifact.json` (sha256, dataset_hash, git_sha).

> **Search‑first rule**: grep existing patterns before adding code/envs.

### 1.5 Dev Guidelines (RAG/Evals)
- **Typed boundaries**: Pydantic v2 (`extra='forbid'`); treat `ValidationError` as a CI hard‑fail.
- **Idempotent DB**: `CREATE/ALTER/INDEX IF NOT EXISTS`; transaction‑wrap multi‑write backfills.
- **Avoid N+1**: batch queries; add indexes only with pg_stat_statements evidence.
- **Provider safety**: PRs use local provider (Ollama/synthetic); cloud only in nightly (still report‑only).
- **Determinism**: seed `random`, `numpy`, `torch` (if present); record `SEED` & `dataset_hash`.
- **Docs**: comment doclets → slots in `400_*/`; **no new guides**.

---

## 2) Environments & Profiles

### 2.1 Profiles
- **real** — full retrieval + reader (production‑like)
- **gold** — curated gold cases (baselines/report)
- **mock** — plumbing only (**forbidden** on mainline commands)
Env files in `configs/`: `real_rag_evaluation.env`, `repo_gold_evaluation.env`, `mock_evaluation.env`

### 2.2 Settings precedence (`pydantic-settings`)
1) Env vars (CI/shell) → 2) `configs/<profile>.env` → 3) `.env.local` (git‑ignored) → 4) defaults in `Settings`

### 2.3 `uv` usage
- First‑time: `uv sync` (local `--extra dev`, Docker/CI `--frozen`)
- Execute with `uv run <cmd>` (never bare `python` in docs/CI)

### 2.4 Dual environments
- **Local**: `UV_PROJECT_ENVIRONMENT=.venv` (with dev extras)
- **Docker/CI**: `UV_PROJECT_ENVIRONMENT=/opt/venv` (install from lockfile)

### 2.5 Providers
- `EVAL_PROVIDER={bedrock|ollama|openai|synthetic}`
- Models: `BEDROCK_MODEL_ID` | `OLLAMA_MODEL`/`OLLAMA_HOST` | `OPENAI_MODEL`
- Log `provider`, `model_id`, `seed` (and token usage if available)

### 2.6 Doc governance (`400_`)
- **No new guides**; fold content into existing `400_*/` using anchors (`ANCHOR_KEY`, etc.).
- Update cross‑links and any index/TOC; follow `200_naming_conventions`.

### 2.7 Comment‑Driven Doclets
- Add `DOCLET:` blocks in code; run extract→render (see `000_core/025_comment-doclets.md`).

---

## 3) Data, Schemas, Artifacts

### 3.1 Postgres
- Extensions: `vector` (pgvector **≥ 0.8**), `pg_trgm`, `pg_stat_statements`
- DDL rules: idempotent (`IF NOT EXISTS`); transactional backfills
- Readiness: `uv run python scripts/db_readiness_check.py`

**Specifics**
- Critical tables: `conversation_sessions`, `conversation_messages`, `conversation_context`, `user_preferences`, `memory_retrieval_cache`, `session_relationships`, `memory_performance_metrics`, legacy: `documents`, `document_chunks`, `conversation_memory`
- Indexes:
  - `document_chunks.content_tsv` (tsvector) + **GIN**
  - `conversation_memory.embedding` vector index — prefer **HNSW**, fallback **IVFFlat**
- DSN: prefer `DATABASE_URL`, fallback `POSTGRES_DSN` via resolver

### 3.2 Datasets & gold cases
- `evals/gold_cases.jsonl` + `datasets/dev_gold.jsonl`; compute `dataset_hash` each run

### 3.3 Artifacts
- Use **Git LFS** for binaries; ship `artifact.json` with `{git_sha, dataset_hash, profile, created_at, sha256}`

---

## 4) CI/CD (relaxed mode)

### 4.1 Required PR jobs
- **profile‑guard** (no `mock` for mainline commands)
- **db‑readiness** (pgvector/version/extensions/tables)
- **qa‑ruff** (`uv run ruff check .` with pyupgrade)
- **qa‑black** (`uv run black --check .`)
- **qa‑types** (`uv run basedpyright || uv run pyright` strict)
- **qa‑tests** (`uv run pytest -q -m "unit or smoke"`)
- **eval‑report** (run eval with `--json`, save to `metrics/`, **report‑only**)
- **doclets‑fresh** (extract/render; fail only on drift/missing slots)

### 4.2 Nightly jobs (optional, report‑only)
- Cloud provider smoke (inference mode)
- Full eval with pinned seed(s); produce JSON deltas (**no gating**)

### 4.3 QA Tooling (configs)

**Ruff**
```toml
[tool.ruff]
line-length = 100
target-version = "py312"
select = ["E","F","UP","I","B"]
fix = true

[tool.ruff.lint.isort]
known-first-party = ["src"]
```

**Black**
```toml
[tool.black]
line-length = 100
target-version = ["py312"]
```

**(based)Pyright**
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

**pytest + markers**
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
markers = [
  "unit", "integration", "smoke", "e2e", "property", "slow", "flaky"
]
```

### 4.5 JSON Result Schema & Exit Codes (required)

All long‑running scripts MUST support `--json` and print **one** JSON object to stdout. Exit codes:
- `0` success · `2` invalid config · `3` readiness failure · `5` unexpected error
*(No gate code in relaxed mode.)*

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
    "retrieval_micro": 0.0,
    "retrieval_macro": 0.0,
    "reader_f1": 0.0
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
- `make dev-up` · `make eval-gold` · `make eval-real` · `make ci-verify-profiles` · `make test` · `make docs-render`

### 5.3 Concurrency
- Local default `MAX_WORKERS=2..3`; CI may override

### 5.4 Determinism & Seeding
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

### 5.5 Commit & PR taxonomy
- **[tests-first]** → **[make-green]** → **[refactor]** · **[docs]** · **[infra]** · **[hotfix]**

---

## 6) Definition of Done (**relaxed mode**)

1. CI checks pass: lint, format, types, tests, profile verifier, DB readiness, doclets fresh.
2. An eval run completes and writes a valid `--json` summary to `metrics/` (no thresholds enforced).
3. A fresh clone can reproduce the run with one command (e.g., `uv sync && make eval-gold`).

### 6.1 TDD‑first plan
- Write tests **before implementation** (unit + property; minimal integration/smoke). Commit `[tests-first]` → `[make-green]` → `[refactor]`.

---

## 7) Non‑Functional Requirements (high‑level)
- Reliability: timeouts/retries/backoff; circuit breakers where applicable
- Scalability: index size, DB growth, storage budgets
- Resource: CPU/RAM budgets in CI and on a dev Mac
- Dev UX: single‑command flows; clear error messages

### 7.6 Edge Cases
- Empty/very long queries; Unicode/markdown/code blocks
- Zero contexts; missing embeddings; dimension mismatch
- Provider timeouts/rate limits/unavailable models
- Dataset drift (id mismatch, stale globs, path casing)
- Partial re‑index; stale `tsvector`
- Seed unset; nondeterminism; over‑parallelism
- DDL locks; migration races

---

## 8) Risks & Mitigations
- Drift between local and CI → `uv run` everywhere; profile verifier
- Docs drift → doclets extract→render with CI freshness check
- Provider/network flakiness → local provider on PR; optional nightly smoke

---

## 9) Open Questions
- Do we need Timescale hypertables for this feature?
- Should new settings extend existing `Settings`, or live in a new module?
- When to re‑enable eval gates (and with what datasets/seeds)?

---

## 10) Appendix: Commands

- **Sync & venv**: `uv sync`
- **Eval (gold)**: `uv run python scripts/ragchecker_official_evaluation.py --profile gold --provider ollama --model "$OLLAMA_MODEL" --seed 42 --json > metrics/gold.42.json`
- **Tests/Types**: `uv run pytest -q` · `uv run basedpyright || uv run pyright`
- **Lint/Format**: `uv run ruff check .` · `uv run black --check .`
- **Doclets**: `uv run python scripts/extract_doclets.py && uv run python scripts/render_doclets.py`

### 10.1 Search‑first helpers
```bash
rg -n "EVAL_PROFILE|EVAL_PROVIDER|dataset_hash|artifact\.json" src/ scripts/ configs/
rg -n "create index .*hnsw|ivfflat|tsvector" scripts/ src/
```

---

## 11) Appendix: Environment variables

| Name               | Example/Default                               | Description                                      |
|--------------------|-----------------------------------------------|--------------------------------------------------|
| DATABASE_URL       | postgresql://user@localhost:5432/ai_agency    | Preferred DSN env                                |
| POSTGRES_DSN       | postgresql://user@localhost:5432/ai_agency    | Fallback DSN env                                 |
| EVAL_PROFILE       | gold                                          | real, gold, mock                                 |
| EVAL_PROVIDER      | ollama                                        | bedrock, ollama, openai, synthetic               |
| BEDROCK_MODEL_ID   | anthropic.claude-3-5-sonnet-20240620-v1:0     | Bedrock model                                    |
| AWS_REGION         | us-east-1                                     | Region for Bedrock                               |
| OLLAMA_HOST        | http://localhost:11434                        | Ollama server URL                                |
| OLLAMA_MODEL       | llama3.1:8b-instruct                          | Ollama model                                     |
| OPENAI_MODEL       | gpt-4o-mini                                   | OpenAI model                                     |
| SEED               | 42                                            | Seed for determinism                             |
| MAX_WORKERS        | 3                                             | Concurrency cap for local runs                   |
| LOG_LEVEL          | INFO                                          | Logging level                                    |
| LOGFIRE_API_KEY    | (set in CI)                                   | Pydantic Logfire key (optional)                  |
| EVAL_ENFORCE       | 0                                             | 0 = relaxed (report‑only), future = gated        |
| EVAL_REPORT_ONLY   | 1                                             | Alias for relaxed mode                           |

---

## 12) Appendix: File/Folder expectations

- `src/` · `scripts/` · `configs/` · `evals/` · `datasets/` · `tests/` · `metrics/` · `Makefile`
