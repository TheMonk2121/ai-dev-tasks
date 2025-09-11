# Task List: B-1070 Database Optimization & Resource Isolation for Evaluation Performance

## Overview
Optimize PostgreSQL for a 128 GB local macOS system and isolate workloads so RAGChecker evaluations complete in <5 minutes without interfering LTST jobs, while protecting the red-line baseline (precision ≥ 0.159, recall ≥ 0.166, F1 ≥ 0.159). This task list follows the PRD `PRD-B-1070-Database-Optimization-Resource-Isolation-Evaluation-Performance.md` and uses the enhanced generation workflow defined in `000_core/002_generate-tasks-TEMPLATE.md`.

## MoSCoW Prioritization Summary
- **🔥 Must Have**: 10 tasks – Canonical DSN, discovery snapshots, healthcheck, Stage A tuning, baseline validation, per-role GUCs, eval cache isolation, vector query-time policy, monitoring views, documentation updates
- **🎯 Should Have**: 6 tasks – Stage B/C tuning, JSON artifacts automation, LTST concurrency guard, selective indexes (evidence-driven), auto snapshots pre/post eval, eval timing dashboards
- **⚡ Could Have**: 4 tasks – Optional PgBouncer feasibility check, RAM-disk cache experiment, archive split plan, minimal EXPLAIN harness
- **⏸️ Won't Have**: 2 tasks – Full PgBouncer deployment, cache UNLOGGED/LZ4 conversions (until metrics justify)

## Solo Developer Quick Star
```bash
# Run healthcheck and discovery snapshots
python3 scripts/healthcheck_db.py &&
python3 scripts/pg_settings_snapshot.py &&
python3 scripts/vector_index_inventory.py

# Run Phase-2 eval (red-line gates enforced in review)
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli
```

## Implementation Phases

### Phase 1: Discovery & Assessmen

#### DSN repository audit and canonicalization plan
**Priority**: High
**MoSCoW**: 🔥 Mus
**Estimated Time**: 0.5h
**Dependencies**: PRD Section 0, repo access
**Solo Optimization**: Auto-advance: yes, Context preservation: yes

**Description**: Scan repo for `DATABASE_URL` and `POSTGRES_DSN` usages; produce `dsn_audit_repo.json` with paths and notes; confirm canonical choice: `DATABASE_URL` with fallback to `POSTGRES_DSN`.

**Acceptance Criteria**:
- [ ] `dsn_audit_repo.json` exists and lists all hits by file path
- [ ] Canonical env var documented in PRD and backlog B-1070 decisions

**Testing Requirements**:
- [ ] Unit: none (report-only)
- [ ] Integration: dry-run imports in scripts using resolver once added

**Implementation Notes**: Use simple os.walk scanner; exclude node_modules and venv.

**Quality Gates**:
- [ ] Documentation Updated – B-1070 section reflects Canonical DSN

---

#### Snapshot current pg_settings and vector indexes (pre-change)
**Priority**: High
**MoSCoW**: 🔥 Mus
**Estimated Time**: 0.5h
**Dependencies**: DB reachable

**Description**: Run snapshot utilities to generate `pg_settings_snapshot.json` and `vector_indexes.json` under `metrics/system_diagnostics/`.

**Acceptance Criteria**:
- [ ] JSON artifacts saved with timestamps
- [ ] Values reflect current discovery (shared_buffers 128MB, etc.)

**Testing Requirements**:
- [ ] Integration: scripts exit 0 and files contain non-empty arrays

**Quality Gates**:
- [ ] Documentation Updated – attach summaries to B-1070 Lessons Learned

---

#### Add lightweight DB healthcheck
**Priority**: High
**MoSCoW**: 🔥 Mus
**Estimated Time**: 0.5h
**Dependencies**: DSN resolver

**Description**: Implement `scripts/healthcheck_db.py` to validate connectivity, extensions (`vector`, `pg_stat_statements`), and key settings; nonzero exit on misconfig.

**Acceptance Criteria**:
- [ ] Running script prints server_version, extensions, and key settings
- [ ] Nonzero exit on missing `vector` or invalid DSN

**Testing Requirements**:
- [ ] Unit: mock DSN failure path
- [ ] Integration: real connection success path

**Quality Gates**:
- [ ] Tests Passing – basic unit/integration

---

### Phase 2: Connection Standardization

