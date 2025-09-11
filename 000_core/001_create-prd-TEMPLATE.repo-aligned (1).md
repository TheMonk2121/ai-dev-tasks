# Product Requirements Document (PRD) — Evaluation & RAG System (Repo‑Aligned Template)

This template replaces legacy assumptions (Poetry, ad‑hoc envs, generic “RAGChecker 0.1.9” notes) with the current toolchain and workflow. Use it for any feature touching retrieval, reader programs, evaluation harnesses, or data/metrics.

---

## 0) How to use this template

- Keep it short where you can, but do not omit required gates.
- Everything under **Definition of Done** must be objectively verifiable in CI.
- Copy this file into the feature’s folder as `001_create-prd.md` and fill every bracketed placeholder.
- No emojis or marketing language; this is an engineering artifact.

---

## 1) Context and Goals

### 1.1 Why this change
[Concise statement of the problem the feature solves, tied to retrieval/reader/eval pain points.]

### 1.2 Target outcomes
- Primary metric to move: [e.g., Reader F1 on gold cases from 0.50 → 0.60].
- Guardrail metrics: [e.g., Retrieval micro ≥ 0.85; macro ≥ 0.75; latency p95 ≤ 800 ms].
- Operational goals: [e.g., deterministic runs, single‑command repro, artifact provenance].

### 1.3 Current stack (authoritative)
- **Language/Runtime**: Python [3.12.x] pinned via `pyproject.toml` and `uv.lock`.
- **Env/Packaging**: `uv` for sync, lock, and execution (`uv sync`, `uv run`). No Poetry.
- **Config**: `pydantic-settings` with layered `.env` files and typed `Settings` classes.
- **RAG/Evals**: DSPy programs, PydanticAI, Pydantic Evals, plus the repo’s evaluation harness.
- **Data store**: Postgres (pgvector installed). Optional: TimescaleDB for time‑series metrics.
- **Indexing**: Hybrid BM25 + vector; entity‑aware retrieval (as applicable).
- **Logging/Telemetry**: Pydantic Logfire + structured logs to stdout.
- **QA Tooling**: pytest (+ markers), Ruff, Black, Pyright, pre‑commit.
- **CI/CD**: GitHub Actions with required checks (lint, type‑check, tests, eval gates, nightly jobs).
- **Task runner**: Makefile targets as the single entry surface for local and CI flows.

Link to repo root and relevant modules: [path/to/src/...], [path/to/scripts/...].

---

## 2) Operating Environments and Profiles




### 2.6 Documentation governance (400_ only)

**Policy:** This project does **not** create new Markdown “guides.” All guide content must be **folded into existing docs under `400_*/`**.
- Prefer updating canonical 400_ docs with **anchors** (`<!-- ANCHOR_KEY: ... -->`, `<!-- ANCHOR_PRIORITY: ... -->`, `<!-- ROLE_PINS: [...] -->`) rather than adding files.
- Cross-link updated sections and update any 400_ index/TOC doc.
- Follow `200_naming_conventions` for headings, code fences, and file naming.

**Exceptions:** If a brand-new guide seems unavoidable, open a “docs-governance exception” issue that includes:
- rationale, proposed filename/path, and how it fits into the 400_ structure;
- a deprecation or merge plan for overlapping docs.
No new guide .md merges without an approved exception.

**DoD hooks:** The PR must show the 400_ doc diffs and link to the exact anchor(s) modified.


### 2.5 LLM providers & evaluation runtime

We support multiple providers and require explicit selection per run:

- **Providers**: `EVAL_PROVIDER={bedrock|ollama|openai|synthetic}`
- **Models**:
  - Bedrock: `BEDROCK_MODEL_ID` (e.g., `anthropic.claude-3-5-sonnet-20240620-v1:0`)
  - Ollama: `OLLAMA_MODEL` (e.g., `llama3.1:70b-instruct`) and `OLLAMA_HOST` (default `http://localhost:11434`)
  - OpenAI: `OPENAI_MODEL` (e.g., `gpt-4o-mini`)
  - Synthetic: no external calls; for plumbing and unit tests

