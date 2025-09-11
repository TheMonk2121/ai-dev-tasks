# Generate Tasks — Agent‑Ready Template (Relaxed Mode)

> Use this to turn a PRD or backlog item into concrete tasks a stateless agent can execute. This focuses on **where to edit**, **which tools exist**, and **how to run**. Evaluation remains **report‑only** until gates are reinstated.

---

## 1. TL;DR (what / when / next)

| what | read when | do next |
|---|---|---|
| Standard workflow to convert PRD/backlog into tasks with reproducible commands | Before you create or update implementation tasks | 1) Read PRD §1.3 + §2; 2) TDD scaffold; 3) Fill Task Template; 4) Wire `--json` outputs; 5) Open PR |

## 0.9 Stateless Agent Checklist (do these in order)

1) Select env (local vs Docker) and sync (`uv sync`).
2) Read PRD §1.3 (stack) and §2 (profiles); set `EVAL_PROFILE`, `EVAL_PROVIDER`, `SEED`.
3) **Write tests first** (TDD): scaffold and commit `[tests-first]`.
4) Generate tasks (automation or manual) with acceptance criteria and wiring.
5) Add provider/model & repro commands (pin `--seed`; local provider for PRs).
6) If behavior will be documented, add `DOCLET:` blocks; plan `docs-render`.
7) Open PR; ensure required CI checks pass; iterate until green.

---

## 2. Current Status (meta)

- **Status**: ACTIVE — task generation workflow
- **Priority**: High leverage
- **Dependencies**: PRD (agent‑ready, relaxed mode)
- **Next Steps**: Prefer automation; otherwise use manual template below

### 2.7 Commit & PR Taxonomy (for agents)
- **[tests-first]** introduce failing tests (TDD Red)
- **[make-green]** minimal implementation to pass
- **[refactor]** behavior‑neutral cleanup
- **[docs]** doclets/400_ updates · **[infra]** CI/locks · **[hotfix]** urgent fix
PR titles: `<area>: <concise description>`; include Backlog/PRD references.

---

## 3. Workflow

### 3.4 TDD‑first steps (before implementation)