#### Implement DSN resolver helper and adopt in scripts path
**Priority**: Critical
**MoSCoW**: 🔥 Mus
**Estimated Time**: 1h
**Dependencies**: DSN audi

**Description**: Create `src/common/db_dsn.py` resolver (DATABASE_URL canonical with POSTGRES_DSN fallback, mismatch warning, write `dsn_audit.json`). Adopt in evaluation scripts first.

**Acceptance Criteria**:
- [ ] Resolver module exists with strict and warn modes
- [ ] Eval scripts import resolver and no longer read env directly

**Testing Requirements**:
- [ ] Unit: env variations (primary only, fallback only, mismatch)
- [ ] Integration: run eval script to ensure resolver chosen DSN used

**Quality Gates**:
- [ ] Code Review
- [ ] Documentation Updated – usage examples in PRD Section 0

---

#### Enable pg_stat_statements (observability first)
**Priority**: High
**MoSCoW**: 🔥 Mus
**Estimated Time**: 0.5h
**Dependencies**: Healthcheck

**Description**: Create extension and set minimal logging knobs (log_min_duration_statement=250ms, track_io_timing=on). Verify via healthcheck.

**Acceptance Criteria**:
- [ ] `pg_stat_statements` present in `pg_extension`
- [ ] Minimal logging enabled per config

**Testing Requirements**:
- [ ] Integration: `SELECT * FROM pg_stat_statements LIMIT 1;` succeeds

**Quality Gates**:
- [ ] Performance Validated – overhead negligible

---

### Phase 3: PostgreSQL Optimization (Incremental)

#### Stage A tuning (conservative)
**Priority**: Critical
**MoSCoW**: 🔥 Mus
**Estimated Time**: 1h
**Dependencies**: Observability enabled

**Description**: Apply Stage A: `shared_buffers=8GB`, `effective_cache_size=64GB`, `work_mem=32MB`, `maintenance_work_mem=2GB`, `max_wal_size=8GB`, `checkpoint_completion_target=0.9`, `wal_compression=on`, `jit=off`, `track_io_timing=on`, `effective_io_concurrency=0` (macOS). Backup `postgresql.conf` first.

**Acceptance Criteria**:
- [ ] Snapshot pre/post values
- [ ] DB restarted and healthcheck OK
- [ ] No baseline regression after eval

**Testing Requirements**:
- [ ] Performance: run full Phase-2 eval; compare metrics to red-line floors

**Quality Gates**:
- [ ] Baseline Protected – precision ≥ 0.159, recall ≥ 0.166, F1 ≥ 0.159

---

#### Stage B tuning (after stability)
**Priority**: High
**MoSCoW**: 🎯 Should
**Estimated Time**: 1h
**Dependencies**: Stage A stable

**Description**: Step up memory: `shared_buffers=16GB`, `effective_cache_size=96GB`, `work_mem=64MB`, `maintenance_work_mem=4GB`, `max_wal_size=16GB`, adopt `wal_compression=lz4` if supported.

**Acceptance Criteria**:
- [ ] Snapshot pre/pos
- [ ] Eval passes red-line gates

**Testing Requirements**:
- [ ] Performance: eval timing and vector p95 tracked

---

#### Stage C tuning (optional)
**Priority**: Medium
**MoSCoW**: 🎯 Should
**Estimated Time**: 0.5h
**Dependencies**: Stage B stable

**Description**: `shared_buffers=24GB`. Proceed only if metrics justify.

**Acceptance Criteria**:
- [ ] Snapshot pre/pos
- [ ] Eval passes red-line gates

**Testing Requirements**:
- [ ] Performance: confirm no regression, improved cache hit ratio

---

### Phase 4: Workload Isolation

#### Per-role GUCs for ltst_app and eval_app
**Priority**: High
**MoSCoW**: 🔥 Mus
**Estimated Time**: 1h
**Dependencies**: Resolver adopted, DB stable

**Description**: Create roles and set GUCs: ltst_app {work_mem=64MB, temp_file_limit=64GB, statement_timeout=25s}, eval_app {work_mem=32MB, temp_file_limit=32GB, statement_timeout=20s}. Tag application_name.

**Acceptance Criteria**:
- [ ] Roles exist; GUCs applied (SHOW current_setting checks)
- [ ] LTST and eval processes show distinct application_name

**Testing Requirements**:
- [ ] Integration: connect via each role and verify settings

