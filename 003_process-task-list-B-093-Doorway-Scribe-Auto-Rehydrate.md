# 003_process-task-list-B-093-Doorway-Scribe-Auto-Rehydrate

## Scope
- Trigger memory rehydration automatically when a Scribe-tracked session starts or resumes.
- Provide both a shell entrypoint and a programmatic Python call.
- Be safe-by-default: feature-flagged, debounced, observable, and failure-tolerant.

## Dependencies
- Completed: B-1006-A/B DSPy 3.0 migration, B-1007 Pydantic style
- Uses existing `scripts/memory_up.sh`

## Tasks
1. Create Python wrapper `scripts/memory_rehydrate.py` to invoke memory rehydration with role/query.
2. Add programmatic function `rehydrate_memory(role: str, query: str) -> bool`.
3. Add feature flag `AUTO_REHYDRATE` and debounce window `REHYDRATE_MINUTES` in config.
4. Integrate into Scribe start/resume path with debounce and try/except non-fatal handling.
5. Emit structured logs and metrics (counter + duration) around rehydration attempts.
6. Docs: brief section in `400_guides/400_development-workflow.md` and update memory context.
7. Tests: unit for debounce/flag; integration to assert single call per window.

## Acceptance Criteria
- With `AUTO_REHYDRATE=1`, session start triggers one rehydration per `REHYDRATE_MINUTES` window.
- Failures are logged and do not interrupt Scribe flow.
- Metrics present: `rehydrate_attempts_total` and `rehydrate_duration_seconds` histogram.
- Docs updated and `python scripts/update_cursor_memory.py` run.

## Rollback
- Set `AUTO_REHYDRATE=0` to disable without code changes.

## Validation Commands
```bash
export AUTO_REHYDRATE=1 REHYDRATE_MINUTES=10
python -m pytest -q
python scripts/memory_rehydrate.py --role planner --query "current project status and core documentation"
```
