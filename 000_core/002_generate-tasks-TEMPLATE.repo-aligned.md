<!-- ANCHOR_KEY: generate-tasks -->
<!-- ANCHOR_PRIORITY: 25 -->
<!-- ROLE_PINS: ["planner", "implementer"] -->

# Generate Tasks — Repo‑Aligned Template

This replaces the legacy version that assumed ad‑hoc Python calls and emoji‑heavy formatting. It aligns with our current stack:
- `uv` for environments and execution
- `pydantic-settings` for typed configuration and layered env files
- Postgres (+pgvector; optional TimescaleDB) as the datastore
- Evaluation **profiles** (`real`, `gold`, `mock`) with Makefile entrypoints
- CI gates (ruff, pyright, pytest budgets, eval gates) and deterministic seeds
- Artifact provenance and Git LFS for large binaries

No emojis in work docs.

---

## 1. TL;DR (what / when / next)

| what this file is | read when | do next |
|---|---|---|
| Standard, reproducible workflow to convert a PRD or backlog item into tasks with CI‑ready acceptance criteria and gates | When you need to create or update implementation tasks tied to a PRD or backlog item | 1) Resolve context (PRD or Backlog ID); 2) Generate task list using the template or automation; 3) Apply MoSCoW prioritization; 4) Save to `tasks/` and open a PR |

## 0.9 Stateless Agent Checklist (do these in order)

1) Select env (local vs Docker) and sync (`uv sync`).
2) Read PRD §1.3 (stack) and §2 (profiles); set `EVAL_PROFILE`, `EVAL_PROVIDER`, `SEED`.
3) **Write tests first** (TDD): scaffold and commit `[tests-first]`.
4) Generate tasks (automation or manual) with acceptance criteria and gates.
5) Add provider/model & repro commands (pin `--seed`; prefer local provider for PRs).
6) If behavior will be documented, add `DOCLET:` blocks; plan `docs-render`.
7) Open PR; ensure required CI checks pass; iterate until green.

---

## 2. Current Status (meta)


- **Local** (macOS): `UV_PROJECT_ENVIRONMENT=.venv`, includes dev extras.
- **Docker/CI** (Linux): `UV_PROJECT_ENVIRONMENT=/opt/venv`, installs from `uv.lock` only.

**Commands**
```bash
# Local
export UV_PROJECT_ENVIRONMENT=.venv
uv sync --extra dev

# Docker/CI
export UV_PROJECT_ENVIRONMENT=/opt/venv
uv sync --frozen   # do not modify lockfile during CI images
```

Tasks that add/modify dependencies must state **where** they run (local vs Docker) and whether they require `--extra dev` or `--frozen` installs.


- **Status**: ACTIVE — task generation workflow
- **Priority**: Critical path componen
- **Points**: 4 (moderate complexity, high leverage)
- **Dependencies**: `000_core/001_create-prd.md` (repo‑aligned) or a valid backlog item
- **Next Steps**: Prefer automated generation via `uv run ...` if available; otherwise use the manual template below

---

### 2.4 Two environments (local vs Docker)

### 2.7 Commit & PR Taxonomy (for agents)

- **[tests-first]** introduce failing tests (TDD Red)
- **[make-green]** minimal implementation to pass
- **[refactor]** behavior-neutral cleanup
- **[docs]** doclets/400_ updates
- **[infra]** CI/locks
- **[hotfix]** urgent fix

PR titles: `<area>: <concise description>`; include Backlog/PRD references.
## 3. Workflow



### 3.4 TDD-first steps (before implementation)