**Gating policy**
- **PR eval gates (gold)** must run on **local** (`ollama` or `synthetic`) to avoid external cost/latency flake.
- **Nightly** may additionally run Bedrock/OpenAI to catch provider regressions.
- All runs must log `provider`, `model_id`, `seed`, and token usage if available.

**Examples**
```bash
# Local gold eval (Ollama)
uv run python scripts/ragchecker_official_evaluation.py --profile gold --provider ollama --model "$OLLAMA_MODEL"

# Nightly gold eval (Bedrock)
uv run python scripts/ragchecker_official_evaluation.py --profile gold --provider bedrock --model "$BEDROCK_MODEL_ID"
```


### 2.4 Dual environments (local macOS vs. Linux in Docker)

We support two project virtual environments:
- **Local (macOS)** for day‑to‑day dev and full tooling (extras=`dev`).
- **Linux (Docker)** for dependency resolution/runtime parity; CI uses this too.

**Authoritative env location** is controlled by `UV_PROJECT_ENVIRONMENT`:
- Local: `UV_PROJECT_ENVIRONMENT=.venv`
- Docker: `UV_PROJECT_ENVIRONMENT=/opt/venv`

> `UV_PROJECT_ENVIRONMENT` sets the venv path uv uses for the project. If the env doesn'tt exist, uv creates it.  See uv docs.

**Lock discipline**
- Local dev may run `uv lock` and commit `uv.lock` only when intentionally upgrading.
- Docker/CI must _not_ re‑lock. Use `uv sync --frozen` to install exactly from `uv.lock`.

**Local setup**
```bash
# macOS
export UV_PROJECT_ENVIRONMENT=.venv
uv sync --extra dev
```

**Dockerfile sketch**
```dockerfile
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:${PATH}"
# Install uv as you prefer (e.g., curl | sh)
# RUN curl -LsSf https://astral.sh/uv/install.sh | sh
RUN uv sync --frozen  # install from uv.lock without re-locking
```

**Platform‑specific deps (example)**
Use PEP‑508 markers in `pyproject.toml` when a package differs by platform:
```toml
[project]
dependencies = [
  "psycopg[binary]>=3.2 ; sys_platform != 'linux'",
  "psycopg[c]>=3.2     ; sys_platform == 'linux'",
]
```

**Makefile selector (optional)**
```make
ENV_TARGET ?= local
ifeq ($(ENV_TARGET),linux)
  UV_ENV := /opt/venv
  UV_SYNC_FLAGS := --frozen
else
  UV_ENV := .venv
  UV_SYNC_FLAGS := --extra dev
endif

.PHONY: sync
sync:
    UV_PROJECT_ENVIRONMENT=$(UV_ENV) uv sync $(UV_SYNC_FLAGS)
```


### 2.1 Runtime profiles (evaluation)
- **real** — runs full retrieval + reader over project data with production‑like settings.
- **gold** — runs on curated gold cases; used for baselines and gates.
- **mock** — synthetic tests for plumbing and CI speed; must never run on `main`.

Each profile has a dedicated env file under `configs/`:
- `configs/real_rag_evaluation.env`
- `configs/repo_gold_evaluation.env`
- `configs/mock_evaluation.env`

### 2.2 Settings precedence (pydantic‑settings)
1. Environment variables (CI and shell)
2. `configs/<profile>.env` (loaded explicitly)
3. `.env.local` (developer overrides; git‑ignored)
4. Defaults in `Settings` classes

Explicitly list the settings your feature uses and the safe defaults:
- `POSTGRES_DSN=postgresql://[user]@localhost:5432/[db]`
- `EVAL_PROFILE=[real|gold|mock]`
- `EVAL_DRIVER=[dspy_rag|synthetic]`
- `RAGCHECKER_USE_REAL_RAG=[0|1]`
- `SEED=[int]`
- `[YOUR_FEATURE_FLAG]=[value]`

