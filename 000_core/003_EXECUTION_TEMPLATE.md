<!-- ANCHOR_KEY: process-task-list -->
<!-- ANCHOR_PRIORITY: 25 -->
<!-- ROLE_PINS: ["implementer", "planner"] -->

# Process Task List — Repo‑Aligned Template

> TL;DR
> - Drive a PRD/backlog task list to completion with uv-only one-command flows and CI-verifiable gates.
> - Rehydrate memory before execution; declare provider/profile/seed; prefer local providers for PR gates.
> - Respect evaluation standards: document seeds and dataset hashes for reproducibility.

This replaces ad‑hoc Python calls and emoji‑heavy formatting with the current stack: `uv` for envs/execution, `pydantic-settings` for configuration, Postgres (+pgvector; optional TimescaleDB), evaluation **profiles** (`real`/`gold`/`mock`), provider selection (Bedrock/Ollama/OpenAI/Synthetic), dual environments (local macOS vs Docker Linux), CI gates, deterministic seeds, artifact provenance, and 400_ documentation governance.

---

## 0) TL;DR (what / when / next)

### Mandatory first step (repo protocol)

```bash
export POSTGRES_DSN="mock://test"
uv run python scripts/unified_memory_orchestrator.py --systems ltst cursor go_cli prime --role planner "current project status and core documentation"
```

## 0.9 Bootstrap (one‑command)

Use a single Make target to prepare a clean machine for execution (scripts optional):

```make
bootstrap:
	UV_PROJECT_ENVIRONMENT=$(UV_ENV) uv sync $(UV_SYNC_FLAGS)
	# Optional readiness checks if present
	-uv run python scripts/ci_verify_profiles.py
	-uv run python scripts/db_readiness_check.py
	uv run python scripts/provider_smoke.py --provider $${EVAL_PROVIDER:-ollama} --model "$${OLLAMA_MODEL:-llama3.1:8b-instruct}" --mode meta
```

| what this file is | read when | do next |
|---|---|---|
| Standard execution workflow for taking a PRD/backlog task list to completion with one‑command flows, CI‑verifiable gates, and reproducibility | You’re ready to run tasks from a PRD/backlog item | 1) Pick env (local vs Docker); 2) Pick profile/provider; 3) Run the solo workflow or manual flow below |

---

## 1) Environments & Profiles

### 1.1 Dual environments (local macOS vs Docker Linux)

- **Local (macOS)**: `UV_PROJECT_ENVIRONMENT=.venv` (includes dev extras)  
- **Docker/CI (Linux)**: `UV_PROJECT_ENVIRONMENT=/opt/venv` (installs from `uv.lock` only)

```bash
# Local
export UV_PROJECT_ENVIRONMENT=.venv
uv sync --extra dev

# Docker/CI
export UV_PROJECT_ENVIRONMENT=/opt/venv
uv sync --frozen  # do not re-lock in CI
```

Optional Makefile switch:
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

### 1.2 Evaluation profiles

- **real** — full retrieval + reader over project data (production‑like)  
- **gold** — curated gold cases (gates and baselines)  
- **mock** — plumbing only; **forbidden on `main` gates**

Each profile has an env file in `configs/`: `real_rag_evaluation.env`, `repo_gold_evaluation.env`, `mock_evaluation.env`.

### 1.3 Provider selection (Bedrock/Ollama/OpenAI/Synthetic)

- Set `EVAL_PROVIDER={bedrock|ollama|openai|synthetic}` and the model variable (`BEDROCK_MODEL_ID`, `OLLAMA_MODEL`, or `OPENAI_MODEL`).
- **PR gates** run local (`ollama` or `synthetic`) for speed/cost determinism.  
- **Nightly** may use Bedrock/OpenAI to catch provider regressions.

Smoke before nightly cloud jobs:
```bash
uv run python scripts/provider_smoke.py --provider bedrock --model "$BEDROCK_MODEL_ID"  # default Haiku; Sonnet for tough cases
uv run python scripts/provider_smoke.py --provider ollama  --model "$OLLAMA_MODEL"
```

