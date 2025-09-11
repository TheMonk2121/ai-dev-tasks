# PR: B-093 — Scribe Auto Rehydrate

## TL;DR
- Adds automatic memory rehydration on Scribe session registration, behind a feature flag and with per‑backlog debounce.
- Provides a Python CLI and programmatic entrypoints, metrics, docs, and tests.
- Backlog `B-093` marked done; roadmap updated.

## Scope
- Trigger memory rehydration when a Scribe‑tracked session starts/resumes.
- Safe by default: feature‑flagged, debounced, non‑fatal on failures, observable.

## Changes
- Entry points
  - New CLI: `scripts/memory_rehydrate.py` (role/query/format)
  - Programmatic helper + debounce: `scripts/rehydration_integration.py`
- Integration
  - Hook in `scripts/session_registry.py` on `register_session` using lazy import to avoid path issues.
- Observability
  - Metrics in `src/monitoring/metrics.py`:
    - `rehydrate_attempts_total`
    - `rehydrate_duration_seconds_{sum,count}`
- Docs
  - `400_guides/400_development-workflow.md`: added B‑093 section with flags, usage, metrics.
- Backlog/Roadmap
  - `000_core/000_backlog.md`: B‑093 set to done with completion date.
  - `000_core/004_development-roadmap.md`: B‑093 moved to Completed This Sprint.
- Tests
  - `tests/test_rehydration_integration.py`: flag and debounce tests (2 passing).

## Configuration
- `AUTO_REHYDRATE=1` to enable (default off)
- `REHYDRATE_MINUTES=10` debounce window (0 to disable debounce)

## Validation
- Unit tests: 2/2 passing
- Manual smoke: `AUTO_REHYDRATE=1 REHYDRATE_MINUTES=0 python3 scripts/session_registry.py register --backlog-id B-093 --pid $$ --worklog-path artifacts/worklogs/B-093.md` → memory bundle generated.

## Rollback
- Set `AUTO_REHYDRATE=0` to disable without code changes.
- Revert commit `7e8e8617` if required.

## Risks & Mitigations
- Risk: Excess rehydration calls. Mitigated by per‑backlog debounce and feature flag.
- Risk: Import path issues. Mitigated by dynamic module load and direct shell invocation fallback.

## Links
- Backlog: B‑093 — Doorway: Scribe + Auto Rehydrate
- Related: B‑1009 (AsyncIO Scribe), B‑1010 (NiceGUI Dashboard)
