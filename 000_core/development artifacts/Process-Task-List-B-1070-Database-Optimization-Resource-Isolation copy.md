# Process Task List: B-1070 Database Optimization & Resource Isolation

## 🔎 TL;DR
| what this file is | read when | do next |
|---|---|---|
| Enhanced execution workflow for B-1070 with solo optimizations, auto-advance, and context preservation | Ready to execute tasks from the B-1070 PRD and task list | Use the commands below to run healthchecks, snapshots, and evaluations with smart pausing |

## Execution Configuration
- **Auto-Advance**: yes
- **Pause Points**: [Postgres restarts, Stage A/B/C tuning commits, baseline regression detected]
- **Context Preservation**: LTST memory integration; artifacts in `metrics/system_diagnostics/`
- **Smart Pausing**: Automatic when a gate fails (healthcheck, baseline, connectivity)

## State Management
- **State File**: `.ai_state.json` (auto-generated, gitignored)
- **Progress Tracking**: Task completion mirrors `Task-List-B-1070-Database-Optimization-Resource-Isolation.md`
- **Session Continuity**: Use PRD Section 0 tech stack and repo layout for quick context

## Error Handling
- **HotFix Generation**: Create focused recovery tasks when gates fail (e.g., revert conf, re-run eval)
- **Retry Logic**: Backoff on transient DB connection failures (up to 3 attempts)
- **User Intervention**: Pause on config edits and restarts; resume after validation

## Execution Commands
```bash
# Healthcheck and discovery (Must)
python3 scripts/healthcheck_db.py && \
python3 scripts/pg_settings_snapshot.py && \
python3 scripts/vector_index_inventory.py

# Enable observability (Must, once)
psql "$DATABASE_URL" -c "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;" && \
psql "$DATABASE_URL" -c "SELECT * FROM pg_stat_statements LIMIT 1;"

# Run Phase‑2 evaluation with baseline gates (Must)
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli

# Show latest baseline summaries
ls -la metrics/baseline_evaluations/ | tail -n 5 && \
python3 - <<'PY'
import json,glob
paths=sorted(glob.glob('metrics/baseline_evaluations/ragchecker_official_evaluation_*.json'))
print(json.load(open(paths[-1]))['summary'])
PY
```

## Task Execution
Reference: `Task-List-B-1070-Database-Optimization-Resource-Isolation.md` (no duplication).

Key gate-driven execution flow:
1. Run healthcheck and snapshots → if fail, pause and fix DSN/config
2. Enable pg_stat_statements → confirm visibility
3. Apply Stage A tuning → restart Postgres → re-run healthcheck → run eval → enforce red-line gates
4. If stable, proceed to per-role GUCs and cache separation → confirm via session settings
5. Adopt pgvector query-time policy in retrieval paths → spot-check latency/rows
6. Optional Stage B/C → only after stability and with snapshots + eval gates

## Enhanced Execution Engine

### Auto-Advance Rules
- 🚀 One-command snapshot/eval tasks auto-advance
- 🔄 Stage changes advance only after healthcheck and eval gates pass
- ⏸️ Smart pause on Postgres restart steps, DSN resolver adoption, or baseline regression

### Smart Pausing Logic
- Critical decisions: Increasing shared_buffers beyond 16GB; switching WAL compression to lz4
- External dependencies: AWS Bedrock availability for full evals
- User validation: Confirm mismatch resolution when `dsn_audit.json` warns
- Error conditions: Any non-zero exit in healthcheck or missing extensions

### Context Preservation
- **LTST Memory**: Keep decisions in B-1070 Lessons Learned; link artifacts
- **Context bundle**: Use PRD Section 0 for tech stack, repo layout, and local commands
- **Scribe integration**: Append command lines and timings to `300_experiments/300_testing-methodology-log.md` tagged [B-1070]

## Quality Gates
- [ ] Code Review Completed (for resolver adoption and policy changes)
- [ ] Tests Passing (resolver + healthcheck unit tests)
- [ ] Documentation Updated (B-1070 decisions + Lessons Learned)
- [ ] Performance Validated (eval < 5 minutes, vector p95 targets)
- [ ] Security Reviewed (no creds in repo; per-role creds used)
- [ ] Resilience Tested (rollback of postgresql.conf via backup)
- [ ] Edge Cases Covered (mock://test vs real DSN; missing extensions)

## PRD Structure to Execution Mapping
- **Section 0** → Execution context (paths, commands, tools)
- **Section 1** → Validate contention assumptions with snapshots
- **Section 2** → Enforce phased optimization and isolation
- **Section 3** → Red-line gates applied after each change
- **Section 4** → Use stack and per-role GUCs as implementation guidance
- **Section 5** → Apply rollback on failure; measure overhead of observability
- **Section 6** → Execute performance and rollback tests per stage
- **Section 7** → Follow phase order and time budgets

## Output & Artifacts
- `metrics/system_diagnostics/pg_settings_snapshot.json`
- `metrics/system_diagnostics/vector_indexes.json`
- `dsn_audit.json`, `dsn_audit_repo.json`
- `metrics/baseline_evaluations/ragchecker_official_evaluation_*.json`
- B-1070 Lessons Learned bullets in `000_core/000_backlog.md`
- Methodology log entries in `300_experiments/300_testing-methodology-log.md` tagged [B-1070]

## Rollback Procedures
- Postgres tuning: restore `postgresql.conf.bak` and restart service
- Resolver adoption: revert import to previous `os.getenv` readers
- Observability: `DROP EXTENSION pg_stat_statements;` (only if overhead proven)
- Query-time policy: remove `SET LOCAL` statements

## Execution Notes
- macOS/Homebrew specifics: `effective_io_concurrency=0`, avoid huge_pages settings
- Separate caches: `.ragcache_eval` vs `.ragcache_ltst` must be honored in scripts
- Avoid heavy LTST jobs during evaluations; limit LTST concurrency to 2–3
