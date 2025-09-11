# Process Task List — Agent‑Ready Execution Playbook (Relaxed Mode)

> This is the **working document** stateless agents use to execute PRD → generate tasks → run. It mirrors PRD wiring but **disables performance gates** so you can iterate without bypasses. The goals: agents know **where to go**, **what tools exist**, and **how to execute** deterministically.

---

## 0) How to use this playbook
- Treat this as the source of truth for execution order, tools, and outputs.
- All long‑running commands must support `--json` and write a single JSON summary file.
- Use local providers for PRs; cloud providers are optional at night and still report‑only.

### 0.1 Bootstrap (strict order)
1. **Env** — `UV_PROJECT_ENVIRONMENT=.venv` (local) → `uv sync --extra dev`  |  `/opt/venv` (Docker/CI) → `uv sync --frozen`
2. **Profile guard** — `uv run python scripts/ci_verify_profiles.py`
3. **DB readiness** — `uv run python scripts/db_readiness_check.py`
4. **Provider smoke** — `uv run python scripts/provider_smoke.py --provider $EVAL_PROVIDER --model $MODEL --mode meta`
5. **Seed** — set `SEED` and keep it fixed for a given run
6. **Execute** — run the targets/commands below
7. **Provenance** — write `metrics/<run_id>.json`; exit non‑zero only on wiring errors
8. **Docs** — run doclets extract→render to update `400_*/` slots if behavior changed

### 0.2 One‑command targets (Makefile sketch)
```make
ENV_TARGET ?= local
ifeq ($(ENV_TARGET),linux)
  UV_ENV := /opt/venv
  UV_SYNC_FLAGS := --frozen
else
  UV_ENV := .venv
  UV_SYNC_FLAGS := --extra dev
endif

.PHONY: bootstrap go docs-render eval-gold eval-real
bootstrap:
    UV_PROJECT_ENVIRONMENT=$(UV_ENV) uv sync $(UV_SYNC_FLAGS)
    uv run python scripts/ci_verify_profiles.py
    uv run python scripts/db_readiness_check.py
    uv run python scripts/provider_smoke.py --provider $${EVAL_PROVIDER:-ollama} --model "$${OLLAMA_MODEL:-llama3.1:8b-instruct}" --mode meta

go: bootstrap
    uv run python scripts/ragchecker_official_evaluation.py --profile $${EVAL_PROFILE:-gold} --provider $${EVAL_PROVIDER:-ollama} --model "$${OLLAMA_MODEL:-llama3.1:8b-instruct}" --seed $${SEED:-42} --json > metrics/$${EVAL_PROFILE:-gold}.$${SEED:-42}.json

docs-render:
    uv run python scripts/extract_doclets.py --src src --out artifacts/doclets.json
    uv run python scripts/render_doclets.py --in artifacts/doclets.json --templates 000_core/templates --fragments-out artifacts/fragments

eval-gold:
    uv run python scripts/ragchecker_official_evaluation.py --profile gold --provider $${EVAL_PROVIDER:-ollama} --model "$${OLLAMA_MODEL:-llama3.1:8b-instruct}" --seed $${SEED:-42} --json > metrics/gold.$${SEED:-42}.json

eval-real:
    uv run python scripts/ragchecker_official_evaluation.py --profile real --provider $${EVAL_PROVIDER:-ollama} --model "$${OLLAMA_MODEL:-llama3.1:8b-instruct}" --seed $${SEED:-42} --json > metrics/real.$${SEED:-42}.json
```

### 0.3 Search‑first helpers
```bash
rg -n "EVAL_PROFILE|EVAL_PROVIDER|dataset_hash|artifact\.json" src/ scripts/ configs/
rg -n "create index .*hnsw|ivfflat|tsvector" scripts/ src/
```

---

## 1) Environments, Profiles, Providers

- **Dual envs**: `.venv` (local, `--extra dev`) and `/opt/venv` (Docker/CI, `--frozen`)
- **Profiles**: `real`, `gold`, `mock` (mock forbidden for mainline commands)
- **Providers**: `EVAL_PROVIDER={ollama|bedrock|openai|synthetic}` with model vars; local provider for PRs

---