1) Generate test skeletons:
```bash
uv run python scripts/tdd_scaffold.py --module <src.module> --func <symbol>
```
2) Flesh out **unit** + **property** tests (fail intentionally).
3) Add any required **integration**/**smoke** tests (keep fast).
4) Commit with tag `[tests-first]`.
5) Only then implement code to make tests pass (`[make-green]`).
### 3.5 Provider selection and commands

**Pick the provider per task** and include the command(s) to run it deterministically:

```bash
# Local (preferred for PR gates)
uv run python scripts/ragchecker_official_evaluation.py --profile gold --provider ollama --model "$OLLAMA_MODEL" --seed 42 --json > metrics/run.json --seed 42

# Nightly (cloud provider)
uv run python scripts/ragchecker_official_evaluation.py --profile gold --provider bedrock --model "$BEDROCK_MODEL_ID" --seed 42
```

Tasks must declare:
- Provider (`EVAL_PROVIDER`) and model id
- Seed used and how to override
- Expected cost/time (if cloud provider)
- Fallback path (ollama or synthetic) if provider not available


### 3.6 Common Tasks → Where to Edi

- **(A) Add gold case(s)** → `evals/gold_cases.jsonl` / `datasets/dev_gold.jsonl`; run `make eval-gold`; commit `[tests-first]`.
- **(B) Tune retrieval scoring/fusion** → `src/dspy_modules/retriever/*` (feature schema, scorers, fusion); add unit + property tests; run gold gates.
- **(C) Reader tweak** → `src/dspy_modules/reader/*`; update Pydantic contracts; add reader F1 tests; run gold gates.
- **(D) Provider defaults/timeouts** → `src/common/settings.py` + `configs/<profile>.env`; doclets + env table updates; provider smoke.
- **(E) DB change** → migration + readiness; idempotent DDL; transaction backfills; run readiness.
- **(F) Gate change** → update PRD §4.1 targets + CI; include rationale in task.
- **(G) Artifact** → produce with Git LFS; include `artifact.json` with `{git_sha, dataset_hash, profile, created_at, sha256}`.

### 3.4 Database-aware tasks (requirements)

**Before any DB-affecting task runs:**
- Ensure the correct env is selected (local vs Docker): set `UV_PROJECT_ENVIRONMENT` accordingly.
- Run `uv run python scripts/db_readiness_check.py` and capture its summary in the task output.

**When a task touches schema/indexes:**
- Use idempotent DDL patterns (`IF NOT EXISTS`, `CREATE OR REPLACE FUNCTION`).
- Target **pgvector ≥ 0.8**; prefer **HNSW** and fall back to **IVFFlat** if unavailable.
- If adding text search, ensure `content_tsv` + **GIN** index on `document_chunks`.
- Do **not** read env vars directly; use `common.db_dsn.resolve_dsn`.

**Accept/verify checklist (copy into the task):**
- [ ] `uv run python scripts/db_readiness_check.py` passes (extensions, tables, version checks)
- [ ] DDL is idempotent and safe on re-run
- [ ] Indexes created as specified (HNSW/IVFFlat, GIN for tsvector)
- [ ] DSN resolver in use for all DB code paths
- [ ] pg_stat_statements confirms expected query patterns before adding non-vector indexes


### 3.1 Automated Task Generation (preferred)

> If `scripts/task_generation_automation.py` is present, use it. Otherwise, skip to **3.2 Manual**.

```bash
# From a PRD file
uv run python scripts/task_generation_automation.py   --prd path/to/001_create-prd.md   --moscow text   --output-file tasks/tasks-<id>.md   --profile gold

# From a backlog ID
uv run python scripts/task_generation_automation.py   --backlog-id B-1045   --moscow text   --solo-optimized   --output-file tasks/tasks-B-1045.md
```

**Flags (contract):**
- `--moscow [text|none]` — use text labels `Must/Should/Could/Won't` (no emojis)
- `--profile [real|gold|mock]` — required for eval‑related tasks; `mock` is forbidden on `main`
- `--solo-optimized` — bundles related subtasks and ensures one‑command execution
- `--output-file <path>` — required; write to `tasks/` folder
- `--seed <int>` — if determinism matters for planned runs
- `--max-workers <int>` — default 2–3 for local; CI may override

**Make targets (recommended):**
```make
# Generate tasks from PRD
tasks-from-prd:
    uv run python scripts/task_generation_automation.py --prd $(PRD) --moscow text --output-file $(OUT) --profile $(PROFILE)

# Generate tasks from backlog
tasks-from-backlog:
    uv run python scripts/task_generation_automation.py --backlog-id $(ID) --moscow text --solo-optimized --output-file $(OUT)
```

### 3.2 Manual Task Generation (fallback)

1) Read PRD **Section 1.3 Current stack** and **Section 2 Profiles** (or use backlog metadata if PRD is skipped under house rules).
2) Fill the **Task Template** (Section 5) for each deliverable.
3) Apply **MoSCoW** priorities using text labels (no emojis).
4) Add **CI gates** and **acceptance criteria** that are directly verifiable.
5) Save to `tasks/tasks-<id>.md` and open a PR referencing the PRD/backlog.

### 3.3 PRD‑less path (allowed in narrow cases)

When a PRD is skipped (e.g., points < 5 **and** score_total ≥ 3.0), parse `000_core/000_backlog.md` and apply defaults from this guide. Explicitly record the skip and rationale at the top of the task file.

---

## 4. Inputs and Context Resolution

- **Inputs**: PRD path or Backlog ID (e.g., `B-1009`), optional profile (`real|gold|mock`), seed, and max workers.
- **Config precedence** (`pydantic-settings`):
  1. Environment variables (CI/shell)
  2. `configs/<profile>.env` (explicitly loaded)
  3. `.env.local` (git‑ignored)
  4. Defaults in `Settings` classes

- **Common vars** (documented in PRD, referenced here):
  - `POSTGRES_DSN=postgresql://user@localhost:5432/ai_agency`
  - `EVAL_PROFILE=gold`
  - `EVAL_DRIVER=dspy_rag|synthetic`
  - `RAGCHECKER_USE_REAL_RAG=1`
  - `SEED=42`
  - `MAX_WORKERS=3`

- **Profiles**:
  - `real` — full retrieval + reader; production‑like
  - `gold` — curated gold cases; used for gates/baselines
  - `mock` — plumbing only; never used on `main` for gating

---

## 5. Task Template (copy per task)

```markdown
### [Task Name]
**Priority**: [Critical|High|Medium|Low]
**MoSCoW**: [Must|Should|Could|Won't]
**Estimate**: [X hours/days]
**Dependencies**: [Backlog IDs, PRD sections, migrations, PRs]
**Profile(s)**: [real|gold|mock]
**Env/Settings touched**: [EVAL_PROFILE, EVAL_PROVIDER, POSTGRES_DSN, SEED, MAX_WORKERS, OLLAMA_HOST, OLLAMA_MODEL, BEDROCK_MODEL_ID, AWS_REGION, ...]
**Make target(s)**: [e.g., make eval-gold, make gen-index]
**Provider & model**: [bedrock|ollama|openai|synthetic] / [model id]
**Commands**:
- uv run python scripts/[...].py --profile [gold] --provider [ollama] --model [llama3.1:70b-instruct] --seed [42]

**Description**
[Actionable description with implementation guidance; reference PRD Section 1.3 + 2.]

**Acceptance Criteria**
- [ ] Verifiable outcome (include metric thresholds if relevant)
- [ ] Commands support `--json` and write `metrics/<run_id>.json` with run summary
- [ ] Pydantic models validate inputs/outputs (no extra fields, strict types); ValidationError fails the task
- [ ] Repro command(s) listed above execute successfully on a fresh clone
- [ ] Provider smoke test passes for the declared provider/model
- [ ] Logs include run ID and evaluation ID; outputs stored with provenance

**Testing Requirements**
- [ ] Unit tests (core logic; mock I/O)
- [ ] Integration tests (Postgres, retrieval/reader path as applicable)
- [ ] Performance checks (latency/throughput or resource budget)
- [ ] Security checks (input validation, secrets, auth if relevant)
- [ ] Resilience checks (timeouts, retries, error paths)
- [ ] Edge cases (boundary values, malformed inputs)

**CI Gates**
- [ ] ruff + black --check via uv run
- [ ] pyright via uv run
- [ ] pytest with budgets/markers
- [ ] eval gates on gold profile (retrieval micro ≥ 0.85; macro ≥ 0.75; reader F1 ≥ 0.60 or waiver)
- [ ] profile verifier (mock forbidden on main)
- [ ] artifact policy (no large binaries outside Git LFS)

**Observability**
- [ ] Structured logs with request/run IDs
- [ ] Metrics recorded (dataset hash, seed, profile)
- [ ] Alerts or dashboards updated if applicable

**Rollback / Feature Flag**
- [ ] Flag name: [FEATURE_X_ENABLED]
- [ ] Safe disable path documented

**Docs**
- [ ] README/guide deltas captured
- [ ] Task file cross‑links to PRD/backlog
- [ ] Changes folded into 400_ guides (no new guide .md); anchors updated; index/TOC refreshed
```

---

## 6. Enhanced Testing Methodology (standards)


### 6.1 QA hooks for tasks

- Lint: `uv run ruff check .` (pyupgrade enabled via `select = ["UP", ...]` in pyproject)
- Format: `uv run black --check .`
- Types: `uv run basedpyright || basedpyright || uv run pyright`
- Tests: `uv run pytest -q` (markers available: unit, integration, smoke, e2e, property, slow, flaky)
- Property tests: use Hypothesis; default profile loaded via `conftest.py`

**Acceptance Criteria additions**
- [ ] Ruff passes with `UP` (pyupgrade) rules enabled; no autofix diffs remain
- [ ] Black passes in `--check` mode
- [ ] basedpyright (or pyright) passes with `typeCheckingMode=strict`
- [ ] pytest suite passes required markers for this task; property tests added where appropriate


- **Unit**: isolate pure logic; mock I/O; exercise error paths.
- **Integration**: exercise Postgres + pgvector, reader/retriever flows as needed.
- **Performance**: define latency/throughput budgets and measure.
- **Security**: validate inputs, sanitize prompts/content, ensure secrets via CI env.
- **Resilience**: simulate network/DB errors; verify retries/backoff and graceful failure.
- **Edge**: large payloads, unusual characters, empty inputs, corrupted state.

Tests run via `uv run pytest -q`; type checks via `basedpyright || uv run pyright`.

---

## 7. MoSCoW Prioritization (text labels)

- **Must** — blocks delivery or gates; always executed firs
- **Should** — important value; follows Must items
- **Could** — optional improvements if time permits
- **Won't** — explicitly deferred; document reason

Dynamic reprioritization is allowed via backlog updates and CI signal (e.g., failures in gates).

---

## 8. Solo Developer Optimizations

- **Auto‑advance**: for non‑critical tasks only; critical items require manual confirm.
- **Context preservation**: cache inputs/decisions in task metadata; persist to `tasks/`.
- **One‑command**: each task declares a single command (Make + `uv run`) to execute the core action.
- **Limited concurrency**: default 2–3 workers locally; CI may increase. Control via `MAX_WORKERS`.

---

## 9. Enhanced Quality Gates Integration

Track overall progress and ensure gates are respected.

```markdown
## Implementation Status

### Progress
- Total tasks: [X] of [Y] complete
- Current phase: [Planning|Implementation|Testing|Deployment]
- Blockers: [list]

### Gates
- [ ] Code review complete
- [ ] Tests passing in CI
- [ ] Performance validated (budget: [...])
- [ ] Security reviewed
- [ ] Resilience verified
- [ ] Eval gates met on gold profile
- [ ] Docs updated
```

---

## 10. PRD → Tasks Mapping (reference)

- **PRD 1.3 (Current stack)** → task environment/commands/env vars
- **PRD 2 (Profiles)** → profile selection and gating
- **PRD DoD** → acceptance criteria and CI gates
- **PRD Data/Artifacts** → provenance and LFS policy

---

## 11. Output Locations and Formats


### 11.1 Documentation governance (400_ only)

- Do **not** create new guide .md files. Fold changes into existing `400_*/` docs using anchors.
- Update cross-links and any 400_ index/TOC doc.
- Follow `200_naming_conventions` (headings, code fences, file naming).
- If a new guide seems necessary, open a **docs-governance exception** issue and block merge until approved.


- Primary: `tasks/tasks-<id>.md` (this template).
- Optional: `tasks/tasks-<id>.json` for programmatic consumption.
- Reports: `metrics/` as applicable (test‑signal, eval summaries).

---

## 12. Reference Commands

```bash
# Environment sync and venv creation
uv sync

# Run tests and type checks
uv run pytest -q
basedpyright || uv run pyrigh

# Lint/forma
uv run ruff check .
uv run black --check .

# Run evaluation (gold profile; local)
uv run python scripts/ragchecker_official_evaluation.py --profile gold --provider ollama --model "$OLLAMA_MODEL" --seed 42 --json > metrics/run.json
```

---

## 13. Notes and Constraints

- Do not commit secrets; use CI secrets or `.env.local` (git‑ignored).
- Large binaries must use Git LFS and include provenance (`artifact.json`).
- `mock` profile is never acceptable for mainline evaluation gates.
- Prefer Make targets and `uv run` over direct `python`/`pip` calls.