### 2.3 Environment creation and execution (uv)
- First‑time setup: `uv sync` (resolves and locks deps; creates project venv).
- Run anything: `uv run <cmd>` — CI and local should both use `uv run`.
- Useful variables:
  - `UV_PROJECT_ENVIRONMENT=.venv` to keep env local to repo.
  - `UV_LINK_MODE=copy` on macOS to avoid symlink oddities (optional).
- Don’t reference `python` directly in docs or scripts; always `uv run python ...`.

---

## 3) Data, Schemas, and Artifacts



### 3.2.1 Pydantic contracts for eval flows

All eval I/O is typed with Pydantic v2 models. Minimum contracts:

```python
from pydantic import BaseModel, ConfigDic
from typing import List, Optional

class GoldCase(BaseModel):
    model_config = ConfigDict(extra='forbid', validate_default=True, str_strip_whitespace=True)
    id: str
    query: str
    expected_files: List[str]
    tags: List[str] = []
    category: Optional[str] = None
    gt_answer: Optional[str] = None  # when reader F1 is evaluated

class EvalRunSummary(BaseModel):
    profile: str  # real|gold|mock
    provider: str  # bedrock|ollama|openai|synthetic
    model_id: str
    seed: in
    dataset_hash: str
    retrieval_micro: floa
    retrieval_macro: floa
    reader_f1: float | None = None
```

**Rules**
- `extra='forbid'` to catch accidental fields; treat `ValidationError` as a **hard fail** in CI.
- Dataset readers must validate each case on load and emit a deterministic `dataset_hash`.
- Feature vectors for learned fusion must use typed models (shape/len asserted) before training or scoring.


### 3.1.1 Database specifics (aligned to current repo)

**Required extensions (minimums):**
- `vector` (pgvector) **≥ 0.8** — required for production; HNSW supported from ≥ 0.5, but repo targets 0.8+.
- `pg_trgm` — recommended for text similarity (tsvector support).
- `pg_stat_statements` — required for performance visibility.

**Critical tables (must exist):**
`conversation_sessions`, `conversation_messages`, `conversation_context`, `user_preferences`, `memory_retrieval_cache`, `session_relationships`, `memory_performance_metrics`, plus legacy: `documents`, `document_chunks`, `conversation_memory`.

**Indexes / columns:**
- `document_chunks.content_tsv` (tsvector), with **GIN** index for text search.
- `conversation_memory.embedding` vector index — **HNSW** preferred; fallback to **IVFFlat** if HNSW unavailable.
- Add JSONB/BTREE indexes only when query patterns justify (pg_stat_statements evidence).

**DSN and resolver:**
- Prefer `DATABASE_URL`; fallback to `POSTGRES_DSN` via `common.db_dsn.resolve_dsn`. Tasks must not read env vars directly—use the resolver.

**Readiness check (PR gate):**
- CI must run: `uv run python scripts/db_readiness_check.py`
  Fails if required extensions/tables missing, or pgvector < 0.8.

**DDL rules (idempotent):**
- `CREATE TABLE IF NOT EXISTS ...`
- `ALTER TABLE ... ADD COLUMN IF NOT EXISTS ...`
- `CREATE INDEX IF NOT EXISTS ...`
- `CREATE OR REPLACE FUNCTION ...`