## 2) Prerequisites (must pass before execution)
- Profile guard OK · DB readiness OK · Provider smoke OK · `SEED` pinned · `MAX_WORKERS=2..3` locally

---

## 3) Execution Order (TDD‑first)
1. Write tests (unit + property; minimal integration/smoke). Commit `[tests-first]`.
2. Implement to pass. Commit `[make-green]`.
3. Refactor; keep green. Commit `[refactor]`.
4. Run eval with `--json` → `metrics/` (report‑only).
5. Run `docs-render` if behavior changed; verify 400_ slots updated.

---

## 4) Automated Engine (optional)
```bash
uv run python scripts/solo_workflow.py execute --prd <prd_file> --auto-advance --seed ${SEED:-42}
```

---

## 5) Manual Flow
- Read PRD §1.3 + §2; pick provider/profile; set `SEED`
- Execute with `uv run ... --json > metrics/<run_id>.json`
- Update `.ai_state.json` (git‑ignored) with progress

---

## 6) Entry Points at a Glance (Where to Edit)
- **Gold data** → `evals/gold_cases.jsonl` / `datasets/dev_gold.jsonl` → `make eval-gold`
- **Retrieval** → `src/dspy_modules/retriever/*` (feature schema, scorers, fusion)
- **Reader** → `src/dspy_modules/reader/*` (typed contracts, tests)
- **DB** → migration + idempotent DDL; readiness script; transactional backfills
- **Provider** → `src/common/settings.py` + `configs/<profile>.env` (doclets + env table)
- **Artifacts** → Git LFS + `artifact.json`

---

## 7) Context Preservation
- Worklog tied to run IDs; persist `profile`, `provider`, `model`, `seed`, `dataset_hash`

---

## 8) Failure Ladder
1. Re‑run with `--json` + verbose logs
2. Check guard/readiness/smoke/seed
3. Reduce concurrency (`MAX_WORKERS=1`) and retry
4. Switch to local provider for PRs
5. File a small **HotFix** task; follow with refactor PR

---

## 9) Execution Sanity (**relaxed mode**)
- [ ] Commands run via `uv run` and complete without error
- [ ] `--json` summary written to `metrics/<run_id>.json` (PRD §10 schema)
- [ ] Provider smoke passes for declared provider/model
- [ ] DB readiness succeeded
- [ ] Logs include run ID, profile, provider, model, seed, dataset_hash
- [ ] Docs updated via doclets if behavior changed (400_ governance)

---

## 10) JSON Result Schema & Exit Codes (required)
- `0` success · `2` invalid config · `3` readiness failure · `5` unexpected error

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
  "metrics": {}
}
```

---

## 11) Outputs & Docs Governance
- **State**: `.ai_state.json` (git‑ignored)
- **Run summaries**: `metrics/` JSON (include `git_sha`, `profile`, `provider`, `model`, `seed`, `dataset_hash`)
- **Docs**: extract→render doclets; **no new guides**; update 400_ anchors/TOC

---

## 12) Determinism & Provenance
- Pin `SEED`; record in run JSON; record `dataset_hash` for every eval
- Git LFS for binaries; include `artifact.json` (`sha256`, `git_sha`, `profile`, `created_at`)

---

## 13) Concurrency & Resource Budgets
- Local default `MAX_WORKERS=2..3`; CI may raise this; document CPU/RAM for heavy steps

---

## 14) Security & Secrets
- No secrets in repo; `.env.local` git‑ignored; CI secrets for providers; DSN via resolver

---

## 15) QA one‑liners
```bash
uv run ruff check .
uv run black --check .
uv run basedpyright || uv run pyrigh
uv run pytest -q -m "unit or smoke"
```

---

## 16) Env knobs (reference)
`POSTGRES_DSN|DATABASE_URL`, `EVAL_PROFILE`, `EVAL_PROVIDER`, `OLLAMA_HOST`, `OLLAMA_MODEL`, `BEDROCK_MODEL_ID`, `AWS_REGION`, `OPENAI_MODEL`, `SEED`, `MAX_WORKERS`, `LOG_LEVEL`, `LOGFIRE_API_KEY`, `EVAL_ENFORCE=0`, `EVAL_REPORT_ONLY=1`