1) Generate test skeletons:
```bash
uv run python scripts/tdd_scaffold.py --module <src.module> --func <symbol>
```
2) Flesh out **unit** + **property** tests (fail intentionally).
3) Add any required **integration**/**smoke** tests (keep fast).
4) Commit with tag `[tests-first]`.
5) Only then implement code to make tests pass (`[make-green]`).

### 3.5 Provider selection and commands

```bash
# Local (preferred for PRs)
uv run python scripts/ragchecker_official_evaluation.py --profile gold --provider ollama --model "$OLLAMA_MODEL" --seed 42 --json > metrics/run.json

# Nightly (cloud provider allowed)
uv run python scripts/ragchecker_official_evaluation.py --profile gold --provider bedrock --model "$BEDROCK_MODEL_ID" --seed 42 --json > metrics/run.json
```

Tasks must declare: provider (`EVAL_PROVIDER`) + model id; seed used; repro cmd; expected cost/time if cloud.

### 3.6 Common Tasks → Where to Edi

- **(A) Add gold case(s)** → `evals/gold_cases.jsonl` / `datasets/dev_gold.jsonl`; run `make eval-gold`; commit `[tests-first]`.
- **(B) Tune retrieval scoring/fusion** → `src/dspy_modules/retriever/*`; add unit + property tests; run eval (report‑only).
- **(C) Reader tweak** → `src/dspy_modules/reader/*`; update Pydantic contracts; add reader tests; run eval (report‑only).
- **(D) Provider defaults/timeouts** → `src/common/settings.py` + `configs/<profile>.env`; doclets + env updates; provider smoke.
- **(E) DB change** → migration + readiness; idempotent DDL; transaction backfills; run readiness.
- **(F) Artifact** → produce with Git LFS; include `artifact.json` (`git_sha`, `dataset_hash`, `profile`, `created_at`, `sha256`).

### 3.4 Database‑aware tasks (requirements)

- Idempotent DDL (`IF NOT EXISTS`); transactional backfills.
- pgvector **≥ 0.8**; prefer **HNSW**, fallback **IVFFlat**; GIN on `content_tsv`.
- Use DSN resolver; do **not** read envs directly.
- Verify with `scripts/db_readiness_check.py` and capture summary.

---

## 4. Inputs & Context Resolution

- **Inputs**: PRD path or Backlog ID, profile (`real|gold|mock`), provider/model, seed.
- **Settings precedence**: Env → `configs/<profile>.env` → `.env.local` → defaults in `Settings`.
- **Common vars**: `POSTGRES_DSN|DATABASE_URL`, `EVAL_PROFILE`, `EVAL_PROVIDER`, `SEED`, `MAX_WORKERS`.

---

## 5. Task Template (copy per task)

```markdown
### [Task Name]
**Priority**: [Critical|High|Medium|Low]
**MoSCoW**: [Must|Should|Could|Won't]
**Estimate**: [X hours/days]
**Dependencies**: [Backlog/PRD refs, migrations, PRs]
**Profile(s)**: [real|gold|mock]
**Env/Settings touched**: [EVAL_PROFILE, EVAL_PROVIDER, POSTGRES_DSN, SEED, MAX_WORKERS, ...]
**Provider & model**: [bedrock|ollama|openai|synthetic] / [model id]
**Make target(s)**: [e.g., make eval-gold, make docs-render]
**Commands**:
- uv run python scripts/[...].py --profile [gold] --provider [ollama] --model [llama3.1:8b-instruct] --seed [42] --json > metrics/[run].json

**Description**
[Actionable description + the exact files/dirs to touch; reference PRD §1.3 + §2.]

**Acceptance Criteria**
- [ ] Commands support `--json` and write `metrics/<run_id>.json` (single object)
- [ ] Pydantic models validate inputs/outputs (no extra fields; strict types)
- [ ] Repro command(s) run on a fresh clone (via `uv run`)
- [ ] Provider smoke passes for the declared provider/model (local provider on PRs)
- [ ] Logs include run ID and evaluation ID; outputs stored with provenance

**Testing Requirements**
- [ ] Unit tests (core logic; mock I/O)
- [ ] Integration tests (Postgres/provider adapters as applicable)
- [ ] Property tests (Hypothesis) where invariants exis
- [ ] Smoke checks (db/provider readiness scripts)

**CI Gates (relaxed mode)**
- [ ] ruff + black --check via uv run
- [ ] basedpyright || pyright via uv run
- [ ] pytest (unit or smoke)
- [ ] eval run is **report‑only**: `--json` output saved to `metrics/`
- [ ] profile verifier (mock forbidden on main)
- [ ] artifact policy (Git LFS for binaries)

**Docs**
- [ ] README/guide deltas captured
- [ ] Task file cross‑links to PRD/backlog
- [ ] Changes folded into 400_ guides (no new guide .md); anchors updated; index/TOC refreshed
```

---

## 6. Enhanced Testing Methodology

- Lint: `uv run ruff check .` (pyupgrade enabled)
- Format: `uv run black --check .`
- Types: `uv run basedpyright || uv run pyright`
- Tests: `uv run pytest -q` (markers: unit, integration, smoke, e2e, property, slow, flaky)

### 6.2 Test Locations (conventions)
- Retriever → `tests/src/dspy_modules/retriever/test_*.py` (unit/property)
- Reader → `tests/src/dspy_modules/reader/test_*.py` (unit)
- DB readiness/indexing → `tests/scripts/test_db_readiness.py` (smoke/integration)
- Provider adapters → `tests/scripts/test_provider_smoke.py` (smoke)

---

## 7. MoSCoW Prioritization
Must · Should · Could · Won’t (text labels only)

---

## 8. Solo Developer Optimizations
One‑command runs; limited concurrency (`MAX_WORKERS=2..3`); context preservation in `.ai_state.json` (git‑ignored).

---

## 9. Output Locations & Formats
- Primary: `tasks/tasks-<id>.md` (this template).
- Optional: `tasks/tasks-<id>.json` for automation.
- Reports: `metrics/` as applicable.

### 11.1 Documentation governance (`400_` only)
- **No new guide .md**. Fold changes into existing `400_*/` docs using anchors.
- Update cross‑links and any 400_ index/TOC.
- Follow `200_naming_conventions`.
- For exceptions, open a docs‑governance issue; block merge until approved.

---

## 12. Reference Commands
```bash
uv sync
uv run pytest -q
uv run basedpyright || uv run pyrigh
uv run ruff check .
uv run black --check .
uv run python scripts/ragchecker_official_evaluation.py --profile gold --provider ollama --model "$OLLAMA_MODEL" --seed 42 --json > metrics/run.json
```