HTTP client guidance:
- Prefer `httpx` for provider checks and small HTTP calls; set explicit timeouts and `.raise_for_status()`.

---

## 2) Prerequisites (must pass before executing tasks)

- **DB readiness**: If available, run `uv run python scripts/db_readiness_check.py` (pgvector ≥ 0.8; required extensions; critical tables). Otherwise manually verify required extensions/tables.  
- **Settings load**: Use `pydantic-settings` via the repo `Settings` classes; **do not** read env vars directly.  
- **Seed & determinism**: set `SEED` and persist it in run summaries.  
- **Concurrency**: default `MAX_WORKERS=2..3` locally; CI may override.  
- **Profiles**: confirm `EVAL_PROFILE` and provider/model are set (and allowed).

---

## 3) Solo Developer Workflow (recommended)

Use the one‑command flows through `uv run`:

```bash
# Start (backlog intake → PRD → tasks → execution)
uv run python scripts/solo_workflow.py start "Enhanced backlog system with industry standards"

# Continue where you left off
uv run python scripts/solo_workflow.py continue

# Ship when done
uv run python scripts/solo_workflow.py ship
```

Suggested Make targets:
```make
solo-start:
	uv run python scripts/solo_workflow.py start "$(DESC)"
solo-continue:
	uv run python scripts/solo_workflow.py continue
solo-ship:
	uv run python scripts/solo_workflow.py ship
```

---

## 4) Automated Execution Engine (parameterized)

```bash
# Execute tasks from PRD with auto-advance
uv run python scripts/solo_workflow.py execute --prd <prd_file> --auto-advance --seed ${SEED:-42}

# Execute with smart pausing
uv run python scripts/solo_workflow.py execute --prd <prd_file> --smart-pause

# Execute with context preservation
uv run python scripts/solo_workflow.py execute --prd <prd_file> --context-preserve
```

**Environment knobs**
- `EVAL_PROFILE=[real|gold|mock]`
- `EVAL_PROVIDER=[ollama|bedrock|openai|synthetic]`
- `OLLAMA_HOST`, `OLLAMA_MODEL` | `BEDROCK_MODEL_ID`, `AWS_REGION` | `OPENAI_MODEL`
- `POSTGRES_DSN` | `DATABASE_URL`
- `SEED`, `MAX_WORKERS`

---

## 5) Manual Execution (fallback)

- Parse the PRD task list and plan sequence.  
- Use profile/provider‑aware commands (above) and capture results in run summaries.  
- Update progress in `.ai_state.json` (git‑ignored).  
- Apply the **Quality Gates** in Section 9 per task and cumulatively.

---

## 6) Execution Configuration (template)

```markdown
# Process Task List: [Project Name]

## Execution Configuration
- Auto-Advance: [yes/no]
- Pause Points: [critical decisions, deployments, user input]
- Context Preservation: LTST integration
- Smart Pausing: [rules]

## State Management
- State File: .ai_state.json (gitignored)
- Progress Tracking: [status]
- Session Continuity: [what is persisted]

## Error Handling
- HotFix Generation: [auto recovery]
- Retry Logic: [backoff]
- User Intervention: [when to pause]

## Execution Commands
```bash
uv run python scripts/solo_workflow.py start "description"
uv run python scripts/solo_workflow.py continue
uv run python scripts/solo_workflow.py ship
```
## Task Execution
[Reference tasks from PRD — no duplication]
```

---

## 7) Context Preservation

- **LTST memory**: maintain context across sessions using PRD Section 0 inputs.  
- **Scribe/worklog**: generate structured worklogs tied to run IDs.  
- **Metadata**: persist `profile`, `provider`, `model`, `seed`, `dataset_hash` per run.

---

## 8) Error Handling & Recovery

### 8.1 Failure Ladder (agent playbook)