**Repro commands:**
```bash
# Verify DB extensions and critical tables
uv run python scripts/db_readiness_check.py

# Example: ensure tsvector column + GIN index (idempotent pattern)
psql "$POSTGRES_DSN" -v ON_ERROR_STOP=1 <<'SQL'
ALTER TABLE document_chunks
  ADD COLUMN IF NOT EXISTS content_tsv tsvector;

CREATE INDEX IF NOT EXISTS idx_document_chunks_content_tsv
  ON document_chunks USING GIN (content_tsv);

-- Optional: populate/update tsvector (tune config to your language needs)
UPDATE document_chunks
SET content_tsv = to_tsvector('english', coalesce(raw_text, ''))
WHERE content_tsv IS NULL;
SQL

# Example: HNSW index (fallback to IVFFlat when needed)
psql "$POSTGRES_DSN" -v ON_ERROR_STOP=1 <<'SQL'
-- Preferred
CREATE INDEX IF NOT EXISTS idx_conversation_memory_embedding_hnsw
ON conversation_memory USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Fallback
CREATE INDEX IF NOT EXISTS idx_conversation_memory_embedding_ivffla
ON conversation_memory USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
SQL
```


### 3.1 Postgres
- Required extensions: `pgvector` [and `timescaledb` if using hypertables].
- Migrations: [link to migration scripts or tool].
- Tables touched/added by this feature: [list], including field types and indexes.
- Determinism: ensure `created_at`, `updated_at`, and `version` fields exist where relevant.

### 3.2 Datasets and gold cases
- Curated gold lives under: `evals/gold_cases.jsonl` and `datasets/dev_gold.jsonl`.
- Every eval run computes and stores a dataset hash and run metadata (git SHA, profile, seed).
- Any learned model must record the dataset hash used for training.

### 3.3 Model and run artifacts
- Large artifacts (e.g., `*.pt`, `*.bin`) must use Git LFS or external releases.
- Each artifact must ship with a provenance file (`artifact.json`) containing:
  - `git_sha`, `dataset_hash`, `profile`, `created_at`, `sha256`.

---

## 4) CI/CD and Required Checks



### 4.4 QA Tooling policy (lint, format, types, tests)

**Ruff (lint)**
- Enforced via CI and local: `uv run ruff check .`
- `pyupgrade` ruleset enabled (Ruff code `UP`) to modernize Python syntax automatically.
- Suggested base config (pyproject):
```toml
[tool.ruff]
line-length = 100
target-version = "py312"
select = ["E","F","UP","I","B"]  # pycodestyle, pyflakes, pyupgrade, isort, flake8-bugbear
fix = true

[tool.ruff.lint.isort]
known-first-party = ["src"]
```

**Black (format)**
- Enforced via CI as `uv run black --check .`.
```toml
[tool.black]
line-length = 100
target-version = ["py312"]
```

**Type checking ((based)Pyright)**
- Preferred: **basedpyright** (drop-in, faster; stricter typing). Fallback: **pyright**.
- CI step should run whichever is present:
  - `uv run basedpyright || uv run pyright`
- Suggested base config:
```toml
[tool.basedpyright]
typeCheckingMode = "strict"
pythonVersion = "3.12"
reportMissingTypeStubs = false
venvPath = "."
venv = ".venv"
# pragma: allow gradual typing in tests
ignore = ["tests/**/fixtures/**"]

# If using pyright instead of basedpyright:
[tool.pyright]
typeCheckingMode = "strict"
pythonVersion = "3.12"
venvPath = "."
venv = ".venv"
```

**pytest & Hypothesis**
- Unit + integration tests via pytest; property-based tests via Hypothesis.
- Standard markers and budgets are enforced; slow/flaky isolated.
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
markers = [
  "unit: fast-running tests with no external I/O",
  "integration: DB, network, or multi-component paths",
  "smoke: minimal end-to-end confidence checks",
  "e2e: full system behavior (rare on PRs)",
  "property: Hypothesis-based property tests",
  "slow: long-running tests (nightly only)",
  "flaky: unstable tests (quarantined)",
]
```

**Hypothesis defaults (recommended)**
Include these in `conftest.py` or a shared fixture:
```python
from hypothesis import settings, HealthCheck