**Quality Gates**:
- [ ] Documentation Updated – connection examples

---

#### Enforce cache separation and LTST concurrency guard
**Priority**: High
**MoSCoW**: 🔥 Mus
**Estimated Time**: 0.5h
**Dependencies**: Roles configured

**Description**: Ensure eval uses `.ragcache_eval` and LTST uses `.ragcache_ltst`. Cap LTST memory ops concurrency to 2–3 with a semaphore.

**Acceptance Criteria**:
- [ ] Cache dirs verified in logs and run output
- [ ] Concurrency cap present in LTST code paths

**Testing Requirements**:
- [ ] Integration: run eval while LTST idle and then lightly active; timings stable

---

### Phase 5: Performance Monitoring & Evidence-Driven Indexing

#### pgvector query-time policy
**Priority**: High
**MoSCoW**: 🔥 Mus
**Estimated Time**: 0.5h
**Dependencies**: Resolver adopted

**Description**: Set `SET LOCAL hnsw.ef_search = GREATEST(100, 2*k)` and `SET LOCAL hnsw.iterative_scan='strict_order'` in vector retrieval paths.

**Acceptance Criteria**:
- [ ] Retrieval code sets ef_search and iterative_scan per query
- [ ] No functional regressions; recall stable or improved

**Testing Requirements**:
- [ ] Performance: sample queries at K={8,16,32} show improved rows/latency

---

#### Create lightweight monitoring views
**Priority**: High
**MoSCoW**: 🔥 Mus
**Estimated Time**: 0.5h
**Dependencies**: pg_stat_statements enabled

**Description**: Add `vx_hot_vectors`, `vx_app_backends`, `vx_waits` SQL views for quick diagnostics.

**Acceptance Criteria**:
- [ ] Views created and queryable

**Testing Requirements**:
- [ ] Integration: each view returns rows under normal workload

---

#### Evidence-driven JSONB/BTREE indexes (if warranted)
**Priority**: Medium
**MoSCoW**: 🎯 Should
**Estimated Time**: 1h
**Dependencies**: pg_stat_statements data

**Description**: If containment-heavy predicates appear, add `jsonb_path_ops` GIN on metadata; add session/time BTREEs only for hot filters.

**Acceptance Criteria**:
- [ ] EXPLAIN (ANALYZE, BUFFERS) shows improved plans

**Testing Requirements**:
- [ ] Performance: before/after latency improvement; index size acceptable

---

### Optional / Deferred

#### PgBouncer feasibility check (no deployment)
**Priority**: Low
**MoSCoW**: ⚡ Could
**Estimated Time**: 0.5h
**Dependencies**: Evidence of backend pressure

**Description**: Assess need for transaction/session pooling; document decision.

**Acceptance Criteria**:
- [ ] Short note in backlog with decision and triggers

---

#### RAM-disk cache experiment (eval-only)
**Priority**: Low
**MoSCoW**: ⚡ Could
**Estimated Time**: 0.5h
**Dependencies**: Stable baseline

**Description**: Temporarily mount RAM disk for `.ragcache_eval` and compare eval timings.

**Acceptance Criteria**:
- [ ] Timing deltas recorded; revert immediately after tes

---

## Quality Metrics
- **Test Coverage Target**: Unit coverage for resolver and healthcheck ≥ 90%
- **Performance Benchmarks**: Eval total time < 5 minutes; vector p95 < 200 ms at K=16
- **Security Requirements**: Per-role creds; no hard-coded passwords in repo
- **Reliability Targets**: Zero baseline regressions across all stages
- **MoSCoW Alignment**: Musts completed before Should/Could tasks begin
- **Solo Optimization**: Auto-advance enabled on low-risk tasks; context preserved via artifacts

## Risk Mitigation
- **Technical Risks**: macOS tuning limits; mitigate via Stage A→B→C with rollback
- **Timeline Risks**: Gate each stage by baseline pass; avoid multi-stage batching
- **Resource Risks**: Limit LTST concurrency to 2–3 during evals
- **Priority Risks**: Defer PgBouncer and cache UNLOGGED/LZ4 until metrics justify

## Implementation Status
- **Total Tasks**: 20
- **MoSCoW Progress**: 🔥 Must: 10, 🎯 Should: 6, ⚡ Could: 4
- **Current Phase**: Planning
- **Blockers**: None (baseline guard enforced during changes)