If a step fails:
1) Re‑run with `--json` and increased logging.
2) Check readiness: DB, provider smoke, seeds.
3) Reduce concurrency (`MAX_WORKERS=1`) and retry.
4) Switch to local provider (Ollama) for PR gates.
5) File a HotFix task; apply minimal change to pass; follow with refactor PR.

1. Detect failure and root cause.  
2. Generate HotFix task(s) with explicit steps.  
3. Execute with retry/backoff and capture all logs.  
4. Validate fix; if successful, resume the main plan.  
5. Record provenance and outcomes in the run summary.

---

## 9) Quality Gates (task‑level and cumulative)

### Status block (copy)

```markdown
## Implementation Status
- Total Tasks: [X/Y]
- Current Phase: [Planning|Implementation|Testing|Deployment]
- Blockers: [list]

## Quality Gates
- [ ] Code review complete
- [ ] Tests passing (unit/integration)
- [ ] Documentation updated (400_ governance in effect)
- [ ] Performance validated (budget stated)
- [ ] Security reviewed
- [ ] Resilience tested (timeouts/retries/failover)
- [ ] Edge cases covered
- [ ] Eval gates met on gold profile (retrieval micro ≥ 0.85; macro ≥ 0.75; reader F1 ≥ 0.60 or waiver)
```

### Eval & provider gates (add to each relevant task)
- Retrieval micro ≥ 0.85; macro ≥ 0.75 on **gold**  
- Reader F1 ≥ 0.60 (or approved waiver)  
- Provider smoke passed for declared provider/model  
- Pydantic I/O validation succeeds (`extra='forbid'`)  
- Repro command works on fresh clone via `uv run` with the declared seed

---

## 10) PRD Structure → Execution Mapping

- Section 0 (Context/Patterns) → execution environment and commands  
- Sections 1–7 → problem, approach, risks, testing; verify alignment before running  
- Task list → execution plan; no duplication of content in this file

---

## 11) Output Locations & Formats

### 11.2 JSON Logging Standard

Every long‑running script MUST support `--json` and print a single JSON object (see PRD §4.5). Logs may stream to stdout/stderr, but the final line must be the JSON result.

- **State**: `.ai_state.json` (git‑ignored)  
- **Run summaries**: `metrics/` (include `git_sha`, `profile`, `provider`, `model`, `seed`, `dataset_hash`)  
- **Logs**: structured stdout + optional Logfire

### 11.1 Documentation governance (400_ only)
- **Do not create new guide .md**. Fold changes into existing `400_*/` docs using anchors.  
- Update cross‑links and any 400_ index/TOC.  
- Follow `200_naming_conventions`.  
- If a new guide seems necessary, open a **docs‑governance exception** issue; block merge until approved.

---

## 12) Determinism & Provenance

- Seeds pinned for PR gates; dataset hash recorded for each eval.  
- Any new artifacts (e.g., `*.pt`) must use Git LFS and ship an `artifact.json` with `sha256` and `git_sha`.  
- PR gates must use local provider; nightly jobs document cost/time for cloud providers.

---

## 13) Concurrency & Resource Budgets

- Local default `MAX_WORKERS=2..3`; CI may raise this.  
- Document CPU/RAM expectations for heavy steps (indexing, training, eval).

---

## 14) Security & Secrets

- No secrets in repo; use CI secrets and `.env.local` (git‑ignored).  
- Provider credentials gated behind provider smoke tests for nightly runs.  
- DB DSN resolved via the repo resolver; do not read env directly in tasks.

## 9.1 QA commands (one-liners)

```bash
# Lint with pyupgrade rules
uv run ruff check .

# Format check
uv run black --check .

# Type check (prefer basedpyright)
uv run basedpyright || uv run pyright

# Tests
uv run pytest -q -m "unit or smoke"
```

**Markers to use**
- unit, integration, smoke, e2e, property, slow, flaky

**Property-based tests**
- Use Hypothesis (`@given(...)`) for invariants and parsers/transforms.
- Load CI profile in `conftest.py` to keep PRs fast and deterministic.