settings.register_profile(
    "ci",
    max_examples=100,
    deadline=500,  # ms
    suppress_health_check=[HealthCheck.too_slow],
)
settings.load_profile("ci")
```

**Test taxonomy**
- **unit**: pure logic, no external I/O; run on PRs.
- **integration**: DB or external service; run on PRs if fast, otherwise nightly.
- **smoke**: thin end-to-end path (e.g., provider/db readiness); always run on PRs.
- **property**: Hypothesis properties for core invariants; run on PRs with limited examples.
- **e2e**: full system flows; generally nightly.


### 4.3 Provider smoke tests (required)

Before any PR eval gate runs:
- If `EVAL_PROVIDER=bedrock`, run a provider smoke test that makes a minimal inference call and fails fast on credentials/region/model errors.
- If `EVAL_PROVIDER=ollama`, verify model availability via `/api/tags` or a one-token prompt.
- OpenAI similar: verify API key scope and model availability.

**Commands**
```bash
# Generic smoke script (example)
uv run python scripts/provider_smoke.py --provider bedrock --model "$BEDROCK_MODEL_ID"
uv run python scripts/provider_smoke.py --provider ollama  --model "$OLLAMA_MODEL"
```
Make the smoke test **non-blocking** for PRs (since PR gates use local providers), but **blocking** for nightly cloud-provider jobs.


### 4.1 Required jobs on pull requests
- Lint: `ruff` and `black --check` via `uv run`.
- Type check: `pyright` via `uv run`.
- Tests: `pytest -q` with markers and budgets enforced.
- Eval gates (gold profile only): retrieval micro ≥ [0.85], macro ≥ [0.75]; reader F1 ≥ [0.60] or explicit waiver.
- Profile verifier: fails PR if `mock` profile is used on `main` or in required gates.
- Artifact policy: blocks if large binaries are committed outside Git LFS allowlist.

### 4.2 Nightly/scheduled jobs (non‑blocking on PRs)
- Test‑signal collection and triage queue update.
- Quarantine/retirement automation per budgets and sentinels.
- Evaluation baseline refresh with pinned seeds; deltas reported to a dashboard or summary artifact.

---

## 5) Local Developmen

### 5.1 One‑time setup
- Install Postgres and enable required extensions.
- `uv sync`
- Create `.env.local` with developer DSN and safe defaults.

### 5.2 Useful Make targets (examples)
- `make dev-up` — run migrations, sanity checks.
- `make eval-gold` — `uv run python scripts/ragchecker_official_evaluation.py --profile gold`.
- `make eval-real` — run full pipeline against project data.
- `make ci-verify-profiles` — ensure environment/profile configuration is valid.
- `make test` — run test suite with budgets and markers.

### 5.3 Determinism and seeds
- All evaluation and training scripts accept `--seed` and default to `SEED` from settings.
- CI pins a seed; local runs may override but must record the value in the run summary.

### 5.4 Concurrency
- Default limited concurrency for CPU‑bound steps (2–3 workers) to keep local runs stable.
- Provide a single env knob: `MAX_WORKERS=[2..4]` and document expected impact.

---

## 6) Definition of Done (gates must be green)

1. CI required checks all pass (lint, types, tests, profile verifier).
2. Eval gates meet targets on gold profile:
   - Retrieval micro ≥ [0.85]; macro ≥ [0.75].
   - Reader F1 ≥ [0.60] or an approved waiver with justification.
3. Reproducible run: one command reproduces headline numbers on a fresh clone:
   - `uv sync && make eval-gold` produces the PR’s reported metrics within ±0.5%.
4. Artifacts: if new models were added, provenance file present and Git LFS policy respected.
5. Docs updated: this PRD, `README` quickstart deltas, env/profile tables, **and 400_ guides** (no new guide .md; anchors updated; index/TOC refreshed).
6. Observability: logs include request IDs and evaluation IDs; Logfire fields appear in CI output.
7. Security: no secrets or sensitive files in repo; `.env.local` git‑ignored; CI uses encrypted secrets.

---

## 7) Non‑Functional Requirements

- **Performance**: [state throughput/latency goals and test method].
- **Reliability**: [retries, timeouts, backoff, circuit breakers if any].
- **Scalability**: [index size targets, DB growth, storage budgets].
- **Resource usage**: [CPU/RAM budget in CI and on a dev Mac].
- **Accessibility/Developer UX**: single‑command flows; clear failure modes and messages.

---

## 8) Risks and Mitigations

- Risk: metric regression due to mislabeled gold. Mitigation: gold review gate before merge.
- Risk: non‑deterministic evals. Mitigation: seeded runs, pinned deps, dataset hash logging.
- Risk: artifact bloat. Mitigation: Git LFS and CI enforcement.
- Risk: env drift between local and CI. Mitigation: `uv run` everywhere and profile verifier.

---

## 9) Open Questions

- Do we need Timescale hypertables for this feature’s metrics, or is Postgres tables + indexes sufficient?
- Should the new settings live in an existing `Settings` class or a new module?
- Are eval targets realistic given current retrieval ceiling? Provide a dry‑run report.

---

## 10) Appendix: Reference commands

- Sync and create venv:
  `uv sync`
- Run evals (gold profile):
  `uv run python scripts/ragchecker_official_evaluation.py --profile gold`
- Run tests and type checks:
  `uv run pytest -q`
  `uv run pyright`
- Lint/format:
  `uv run ruff check .`
  `uv run black --check .`

---

## 11) Appendix: Environment variables (document the ones you use)

| Name                         | Example/Default                                  | Description                                         |
|------------------------------|--------------------------------------------------|-----------------------------------------------------|
| POSTGRES_DSN                 | postgresql://user@localhost:5432/ai_agency       | Primary DB connection                               |
| EVAL_PROFILE                 | gold                                             | Eval mode: real, gold, mock                         |
| EVAL_DRIVER                  | dspy_rag                                         | Underlying driver: dspy_rag or synthetic            |
| RAGCHECKER_USE_REAL_RAG      | 1                                                | Forces real RAG path in eval harness                |
| SEED                         | 42                                               | Seed for determinism                                |
| MAX_WORKERS                  | 3                                                | Concurrency cap for local runs                      |
| LOG_LEVEL                    | INFO                                             | Logging level                                       |
| LOGFIRE_API_KEY              | [set in CI]                                      | Pydantic Logfire key (if used)                      |
| OPENAI_API_KEY               | [set in CI/local]                                | If applicable                                       |
| AWS_*                        | [set in CI]                                      | If using Bedrock or S3                              |
| AWS_REGION                   | us-east-1                                        | Required for Bedrock                                |
| EVAL_PROVIDER                | ollama                                           | Provider: bedrock, ollama, openai, synthetic        |
| BEDROCK_MODEL_ID             | anthropic.claude-3-5-sonnet-20240620-v1:0       | Bedrock model identifier                            |
| OLLAMA_HOST                  | http://localhost:11434                           | Ollama server URL                                   |
| OLLAMA_MODEL                 | llama3.1:70b-instruct                            | Ollama model name                                   |
| OPENAI_MODEL                 | gpt-4o-mini                                      | OpenAI model name                                   |
| BEDROCK_MAX_TOKENS           | 1024                                             | Optional generation cap                             |
| BEDROCK_TEMPERATURE          | 0.2                                              | Optional temperature                                |

---

## 12) Appendix: File/Folder expectations (update if you add/rename)

- `src/` contains importable modules (reader, retriever, settings, utils).
- `scripts/` contains CLI entrypoints; all runnable via `uv run`.
- `configs/` holds profile env files.
- `evals/` and `datasets/` hold gold and dev cases.
- `tests/` with markers and budgets; `metrics/` for reports.
- `Makefile` is the single entry surface for common flows.
