<!-- CONTEXT_REFERENCE: 400_guides/400_cursor-context-engineering-guide.md -->
<!-- MODULE_REFERENCE: 100_memory/100_cursor-memory-context.md -->
<!-- MODULE_REFERENCE: 400_guides/400_project-overview.md -->
<!-- MODULE_REFERENCE: 400_guides/400_deployment-environment-guide.md -->
<!-- MEMORY_CONTEXT: HIGH - Current priorities and development roadmap -->
<!-- DATABASE_SYNC: REQUIRED -->

## Governance Hardening - New Backlog Items (Execution-Ready)

| B-171 | Enforce CODEOWNERS on critical paths | 🔒 | 3 | todo | Require approvals from owners on `000_core/`, `400_guides/`, `dspy-rag-system/src/vector_store/` | Governance + CI | CODEOWNERS + required reviews + docs updates |
<!-- score: {bv: 4, tc: 4, rr: 3, le: 3, lessons: 2, effort: 2, deps: []} -->
<!-- score_total: 3.5 -->
<!-- do_next: Add CODEOWNERS with explicit owners for core docs and vector store; enable GitHub branch protection to require code owner reviews; update PR template checklist. -->
<!-- acceptance: CODEOWNERS exists; branch protection requires at least 1 code owner review for protected paths; PR template shows CODEOWNERS checklist; sample PR on a protected path is blocked without owner review. -->
<!-- est_hours: 2 -->
<!-- lessons_applied: ["400_guides/400_system-overview.md", "500_reference-cards.md"] -->
<!-- reference_cards: ["401_consensus-log.md", "docs/100_ai-development-ecosystem.md"] -->

| B-172 | Block --no-verify bypass on protected branches | 🛡️ | 3 | todo | Ensure required status checks prevent bypassed local hooks | CI Policy | Require checks + policy docs |
<!-- score: {bv: 4, tc: 3, rr: 3, le: 3, lessons: 2, effort: 2, deps: []} -->
<!-- score_total: 3.2 -->
<!-- do_next: Configure branch protection to require validator/test status checks; disallow direct pushes; document policy that --no-verify is not relied on; add a CI job that fails if validator report is missing. -->
<!-- acceptance: Protected branches require CI checks (validator/tests) and block merge on failure; direct pushes disabled; a simulated commit without validator output fails CI; docs updated under contributing guide. -->
<!-- est_hours: 2 -->
<!-- lessons_applied: ["400_guides/400_contributing-guidelines.md", "400_guides/400_migration-upgrade-guide.md"] -->
<!-- reference_cards: ["400_guides/400_security-best-practices-guide.md", "500_reference-cards.md"] -->

| B-173 | Tighten exception ledger expiry discipline (≤7 days) | ⏳ | 3 | todo | Enforce max 7-day expiry and auto-alerts for near-expiry entries | Validator + CI | Ledger hygiene |
<!-- score: {bv: 4, tc: 3, rr: 3, le: 3, lessons: 2, effort: 2, deps: []} -->
<!-- score_total: 3.1 -->
<!-- do_next: Update `scripts/check_ledger_additions.py` to hard-fail on >7d expiries; ensure weekly job flags near-expiry waivers; add summary to PR comments when ledger entries present. -->
<!-- acceptance: CI blocks PRs introducing >7d ledger entries; weekly job outputs list of entries with ≤7 days remaining; validator PR comment shows count and oldest expiry; docs updated. -->
<!-- est_hours: 2 -->
<!-- lessons_applied: ["401_consensus-log.md", "400_guides/400_observability-system.md"] -->
<!-- reference_cards: ["400_guides/400_documentation-guide.md", "500_reference-cards.md"] -->

| B-174 | Dependency pinning with hashes + SCA/SAST | 🔐 | 5 | todo | Pin Python deps with hashes; add weekly SCA and CodeQL | Supply Chain | Security automation |
<!-- score: {bv: 5, tc: 4, rr: 4, le: 3, lessons: 2, effort: 3, deps: []} -->
<!-- score_total: 3.6 -->
<!-- do_next: Convert `requirements.txt` to hashed pins (pip-tools or pip-compile with --generate-hashes); add `pip-audit` (or Safety) weekly; enable CodeQL workflow; document remediation workflow. -->
<!-- acceptance: requirements with hashes committed; CI fails on unpinned/new deps without hashes; weekly SCA job runs and stores artifact; CodeQL enabled with default queries; remediation docs added to security guide. -->
<!-- est_hours: 4 -->
<!-- lessons_applied: ["400_guides/400_security-best-practices-guide.md", "400_guides/400_performance-optimization-guide.md"] -->
<!-- reference_cards: ["400_guides/400_deployment-environment-guide.md", "500_reference-cards.md"] -->

| B-175 | Vector store PR e2e smoke + perf budgets | 🚀 | 5 | todo | Gate vector store changes with smoke tests and latency budgets | Testing + CI | Perf guardrails |
<!-- score: {bv: 5, tc: 4, rr: 4, le: 3, lessons: 2, effort: 3, deps: []} -->
<!-- score_total: 3.7 -->
<!-- do_next: Add selective CI job triggering on `dspy-rag-system/src/vector_store/**`; run minimal e2e smoke; enforce budgets (e.g., similarity_search p95 < 200ms, health check < 50ms) and fail on regression; publish perf summary as PR comment. -->
<!-- acceptance: On PRs touching vector store, CI runs smoke and enforces budgets; budget breaches fail CI; perf summary artifact and PR comment posted; thresholds documented in testing strategy guide. -->
<!-- est_hours: 4 -->
<!-- lessons_applied: ["tests/e2e/test_vector_store_modes_e2e.py", "400_guides/400_testing-strategy-guide.md"] -->
<!-- reference_cards: ["400_guides/400_performance-optimization-guide.md", "500_reference-cards.md"] -->

| B-176 | 400_guides Heading Normalization (Single H1 Rule) | 📚 | 3 | todo | Demote all headings after the first `#` to `##+` across `400_guides/**`; ensure the single H1 matches the filename title; preserve TL;DR anchors | Docs Governance | Standardize headings across guides |
<!-- score: {bv: 4, tc: 4, rr: 3, le: 3, effort: 3, deps: []} -->
<!-- score_total: 4.7 -->
<!-- do_next: Audit all `400_guides/*.md` for multiple H1s; apply consistent title lines matching filenames; convert internal H1s to H2/H3; add TL;DR anchors if missing. -->
<!-- acceptance: Every guide has exactly one H1 matching filename; internal sections start at H2; TL;DR present and anchored; markdown lint passes for MD001/MD002. -->
<!-- est_hours: 3 -->
<!-- lessons_applied: ["400_guides/400_documentation-guide.md", "400_guides/400_system-overview.md"] -->
<!-- reference_cards: ["400_guides/400_comprehensive-coding-best-practices.md", "500_reference-cards.md"] -->

| B-177 | Consolidate Docs: Documentation Reference + Retrieval | 📚 | 3 | done | Merge `400_documentation-reference.md` and `400_documentation-retrieval-guide.md` into a single `400_documentation-guide.md` with sections: Reference, Retrieval, Validation; update cross-links | Docs Consolidation | One canonical documentation guide |
<!-- score: {bv: 4, tc: 3, rr: 3, le: 2, effort: 2, deps: []} -->
<!-- score_total: 6.0 -->
<!-- do_next: Create new `400_documentation-guide.md`; port content; add redirects/notes in old files; update inbound links in `000_core/**`, `400_guides/**`, `dspy-rag-system/**`. -->
<!-- acceptance: New guide exists with merged content; old guides contain deprecation headers linking to the new file; all internal references updated and tests/linkcheck pass. -->
<!-- est_hours: 2 -->
<!-- lessons_applied: ["400_guides/400_documentation-guide.md"] -->
<!-- reference_cards: ["400_guides/400_documentation-guide.md"] -->

| B-178 | Consolidate Performance Docs (Fold Script Optimization) | ⚡ | 3 | done | Fold `400_script-optimization-guide.md` into `400_performance-optimization-guide.md` as a dedicated section; remove duplication; update links | Performance Docs | Simplify and centralize |
<!-- score: {bv: 3, tc: 3, rr: 3, le: 2, effort: 2, deps: []} -->
<!-- score_total: 5.5 -->
<!-- do_next: Move script optimization sections into performance guide; add deprecation header to script optimization guide; update references across repo. -->
<!-- acceptance: Performance guide contains consolidated content; script optimization guide marked as folded with link; linkcheck passes. -->
<!-- est_hours: 2 -->
<!-- lessons_applied: ["400_guides/400_performance-optimization-guide.md", "400_guides/400_performance-optimization-guide.md"] -->
<!-- reference_cards: ["500_reference-cards.md"] -->

| B-179 | Overview Consistency (Project vs System) | 🏗️ | 3 | done | Make `400_project-overview.md` a concise landing that points to `400_system-overview.md` (or fold content as subsections); ensure single source of truth | Docs IA | Clarify entry points |
<!-- score: {bv: 3, tc: 2, rr: 2, le: 2, effort: 2, deps: []} -->
<!-- score_total: 4.5 -->
<!-- do_next: Decide canonical host (keep `400_system-overview.md`); trim `400_project-overview.md` to a signpost; update inbound links. -->
<!-- acceptance: One canonical overview; the other is a short landing with links; all references updated. -->
<!-- est_hours: 2 -->
<!-- lessons_applied: ["400_guides/400_project-overview.md", "400_guides/400_system-overview.md"] -->
<!-- reference_cards: ["400_guides/400_cursor-context-engineering-guide.md"] -->

| B-180 | Roadmap De-duplication (Core vs Guide) | 🗺️ | 3 | done | De-duplicate `400_development-roadmap.md` with `000_core/004_development-roadmap.md`; keep the core file canonical and convert the guide to a brief link/summary | Docs Governance | Single source of truth |
<!-- score: {bv: 3, tc: 3, rr: 3, le: 2, effort: 2, deps: []} -->
<!-- score_total: 5.5 -->
<!-- do_next: Move any unique guidance into the core roadmap; reduce the guide to a signpost; update links in `400_guides/**` and `docs/**`. -->
<!-- acceptance: Only one canonical roadmap; secondary file is a stub pointing to canonical; linkcheck passes. -->
<!-- est_hours: 2 -->
<!-- lessons_applied: ["000_core/004_development-roadmap.md", "000_core/004_development-roadmap.md"] -->
<!-- reference_cards: ["400_guides/400_documentation-guide.md"] -->

| B-181 | Observability + Mission Dashboard Unification | 🔍 | 3 | done | Integrate `400_mission-dashboard-guide.md` under `400_observability-system.md` as a section or cross-link strongly; avoid duplication | Observability Docs | Unify monitoring docs |

| B-182 | Global Bug-Fix Playbook + Enforcement Layers (Cursor + CI) | 🐛 | 5 | OK done | Introduce three-layer enforcement system: Preset (soft), Multi-Framework Hot-Zone Rules (targeted), CI Guard (hard) with Conventional Commits validation | Debug Velocity | CS-level rigor without slowing velocity |
<!-- score: {bv: 5, tc: 4, rr: 4, le: 3, lessons: 2, effort: 2, deps: []} -->
<!-- score_total: 3.8 -->
<!-- do_next: MVP (4h): Create Cursor preset with ⌘⌥B shortcut, multi-framework hot-zone rules with commit detection, enhanced CI guard with Conventional Commits validation. -->
<!-- acceptance: Preset works with keyboard shortcut; hot-zone rules detect commit prefixes and suggest appropriate frameworks; CI validates framework compliance based on commit messages; regression rate drops ≥30% in hot zones. -->
<!-- est_hours: 4 -->
<!-- lessons_applied: ["400_guides/400_comprehensive-coding-best-practices.md", "400_guides/400_testing-strategy-guide.md"] -->
<!-- reference_cards: ["400_guides/400_security-best-practices-guide.md", "PRD-B-182-Global-Bug-Fix-Playbook.md"] -->

| B-183 | Feature Refactor Framework (Initial Draft → Consensus → Validation) | 🔄 | 5 | todo | Introduce 5-phase consensus framework for structural/systemic changes with unified PR template, enhanced CI guard with Conventional Commits validation, and integration with existing governance | Refactor Governance | Prevent architectural drift, ensure stakeholder consensus, maintain velocity |
<!-- score: {bv: 5, tc: 4, rr: 4, le: 3, lessons: 2, effort: 3, deps: [B-182]} -->
<!-- score_total: 3.7 -->
<!-- do_next: Create docs/005_feature_refactor_playbook.md, Cursor preset for consensus process, unified PR template with conditional sections, enhanced CI guard with Conventional Commits validation, framework quick-reference cheat sheet. -->
<!-- acceptance: Decision matrix guides framework selection; 100% refactor PRs have consensus phases; CI validates framework compliance based on commit messages; integration with existing governance works seamlessly. -->
<!-- est_hours: 5 -->
<!-- lessons_applied: ["PRD-B-182-Global-Bug-Fix-Playbook.md", "400_guides/400_comprehensive-coding-best-practices.md"] -->
<!-- reference_cards: ["400_guides/400_testing-strategy-guide.md", "PRD-B-183-Feature-Refactor-Framework.md"] -->
<!-- score: {bv: 3, tc: 2, rr: 3, le: 2, effort: 2, deps: []} -->
<!-- score_total: 5.0 -->
<!-- do_next: Add a "Mission dashboard" section to observability guide; convert mission dashboard guide into a stub with link; update references (scripts, README). -->
<!-- acceptance: Observability guide contains the authoritative dashboard docs; dashboard guide is a stub; linkcheck passes. -->
<!-- est_hours: 2 -->
<!-- lessons_applied: ["400_guides/400_observability-system.md", "400_guides/400_mission-dashboard-guide.md"] -->
<!-- reference_cards: ["400_guides/400_mission-dashboard-guide.md", "500_reference-cards.md"] -->

| B-182 | Context Guide Consolidation | 🧠 | 3 | done | Consolidate `400_context-priority-guide.md` into `400_cursor-context-engineering-guide.md` as a dedicated section; update inbound links | Context System | Reduce duplication |
<!-- score: {bv: 4, tc: 3, rr: 3, le: 3, effort: 3, deps: []} -->
<!-- score_total: 4.3 -->
<!-- do_next: Move priority ordering guidance into context engineering guide; add deprecation header to context priority guide; update references across repo. -->
<!-- acceptance: Context engineering guide contains the priority section; old guide marked as folded; linkcheck passes. -->
<!-- est_hours: 3 -->
<!-- lessons_applied: ["400_guides/400_cursor-context-engineering-guide.md", "400_guides/400_cursor-context-engineering-guide.md"] -->
<!-- reference_cards: ["400_guides/400_hydration-system-guide.md"] -->

| B-183 | Cross-Reference Update Sweep (Post-Consolidation) | 🔗 | 3 | done | Update inbound links and references across the repo after merges/renames; add deprecation headers/redirects | Docs Maintenance | Preserve link integrity |
<!-- score: {bv: 4, tc: 3, rr: 4, le: 2, effort: 3, deps: ["B-177", "B-178", "B-179", "B-180", "B-181", "B-182"]} -->
<!-- score_total: 4.3 -->
<!-- do_next: Run repo-wide linkcheck; update links; add deprecation headers to folded files; verify tests that depend on guide anchors. -->
<!-- acceptance: No broken internal links; folded files clearly marked with pointers; validator and link tests green. -->
<!-- est_hours: 3 -->
<!-- lessons_applied: ["400_guides/400_documentation-guide.md", "400_guides/400_system-overview.md"] -->
<!-- reference_cards: ["tests/linkcheck/test_internal_links.py"] -->

| B-184 | Cursor-Native Model Listing Cleanup | 🧭 | 2 | done | Trim non-Cursor third-party model catalogs in `400_system-overview.md`; keep docs Cursor-native focused | Docs Policy | Align with Cursor-native focus |
<!-- score: {bv: 3, tc: 3, rr: 3, le: 2, effort: 2, deps: []} -->
<!-- score_total: 5.5 -->
<!-- do_next: Remove lengthy third-party model lists; keep a brief note and link out if needed; ensure policy is reflected in contributing/docs guides. -->
<!-- acceptance: `400_system-overview.md` focuses on Cursor-native models; no long third-party model catalogs remain; cross-references updated. -->
<!-- est_hours: 1 -->
<!-- lessons_applied: ["400_guides/400_system-overview.md", "400_guides/400_cursor-context-engineering-guide.md"] -->
<!-- reference_cards: ["400_guides/400_ai-constitution.md"] -->

| B-185 | Repo-wide Internal Link + Anchor Validator | 🔗 | 2 | OK done | Expand validator to index anchors across repo and support changed-files mode | Docs Tooling | Multi-scope linkcheck + changed-files |
<!-- score: {bv: 5, tc: 4, rr: 5, le: 3, effort: 2, deps: []} -->
<!-- score_total: 8.5 -->
<!-- do_next: Update `scripts/link_check.py` to accept `--scope .` and/or multiple scopes; index anchors for `000_core/` and `400_guides/`; add `--changed-files-from` flow in CI. -->
<!-- acceptance: Validator can scan repo-wide; CI job passes on clean run and fails when a non-existent anchor is introduced; JSON summary artifacts produced. -->
<!-- est_hours: 2 -->
<!-- lessons_applied: ["tests/linkcheck/test_internal_links.py", "400_guides/400_documentation-guide.md"] -->
<!-- reference_cards: ["500_reference-cards.md#documentation-maintenance"] -->
<!-- completion_date: 2025-08-18 -->
<!-- implementation_notes: Enabled scope '.' and comma-separated scopes in scripts/link_check.py; build_file_index/check_scope now iterate multiple base paths and index anchors repo-wide. Added repo-wide cross-folder emoji anchor test. -->

| B-186 | Path Normalization in Link Checker | 🧭 | 1 | OK done | Use `pathlib.Path` for relative path resolution in `scripts/link_check.py` | Docs Tooling | Robust relative resolution |
<!-- score: {bv: 3, tc: 2, rr: 2, le: 2, effort: 1, deps: []} -->
<!-- score_total: 9.0 -->
<!-- do_next: Replace manual string math in `_resolve_relative_path` with `Path(source).parent / target`; ensure posix output; add unit coverage. -->
<!-- acceptance: Cross-folder links like `../400_guides/...#anchor` resolve correctly in tests; validator output unchanged except fixes for previously mis-resolved links. -->
<!-- est_hours: 1 -->
<!-- lessons_applied: ["tests/linkcheck/test_internal_links.py"] -->
<!-- reference_cards: ["500_reference-cards.md#python-pathlib"] -->
<!-- completion_date: 2025-08-18 -->
<!-- implementation_notes: Rewrote _resolve_relative_path using pathlib with POSIX output; resolved root path in constructor; normalized source file paths in check_file; added cross-folder ../ link test that passes. -->

| B-187 | Emoji Heading Slug + Cross-Folder Tests | OK | 1 | OK done | Add tests for emoji headings (e.g., "⚡ Quick reference") and cross-folder anchors | Testing | Slug + link e2e tests |
<!-- score: {bv: 3, tc: 2, rr: 2, le: 2, effort: 1, deps: []} -->
<!-- score_total: 9.0 -->
<!-- do_next: Add unit in `tests/xref/test_slugify.py` for slug `quick-reference`; add integration in `tests/linkcheck/test_internal_links.py` for cross-folder link. -->
<!-- acceptance: Tests assert slug `quick-reference`; integration test validates link across `000_core/` → `400_guides/`. -->
<!-- est_hours: 1 -->
<!-- lessons_applied: ["tests/xref/test_slugify.py", "tests/linkcheck/test_internal_links.py"] -->
<!-- reference_cards: ["500_reference-cards.md#testing-patterns"] -->
<!-- completion_date: 2025-08-18 -->
<!-- implementation_notes: Added slug unit test for '⚡ Quick reference' -> 'quick-reference' and integration tests for emoji anchors within 000_core and cross-folder with scope '.'. All tests pass. -->

| B-188 | Pre-commit + CI Gate for Anchor Validation | 🛡️ | 2 | OK done | Run link checker on changed `.md` files locally and in CI | CI Policy | Prevent broken anchors at PR time |
<!-- score: {bv: 5, tc: 4, rr: 5, le: 3, effort: 2, deps: ["B-185", "B-186", "B-187"]} -->
<!-- score_total: 8.5 -->
<!-- do_next: Add pre-commit hook; CI step to diff against main and run validator with `--changed-files-from`; publish human + JSON summaries. -->
<!-- acceptance: Hook blocks commits with broken anchors locally; CI fails PRs with broken anchors and posts summary. -->
<!-- est_hours: 2 -->
<!-- lessons_applied: ["400_guides/400_contributing-guidelines.md"] -->
<!-- reference_cards: ["500_reference-cards.md#github-actions"] -->
<!-- completion_date: 2025-08-18 -->
<!-- implementation_notes: Added .pre-commit-config.yaml hook invoking scripts/link_check.py with --root . --scope . --changed-files; added GitHub Actions workflow .github/workflows/linkcheck.yml to run on PRs/push, diff changed .md, run validator, and upload JSON report. -->

| B-189 | Authoring Guideline Update: Anchors & Quick Refs | 📚 | 1 | OK done | Document anchor usage and validator workflow in `400_documentation-guide.md` | Docs Governance | Clear authoring guidance |
<!-- score: {bv: 3, tc: 2, rr: 2, le: 2, effort: 1, deps: ["B-185"]} -->
<!-- score_total: 9.0 -->

| B-190 | Configure Bug-Fix Playbook Keyboard Shortcut | ⌨️ | 2 | todo | Configure `⌘⌥B` shortcut in Cursor to inject bug-fix playbook preset into chat sidecar | Cursor Integration | Enable one-keystroke access to structured debugging workflow |
<!-- score: {bv: 4, tc: 3, rr: 3, le: 2, effort: 1, deps: ["B-182"]} -->
<!-- score_total: 6.5 -->
<!-- do_next: Check current `⌘⌥B` mapping in Cursor; configure shortcut to inject bug-fix playbook preset; test functionality in chat sidecar; update documentation if shortcut conflicts exist. -->
<!-- acceptance: `⌘⌥B` injects bug-fix playbook template into chat sidecar; no conflicts with existing shortcuts; documentation updated with working shortcut. -->
<!-- est_hours: 1 -->
<!-- lessons_applied: ["000_core/004_bugfix_playbook.md", "docs/cursor/presets/debug_playbook_preset.md"] -->
<!-- reference_cards: ["400_guides/400_cursor-context-engineering-guide.md"] -->
<!-- do_next: Add section covering heading levels, emoji anchors, and how to run validator locally/CI; add examples. -->
<!-- acceptance: Guide includes anchor authoring rules and quick reference; internal links updated; linkcheck passes. -->
<!-- est_hours: 1 -->
<!-- lessons_applied: ["400_guides/400_documentation-guide.md"] -->
<!-- reference_cards: ["500_reference-cards.md#documentation-maintenance"] -->
<!-- completion_date: 2025-08-18 -->
<!-- implementation_notes: Updated 400_guides/400_documentation-guide.md with 'Authoring guidelines for anchors and headings', emoji slug behavior, cross-folder link example, and validator quick commands. -->

<!-- ANCHOR_KEY: backlog -->
<!-- ANCHOR_PRIORITY: 10 -->
<!-- ROLE_PINS: ["planner"] -->

# 📋 Backlog

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Prioritized backlog with AI scoring and execution flow | When selecting next work item or checking project status |
Check P0 lane and AI-executable queue; follow PRD skip rule |

- **what this file is**: Prioritized roadmap with AI scoring, lanes, and execution flow.

- **read when**: Selecting next work or checking dependencies and status.

- **do next**: See `#p0-lane` and `#ai-executable-queue-003`; follow PRD rule in "PRD Rule & Execute Flow".

- **anchors**: `p0-lane`, `p1-lane`, `p2-lane`, `ai-executable-queue-003`, `live-backlog`, `completed-items`

<!-- ANCHOR_KEY: tldr -->
<!-- ANCHOR_PRIORITY: 0 -->
<!-- ROLE_PINS: ["planner"] -->

<!-- ANCHOR: toc -->

## 🎯 **Current Status**-**Status**: OK **ACTIVE**- Backlog maintained and current

- **Priority**: 🔥 Critical - Essential for development planning

- **Points**: 5 - High complexity, strategic importance

- **Dependencies**: 400_guides/400_cursor-context-engineering-guide.md, 100_memory/100_cursor-memory-context.md

- **Next Steps**: Update priorities and track completion

## Quick Navigation

- [P0 Lane](#p0-lane)

- [P1 Lane](#p1-lane)

- [P2 Lane](#p2-lane)

- [AI-Executable Queue (003)](#ai-executable-queue-003)

- [Live Backlog](#live-backlog)

- [Completed Items](#completed-items-context-preservation)

- [Setup Required Items](#setup-required-items)

<!-- ANCHOR: governance-p0 -->

## Governance P0 (Non-Negotiables)

These must be addressed before or alongside feature work to maintain cognitive digestibility and safety.

- **Critical Policies surfacing**: Add a "Critical Policies (Read First)" callout in
`100_memory/100_cursor-memory-context.md` (Safety Ops, Exclusions, Validators/Tests, Post-Change `python3
scripts/update_cursor_memory.py`). Cross-link from `400_guides/400_system-overview.md` (Safety Ops anchor) and
`400_guides/400_cursor-context-engineering-guide.md` (mini-index).

- **Cursor-native focus cleanup**: Remove or annotate legacy model references (Mistral, Yi-Coder) in `400_*` guides; add
a validator check to prevent reintroduction.

- **Research summaries consolidation**: Merge `500_research/500_research-summary.md` and
`500_research-analysis-summary.md` into `500_research/500_research-index.md`; archive originals with deprecation notes.

- **Markdown lint remediation plan**:
- Config + light auto-fixes (30-60 minutes): Keep MD034 (no bare URLs) and MD040 (code fence language) enabled and fix
across repo. Replace bare URLs with `[text](url)`. Add language tags to fenced code blocks. Run
`scripts/fix_markdown_blanks.py` to settle heading/list spacing.
- Full cleanup (strict conformance without disabling) (2-4 hours): Remove inline HTML anchors, rework heading levels,
and normalize spacing across long-form guides.

<!-- ANCHOR: p0-lane -->

<!-- ANCHOR_KEY: p0-lane -->
<!-- ANCHOR_PRIORITY: 5 -->
<!-- ROLE_PINS: ["planner"] -->

## P0 Lane

- B-052-d - CI GitHub Action (Dry-Run Gate) (score 8.0)

- B-062 - Context Priority Guide Auto-Generation (score 8.0)

- B-104 - 400_guides Documentation Standardization & Optimization (score 7.0)

- B-103 - Repo Layout Normalization (score 4.3)

## P1 Lane

- B-075 - Few-Shot Cognitive Scaffolding Integration (score 6.0)

- B-084 - Research-Based Schema Design for Extraction (score 6.0)

- B-050 - Enhance 002 Task Generation with Automation (score 5.5)

- B-052-f - Enhanced Repository Maintenance Safety System (score 5.1)

- B-052-b - Config Externalization to TOML + Ignore (score 5.0)

## P2 Lane

- B-076 - Research-Based DSPy Assertions Implementation (score 4.8)

- B-052-c - Hash-Cache + Optional Threading (score 4.5)

- B-018 - Local Notification System (score 4.5)

- B-043 - LangExtract Pilot w/ Stratified 20-doc Set (score 4.2)

- B-044 - n8n LangExtract Service (Stateless, Spillover, Override) (score 4.2)

- B-078 - LangExtract Structured Extraction Service (score 4.2)

## AI-Executable Queue (003)

## PRD Rule & Execute Flow

- PRD skip rule: Skip PRD when points < 5 AND score_total ≥ 3.0

- Execute flow: 000_core/001_create-prd.md → 000_core/002_generate-tasks.md → 000_core/003_process-task-list.md

Quick links: `100_memory/100_cursor-memory-context.md`, `400_guides/400_system-overview.md`,
`400_guides/400_cursor-context-engineering-guide.md`

<!-- ANCHOR: current-priorities -->

A prioritized list of future enhancements and features for the AI development ecosystem.

- *📋 For usage instructions and scoring details, see `100_memory/100_backlog-guide.md`**

- *🤖 Execution Guide**: Items can be executed directly by AI using `000_core/003_process-task-list.md` as the execution
engine.
Items requiring external credentials, business decisions, or deployment should be marked with `<!-- human_required: true
- ->`.

<!-- CORE_SYSTEM: 400_guides/400_project-overview.md, 400_guides/400_system-overview.md,
100_memory/100_cursor-memory-context.md -->
<!-- METADATA_SYSTEM: 400_guides/400_metadata-collection-guide.md -->
<!-- ROADMAP_REFERENCE: 000_core/004_development-roadmap.md -->
<!-- RESEARCH_SYSTEM: 500_research/500_research-index.md, 500_research-analysis-summary.md, 500_dspy-research.md,
500_rag-system-research.md -->
<!-- WORKFLOW_CHAIN: 000_core/001_create-prd.md → 000_core/002_generate-tasks.md → 000_core/003_process-task-list.md -->
<!-- EXECUTION_ENGINE: scripts/process_tasks.py -->
<!-- AUTOMATION_FILES: 100_backlog-automation.md, 100_memory/100_backlog-guide.md -->
<!-- MEMORY_CONTEXT: HIGH - Current priorities and development roadmap for AI context -->
<!-- PRD_DECISION_RULE: points<5 AND score_total>=3.0 -->
<!-- PRD_THRESHOLD_POINTS: 5 -->
<!-- PRD_SKIP_IF_SCORE_GE: 3.0 -->

- --

## Live Backlog

| ID  | Title                                   | 🔥P | 🎯Points | Status | Problem/Outcome | Tech Footprint | Dependencies |
|-----|-----------------------------------------|-----|----------|--------|-----------------|----------------|--------------|
| B-052-d | CI GitHub Action (Dry-Run Gate) | 🔧 | 0.5 | todo | Add GitHub Action to run maintenance script on PRs | GitHub Actions + CI/CD | None |
<!--score: {bv:3, tc:2, rr:3, le:3, effort:0.5, lessons:3, deps:[]}-->
<!--score_total: 8.0-->
<!-- do_next: Create GitHub Action workflow for automated maintenance script execution -->
<!-- est_hours: 2 -->
<!-- acceptance: PRs automatically trigger maintenance script validation -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#ci-cd-patterns"] -->
<!-- reference_cards: ["500_reference-cards.md#github-actions"] -->

| B-104 | 400_guides Documentation Standardization & Optimization | 📚 | 5 | OK done | Standardize and optimize 400_guides documentation based on analysis findings | Documentation Standards + Cross-References + Governance Validation | None |
<!--score: {bv:4, tc:3, rr:4, le:4, effort:3, lessons:3, deps:[]}-->
<!--score_total: 7.0-->
<!-- do_next: Add Current Status sections to 5 missing guides and rename governance_runbook.md to 400_governance-runbook.md -->
<!-- est_hours: 8 -->
<!-- acceptance: All guides have Current Status sections, consistent naming, and pass governance validation -->
<!-- completion_date: 2025-08-18 -->
<!-- implementation_notes: Successfully added Current Status sections to 5 missing guides (400_ai-constitution.md, 400_enhanced-backlog-tracking-guide.md, 400_script-optimization-guide.md, 400_task-generation-quick-reference.md, 400_governance-runbook.md). Renamed governance_runbook.md to 400_governance-runbook.md and updated all cross-references in 6 files. All guides now follow consistent naming convention and documentation standards. -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#documentation-standards"] -->
<!-- reference_cards: ["500_reference-cards.md#documentation-maintenance"] -->

| B-062 | Context Priority Guide Auto-Generation | 🔧 | 0.5 | todo | Create regen_guide.py to auto-generate context
priority guide from file headers | Guide Generation + Cross-Reference Aggregation + Tier Lists | B-060 Documentation
Coherence Validation System |
<!--score: {bv:3, tc:2, rr:2, le:2, effort:0.5, deps:["B-060"]}-->
<!--score_total: 8.0-->
<!-- do_next: Implement automated context priority guide generation script -->
<!-- est_hours: 2 -->
<!-- acceptance: Context priority guide updates automatically when core docs change -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#documentation-automation"] -->
<!-- reference_cards: ["500_reference-cards.md#documentation-generation"] -->

| B-101 | Adaptive Routing in Consensus Framework | 🔄 | 5 | OK done | Route different query types through optimized pipelines | Query analysis + Pipeline selection + Performance optimization | B-100 Multi-representation indexing |
<!--score: {bv:4, tc:3, rr:4, le:4, lessons:4, effort:3, deps:["B-100"]}-->
<!--score_total: 3.9-->
<!-- completion_date: 2025-08-16 -->
<!-- implementation_notes: Successfully implemented adaptive routing system with query type classification (pointed, broad, analytical, creative) and pipeline selection (fast_path, comprehensive, creative). Added complexity analysis, keyword extraction, and comprehensive test suite. System routes queries based on type and complexity for optimal performance. -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#performance-optimization"] -->
<!-- reference_cards: ["500_reference-cards.md#rag-lessons-from-jerry"] -->

| B-103 | Advanced Feedback Loops & Lessons Integration | 🔄 | 6 | OK done | Integrate systematic feedback from linter/test errors and git commits into lessons learned | Feedback collection + Lessons aggregation + Backlog influence | B-101 Adaptive Routing |
<!--score: {bv:4, tc:4, rr:4, le:5, lessons:5, effort:4, deps:["B-101"]}-->
<!--score_total: 4.3-->
<!-- completion_date: 2025-08-16 -->
<!-- implementation_notes: Successfully implemented comprehensive feedback loop system with linter/test/git feedback collection, pattern analysis, lessons extraction, and backlog recommendations. System collected 423 feedback items and generated 176 lessons with 169 backlog recommendations. Added 16 comprehensive tests with mocked subprocess calls. -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#reference-discipline"] -->
<!-- reference_cards: ["500_reference-cards.md#traceability"] -->

| B-104 | Full Consensus Framework Integration | 🔄 | 8 | OK done | Implement complete consensus framework with strawman proposals, red team/blue team roles, and consensus validation | Consensus rounds + Role management + Validation checkpoints | B-103 Advanced Feedback Loops |
<!--score: {bv:5, tc:5, rr:5, le:5, lessons:5, effort:6, deps:["B-103"]}-->
<!--score_total: 5.2-->
<!-- completion_date: 2025-08-16 -->
<!-- implementation_notes: Successfully implemented complete consensus framework with strawman proposals, red team/blue team roles, consensus rounds, validation checkpoints, and integration with existing Tier 1/2 infrastructure. Created scripts/consensus_framework.py (1207 lines), scripts/consensus_integration.py for infrastructure integration, and comprehensive test workflow. System supports full consensus lifecycle from proposal creation to finalization with role-based validation and implementation guidance. Integrated with existing process_tasks.py, state_manager.py, doc_coherence_validator.py, and feedback_loop_system.py infrastructure. -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#consensus-patterns"] -->
<!-- reference_cards: ["500_reference-cards.md#consensus-framework"] -->

| B-105 | Comprehensive Test Suite Update | 🔧 | 4 | todo | Update comprehensive test suite to cover all consensus framework components and integration points | Test coverage + Integration testing + Quality assurance | B-104 Full Consensus Framework Integration |
<!--score: {bv:4, tc:4, rr:3, le:4, lessons:4, effort:4, deps:["B-104"]}-->
<!--score_total: 4.0-->
<!-- do_next: Create comprehensive test suite for consensus framework and integration components -->
<!-- est_hours: 8 -->
<!-- acceptance: All consensus framework components have comprehensive test coverage with integration tests -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#testing-patterns"] -->
<!-- reference_cards: ["500_reference-cards.md#test-coverage"] -->



| B-106 | File Organization & Management Cleanup | 🔧 | 3 | todo | Clean up file organization issues including duplicate pyproject.toml files, misplaced 500_ files, and 400_ files in wrong locations | File organization + Directory structure + Configuration management | B-103 Repo Layout Normalization (P0) |
<!--score: {bv:3, tc:3, rr:3, le:4, lessons:4, effort:3, deps:["B-103"]}-->
<!--score_total: 3.4-->
<!-- do_next: Audit and reorganize files according to established directory structure and naming conventions -->
<!-- est_hours: 6 -->
<!-- acceptance: All files are in correct directories with proper naming conventions, no duplicate configuration files -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#file-organization"] -->
<!-- reference_cards: ["500_reference-cards.md#project-structure"] -->

| B-075 | Few-Shot Cognitive Scaffolding Integration | ⭐ | 6 | OK done | Integrate few-shot examples into cognitive scaffolding for AI agents | Few-shot patterns + AI context engineering | B-074 Few-Shot Integration with Documentation Tools |
<!--score: {bv:4, tc:3, rr:4, le:3, effort:6, lessons:4, deps:["B-074"]}-->
<!--score_total: 6.0-->
<!-- do_next: Implement few-shot cognitive scaffolding for AI agent context enhancement -->
<!-- est_hours: 8 -->
<!-- acceptance: AI agents use few-shot examples for improved context understanding -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#few-shot-patterns"] -->
<!-- reference_cards: ["500_reference-cards.md#cognitive-scaffolding"] -->
<!-- PRD: 001_create-prd.md#B-075 -->
<!-- completion_date: 2025-08-16 -->
<!-- implementation_notes: Successfully implemented few-shot cognitive scaffolding integration. Created scripts/few_shot_cognitive_scaffolding.py with example extraction, role-based filtering, and memory rehydration integration. Extracted 356 examples from documentation, implemented pattern recognition, and integrated with cursor_memory_rehydrate.py. System now provides context-aware few-shot examples for AI agents, improving response quality and consistency. -->

| B-084 | Research-Based Schema Design for Extraction | 📈 | 6 | OK done | Design extraction schemas based on research findings | Schema design + research integration | Research framework |
<!--score: {bv:4, tc:3, rr:4, le:3, effort:6, lessons:4, deps:[]}-->
<!--score_total: 6.0-->
<!-- do_next: Research and design extraction schemas for improved data processing -->
<!-- est_hours: 8 -->
<!-- acceptance: Extraction schemas are research-backed and improve data quality -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#schema-design"] -->
<!-- reference_cards: ["500_reference-cards.md#research-based-design"] -->
<!-- PRD: 600_archives/prds/PRD-B-084-Research-Based-Schema-Design.md -->
<!-- completion_date: 2025-08-16 -->
<!-- implementation_notes: Successfully implemented research-based schema design system. Created scripts/research_based_schema_design.py with research analysis, pattern generation, schema creation, validation, and quality assessment. System extracts 44 findings from 20 research files, generates 4 research-based patterns (span-level grounding, multi-stage retrieval, metadata governance, DSPy assertions), and creates validated schemas for documentation, code, and research content types. Comprehensive test suite with 14 tests validates all functionality. Research coverage: 75%, average patterns per schema: 2.2, validation accuracy: 95%. System integrates with existing research infrastructure and provides foundation for improved extraction quality. PRD archived with complete metadata for lessons learned extraction (B-098). -->

| B-050 | Enhance 002 Task Generation with Automation | 🔥 | 5 | OK done | Automate task generation process for improved efficiency | Task automation + workflow enhancement | 600_archives/prds/PRD-B-050-Task-Generation-Automation.md |
<!--score: {bv:4, tc:3, rr:4, le:3, effort:5, lessons:4, deps:[]}-->
<!--score_total: 5.5-->
<!-- do_next: Implement automated task generation enhancements -->
<!-- est_hours: 6 -->
<!-- acceptance: Task generation is automated and produces higher quality tasks -->
<!-- completion_date: 2025-08-16 -->
<!-- implementation_notes: Created comprehensive task generation automation system with PRD parsing, backlog parsing, task template generation, testing requirements automation, quality gates, and output formatting. Includes full test suite with 27 tests covering all functionality. System successfully generates tasks from both PRDs and backlog items with appropriate complexity-based testing and priority-based quality gates. -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#task-automation"] -->
<!-- reference_cards: ["500_reference-cards.md#workflow-automation"] -->
<!-- PRD: 000_core/PRD-B-050-Task-Generation-Automation.md -->

| B-052-f | Enhanced Repository Maintenance Safety System | 🔧 | 1 | todo | Improve repository maintenance safety with enhanced validation | Safety validation + repository management | B-052-a Safety & Lint Tests |
<!--score: {bv:3, tc:2, rr:3, le:3, effort:1, lessons:3, deps:["B-052-a"]}-->
<!--score_total: 5.1-->
<!-- do_next: Implement enhanced safety validation for repository maintenance -->
<!-- est_hours: 3 -->
<!-- acceptance: Repository maintenance operations are safer with enhanced validation -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#safety-validation"] -->
<!-- reference_cards: ["500_reference-cards.md#repository-safety"] -->

| B-052-b | Config Externalization to TOML + Ignore | 🔧 | 1 | todo | Externalize configuration to TOML files with proper ignore patterns | TOML configuration + git ignore patterns | None |
<!--score: {bv:3, tc:2, rr:3, le:3, effort:1, lessons:3, deps:[]}-->
<!--score_total: 5.0-->
<!-- do_next: Move configuration to TOML files with proper git ignore patterns -->
<!-- est_hours: 2 -->
<!-- acceptance: Configuration is externalized and properly ignored in version control -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#configuration-management"] -->
<!-- reference_cards: ["500_reference-cards.md#toml-configuration"] -->

| B-076 | Research-Based DSPy Assertions Implementation | 📈 | 4 | todo | Implement DSPy assertions based on research findings | DSPy + assertions + research integration | DSPy framework |
<!--score: {bv:3, tc:2, rr:3, le:3, effort:4, lessons:3, deps:[]}-->
<!--score_total: 4.8-->
<!-- do_next: Research and implement DSPy assertions for improved model reliability -->
<!-- est_hours: 6 -->
<!-- acceptance: DSPy assertions improve model reliability based on research -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#dspy-assertions"] -->
<!-- reference_cards: ["500_reference-cards.md#dspy-framework"] -->

| B-052-c | Hash-Cache + Optional Threading | 🔧 | 2 | todo | Implement hash-based caching with optional threading support | Caching + threading + performance optimization | None |
<!--score: {bv:3, tc:2, rr:3, le:3, effort:2, lessons:3, deps:[]}-->
<!--score_total: 4.5-->
<!-- do_next: Implement hash-based caching system with optional threading -->
<!-- est_hours: 4 -->
<!-- acceptance: Hash-based caching improves performance with optional threading support -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#caching-patterns"] -->
<!-- reference_cards: ["500_reference-cards.md#performance-optimization"] -->

| B-018 | Local Notification System | ⭐ | 2 | todo | Improve local development experience with notifications | Desktop notifications + local system integration | Local system APIs |
<!--score: {bv:3, tc:2, rr:2, le:2, effort:2, lessons:3, deps:[]}-->
<!--score_total: 4.5-->
<!-- do_next: Implement local notification system for development feedback -->
<!-- est_hours: 4 -->
<!-- acceptance: Local notifications improve development experience and feedback -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#notification-systems"] -->
<!-- reference_cards: ["500_reference-cards.md#local-development"] -->

| B-043 | LangExtract Pilot w/ Stratified 20-doc Set | 📈 | 3 | todo | Pilot LangExtract with stratified document set for validation | LangExtract + document processing + validation | LangExtract framework |
<!--score: {bv:3, tc:2, rr:3, le:3, effort:3, lessons:3, deps:[]}-->
<!--score_total: 4.2-->
<!-- do_next: Implement LangExtract pilot with stratified document validation -->
<!-- est_hours: 5 -->
<!-- acceptance: LangExtract pilot validates extraction quality with stratified documents -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#extraction-validation"] -->
<!-- reference_cards: ["500_reference-cards.md#langextract"] -->

| B-044 | n8n LangExtract Service (Stateless, Spillover, Override) | 📈 | 3 | todo | Create stateless n8n service for LangExtract with spillover and override | n8n + LangExtract + service architecture | n8n workflow system |
<!--score: {bv:3, tc:2, rr:3, le:3, effort:3, lessons:3, deps:[]}-->
<!--score_total: 4.2-->
<!-- do_next: Implement stateless n8n LangExtract service with advanced features -->
<!-- est_hours: 5 -->
<!-- acceptance: n8n LangExtract service handles stateless processing with spillover and override -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#service-architecture"] -->
<!-- reference_cards: ["500_reference-cards.md#n8n-workflows"] -->

| B-078 | LangExtract Structured Extraction Service | 📈 | 3 | todo | Implement structured extraction service using LangExtract | LangExtract + structured extraction + service design | LangExtract framework |
<!--score: {bv:3, tc:2, rr:3, le:3, effort:3, lessons:3, deps:[]}-->
<!--score_total: 4.2-->
<!-- do_next: Build structured extraction service using LangExtract framework -->
<!-- est_hours: 5 -->
<!-- acceptance: Structured extraction service provides reliable data extraction -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#structured-extraction"] -->
<!-- reference_cards: ["500_reference-cards.md#extraction-services"] -->

| B-098 | Mine Archived PRDs for Lessons and Reference Cards | 🧠 | 5 | todo | Extract systematic lessons and cross-references from archived PRDs (600_) to feed into lessons_applied, reference_cards, and backlog hygiene | PRD analysis + lessons extraction + reference card creation | 600_archives/ |
<!--score: {bv:4, tc:3, rr:3, le:5, lessons:4, effort:3, deps:[]}-->
<!--score_total: 3.8-->
<!-- do_next: Design script/workflow to parse archived PRDs -->
<!-- est_hours: 5 -->
<!-- acceptance: At least 3 lessons and 2 reference cards extracted -->
<!-- lessons_applied: [] -->
<!-- reference_cards: [] -->

| B-099 | Enhanced Backlog Status Tracking with Timestamps | 🔧 | 1 | OK done| Add started_at, last_updated timestamps and stale item detection for better in-progress tracking | Timestamp tracking + stale detection + automated alerts | None |
<!-- last_updated: 2025-08-16T08:41:45.155925 -->
<!-- started_at: 2025-08-16T08:40:01.163126 -->
<!-- completion_date: 2025-08-16 -->
<!-- implementation_notes: Successfully implemented enhanced backlog status tracking with timestamps and stale item detection. Created scripts/enhanced_backlog_tracking.py with comprehensive tracking capabilities including started_at, last_updated timestamps, stale item detection, and automated alerts. System provides CLI interface for starting work, updating status, checking stale items, and generating item summaries. Supports configurable stale thresholds and maintains timestamp history in HTML comments. -->
<!--score: {bv:4, tc:2, rr:3, le:3, effort:1, lessons:3, deps:[]}-->
<!--score_total: 4.5-->
<!-- do_next: Implement enhanced status tracking with timestamps and stale item detection -->
<!-- est_hours: 3 -->
<!-- acceptance: Backlog items track when work started and flag stale in-progress items -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#status-tracking"] -->
<!-- reference_cards: ["500_reference-cards.md#backlog-management"] -->

| B-107 | Node Version Consistency & Tooling Standardization | 🔧 | 1 | todo | Pin Node 20 LTS across dev and CI; enforce via engines and CI to prevent drift | Node.js + npm + GitHub Actions | None |
| B-001 | Fix the notification system | 🔧 | 3 | todo | Fix the notification system | None | None |
| B-108 | Single Doorway Automation (3-command flow) | 🔧 | 3 | todo | Single Doorway Automation (3-command flow) | None | None |
<!--score: {bv:4, tc:3, rr:4, le:3, effort:1, deps:[]}-->
<!--score_total: 7.5-->
<!-- do_next: Add .nvmrc and .node-version (20.18.0); add engines and packageManager to config/package.json; add .npmrc with engine-strict=true; add setup-node lint CI -->
<!-- est_hours: 1 -->
<!-- acceptance: Node 20 LTS pinned (.nvmrc/.node-version); npm install enforces engines; CI uses actions/setup-node@v4 20.x and runs npm run lint on clean checkout; green run verified -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#repository-safety"] -->
<!-- reference_cards: ["500_reference-cards.md#github-actions"] -->

## Backlog Working Agreements

- WIP limit: at most 2 items may be marked in-progress at any time.

- Status normalization: use only `todo`, `in-progress`, `blocked`, `done`.

- Next actionable: every `todo` should include a one-line `do_next` metadata to enable immediate start.

- Blockers: note `blocked_by` when external dependencies (credentials, infra, decisions) apply.

- Acceptance criteria: add an `acceptance` note or PRD link to enable quick verification.

- Estimated hours: include `est_hours` (2-4h granularity) to improve planning.

- Grooming cadence: add `review_on` dates and sweep monthly to reduce drift.

- Ordering: keep this table ordered by score, then dependencies; append new items at the end.

- Tooling flags: use booleans like `needs_strict_anchors` or `needs_precommit_gate` for rollout items.

Metadata fields (HTML comments under each item):

- `<!-- do_next: ... -->`, `<!-- blocked_by: ... -->`, `<!-- acceptance: ... -->`, `<!-- est_hours: N -->`, `<!--
review_on: YYYY-MM-DD -->`

## 🗺️ Roadmap Integration

This backlog is the **executable roadmap** for the AI development ecosystem. Each item connects to strategic goals:

### **Strategic Alignment**
- **P0 Items**: Critical path for system stability and core functionality
- **P1 Items**: High-value features that advance the AI development ecosystem
- **P2 Items**: Performance and optimization improvements

### **Roadmap Connection**
- **Current Focus**: Lean Hybrid Memory System + Consensus Framework
- **Next Phase**: Advanced RAG & Extraction (B-043, B-044, B-078)
- **Future Phase**: Performance & Benchmarking (B-076, B-052-c)

### **Cross-References**
- **Development Roadmap**: `000_core/004_development-roadmap.md`
- **System Overview**: `400_guides/400_system-overview.md`
- **Memory Context**: `100_memory/100_cursor-memory-context.md`

<!-- ANCHOR: completed-items-context-preservation -->
## Completed Items Context Preservation

### **Core System Foundation (Completed)**
| ID | Title | Completion Date | Key Outcomes | Lessons Applied |
|---|---|---|---|---|
| B-000 | v0.3.1-rc3 Core Hardening | 2024-08-05 | Production-ready security and reliability | Security-first approach, comprehensive testing |
| B-001 | Real-time Mission Dashboard | 2024-08-06 | Live visibility into AI task execution | Real-time monitoring essential for AI development |
| B-002 | Advanced Error Recovery & Prevention | 2024-08-07 | Intelligent error handling and HotFix generation | Automated error recovery reduces development friction |
| B-011 | Cursor Native AI + Specialized Agents | 2024-08-07 | AI code generation with specialized agents | Native-first approach provides best performance |

### **Documentation & Context Management (Completed)**
| ID | Title | Completion Date | Key Outcomes | Lessons Applied |
|---|---|---|---|---|
| B-070 | AI Constitution Implementation | 2024-08-07 | Persistent AI ruleset for safety | Constitutional approach prevents context loss |
| B-071 | Memory Context File Splitting | 2024-08-07 | Modular memory system | Modular documentation improves AI comprehension |
| B-072 | Documentation Retrieval System | 2024-08-07 | RAG for documentation context | RAG solves context overload in AI development |
| B-073 | Giant Guide File Splitting | 2024-08-07 | Focused 200-300 line modules | Smaller files improve attention and comprehension |

### **Infrastructure & Automation (Completed)**
| ID | Title | Completion Date | Key Outcomes | Lessons Applied |
|---|---|---|---|---|
| B-003 | Production Security & Monitoring | 2024-08-05 | File validation + OpenTelemetry | Security monitoring essential for AI systems |
| B-004 | n8n Backlog Scrubber Workflow | 2024-08-06 | Automated scoring and prioritization | Automation reduces cognitive load in planning |
| B-010 | n8n Workflow Integration | 2024-08-06 | Automated task execution | Workflow automation enables systematic development |
| B-060 | Documentation Coherence Validation | 2024-08-07 | Lightweight doc-linter with Cursor AI | Validation prevents documentation drift |

### **Key Lessons Learned**
1. **Security First**: All AI systems need comprehensive security validation
2. **Modular Design**: Smaller, focused files improve AI comprehension
3. **Automation Reduces Friction**: Automated workflows enable systematic development
4. **Real-time Monitoring**: Essential for AI development ecosystem visibility
5. **Constitutional Approach**: Prevents context loss and ensures safety

### **Context Preservation Strategy**
- **Completed items** are archived here for historical context
- **Key outcomes** and **lessons applied** are preserved for future reference
- **Cross-references** to lessons learned in `100_memory/105_lessons-learned-context.md`
- **Strategic alignment** with development roadmap maintained

| B-091 | Strict Anchor Enforcement (Phase 2) | 🔥 | 2 | todo | Enforce heading-based anchors; disallow non-TLDR HTML
anchors in core docs | Validator (--strict-anchors) + pre-commit/CI | 200_naming-conventions.md,
scripts/doc_coherence_validator.py |
<!--score: {bv:5, tc:3, rr:4, le:3, effort:2,
deps:["200_naming-conventions.md","scripts/doc_coherence_validator.py"]}-->
<!--score_total: 7.5-->
<!-- do_next: Enable --strict-anchors in CI for core docs and update pre-commit to reflect policy -->
<!-- est_hours: 2 -->
<!-- acceptance: Validator fails on any non-TLDR explicit anchors in core docs; CI green after change -->

| B-092 | Retrieval Output: At-a-Glance Integration | ⭐ | 2 | todo | Show At-a-glance (what/read/do next) for sources in
search/context outputs | documentation_retrieval_cli.py + index metadata | scripts/documentation_indexer.py |
<!--score: {bv:4, tc:2, rr:2, le:3, effort:2, deps:["scripts/documentation_indexer.py"]}-->
<!--score_total: 5.5-->
<!-- do_next: Print At-a-glance (what/read/do next) for each source in CLI 'context' and 'search' outputs -->
<!-- est_hours: 3 -->
<!-- acceptance: CLI output includes At-a-glance for at least 3 core sources in summary/text modes -->

| B-093 | Validator Performance Optimizations | 📈 | 3 | todo | Speed up local runs with parallel IO and cached anchor
maps | Python threading + cached scans | scripts/doc_coherence_validator.py |
<!--score: {bv:3, tc:2, rr:2, le:3, effort:3, deps:["scripts/doc_coherence_validator.py"]}-->
<!--score_total: 3.3-->
<!-- do_next: Add parallel IO for file reads and cache anchor map across tasks -->
<!-- est_hours: 4 -->
<!-- acceptance: 2x speedup measured on only-changed runs on a representative commit -->

| B-094 | MCP Memory Rehydrator Server | 🔥 | 3 | todo | Create minimal MCP server to automate database-based memory rehydration in Cursor | MCP Server + HTTP transport + Cursor integration | scripts/cursor_memory_rehydrate.py |
<!--score: {bv:5, tc:4, rr:5, le:4, effort:3, lessons:4, deps:["scripts/cursor_memory_rehydrate.py"]}-->
<!--score_total: 9.5-->
<!-- do_next: Create basic MCP server that wraps existing memory rehydrator and exposes it as a tool -->
<!-- est_hours: 3 -->
<!-- acceptance: Cursor automatically connects to MCP server and can call memory rehydration tool -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#mcp-integration-patterns"] -->
<!-- reference_cards: ["500_reference-cards.md#mcp-server-architecture"] -->

| B-095 | MCP Server Role Auto-Detection | 🔥 | 2 | todo | Enhance MCP server to automatically detect role based on conversation context | Context analysis + role detection + dynamic tool selection | B-094 MCP Memory Rehydrator Server |
<!--score: {bv:5, tc:3, rr:4, le:3, effort:2, lessons:3, deps:["B-094"]}-->
<!--score_total: 7.5-->
<!-- do_next: Add conversation context analysis to automatically select appropriate role -->
<!-- est_hours: 2 -->
<!-- acceptance: MCP server automatically detects planner/implementer/researcher role from conversation -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#role-detection-patterns"] -->
<!-- reference_cards: ["500_reference-cards.md#context-analysis"] -->

| B-096 | MCP Server Performance Optimization | 📈 | 2 | todo | Optimize MCP server for low latency and high throughput | Connection pooling + caching + async processing | B-094 MCP Memory Rehydrator Server |
<!--score: {bv:4, tc:3, rr:3, le:3, effort:2, lessons:3, deps:["B-094"]}-->
<!--score_total: 5.5-->
<!-- do_next: Implement connection pooling and response caching for faster context retrieval -->
<!-- est_hours: 2 -->
<!-- acceptance: MCP server responds in <500ms for context requests -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#performance-optimization"] -->
<!-- reference_cards: ["500_reference-cards.md#connection-pooling"] -->

| B-097 | Roadmap Milestones & Burndown Charts | 📊 | 3 | todo | Add milestone tracking and burndown charts to roadmap for progress visibility | Milestone definition + progress tracking + chart generation | 000_core/004_development-roadmap.md |
<!--score: {bv:4, tc:3, rr:4, le:3, effort:3, lessons:3, deps:["000_core/004_development-roadmap.md"]}-->
<!--score_total: 6.0-->
<!-- do_next: Define milestone structure and implement burndown chart generation -->
<!-- est_hours: 3 -->
<!-- acceptance: Roadmap shows milestone progress and burndown charts for sprint tracking -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#project-tracking"] -->
<!-- reference_cards: ["500_reference-cards.md#agile-tracking"] -->

- --

| B-070 | AI Constitution Implementation | 🔥 | 3 | OK done | Create persistent AI ruleset to prevent context loss and
ensure safety | System prompt + critical rules | Documentation context management |
<!--score: {bv:5, tc:3, rr:5, le:4, effort:3, deps:[]}-->
<!--score_total: 5.7-->
<!--research: 500_research-analysis-summary.md - AI documentation consumption research shows critical rules get lost in
large files-->
<!--progress: Complete implementation with comprehensive AI Constitution, compliance checker, integration with core
system files, comprehensive test suite, and validation framework-->
<!--completion_date: 2024-08-07-->
<!--implementation_notes: Created 400_ai-constitution.md with 5 articles covering file safety, context preservation,
error prevention, documentation management, and system integration. Implemented
scripts/constitution_compliance_checker.py with validation framework and tests/test_constitution_compliance.py with
comprehensive test suite. Integrated constitution references into 100_memory/100_cursor-memory-context.md and
000_core/003_process-task-list.md. Constitution provides persistent rules to prevent context loss and ensure safety
across all AI
operations.-->
| B-071 | Memory Context File Splitting | 🔥 | 4 | OK done | Split 378-line memory file into focused modules for better AI
consumption | File organization + cross-references | B-070 AI Constitution Implementation |
<!--score: {bv:5, tc:4, rr:5, le:4, effort:4, deps:[]}-->
<!--score_total: 4.5-->
<!--research: 500_documentation-coherence-research.md - Modular documentation patterns improve AI comprehension-->
<!--progress: Complete implementation with modular memory context system, migration script, cross-reference updates, and
comprehensive documentation-->
<!--completion_date: 2024-08-07-->
<!--implementation_notes: Split 100_memory/100_cursor-memory-context.md (384 lines) into 5 focused modules:
100_memory/100_cursor-memory-context.md (primary entry point), 101_memory-context-safety.md (safety requirements),
102_memory-context-state.md (project state), 103_memory-context-workflow.md (development process),
104_memory-context-guidance.md (context-specific help). Created scripts/migrate_memory_context.py to update 47 files
with cross-references. Migration successful with 0 errors. Modular system improves AI comprehension and reduces context
overload.-->
| B-072 | Documentation Retrieval System Enhancement | 🔥 | 5 | OK done | Implement RAG for documentation to provide
relevant context on-demand | PGVector + DSPy + retrieval | B-031 Vector Database Enhancement |
<!--score: {bv:5, tc:4, rr:5, le:5, effort:5, deps:[]}-->
<!--score_total: 4.8-->
<!--research: 500_research-implementation-summary.md - Industry analysis shows RAG solves context overload-->
<!--progress: Complete implementation with documentation indexer, retrieval service, CLI interface, comprehensive
testing, and integration guide-->
<!--completion_date: 2024-08-07-->
<!--implementation_notes: Implemented scripts/documentation_indexer.py for automatic documentation scanning and
indexing, dspy-rag-system/src/dspy_modules/documentation_retrieval.py for RAG-based context provision,
scripts/documentation_retrieval_cli.py for easy command-line access, tests/test_documentation_retrieval.py for
comprehensive testing, and 400_guides/400_documentation-guide.md for complete usage guide. System provides
relevant
context on-demand to solve context overload, with confidence scoring, category filtering, and multi-source synthesis.-->
| B-073 | Giant Guide File Splitting | 📈 | 8 | OK done | Split 1,400+ line guide files into focused 200-300 line modules
| File organization + content analysis | B-071 Memory Context File Splitting |
<!--score: {bv:4, tc:3, rr:4, le:3, effort:8, deps:[]}-->
<!--score_total: 2.0-->
<!--research: 500_maintenance-safety-research.md - Research shows files over 300 lines cause attention dilution-->
<!--progress: Complete implementation with giant guide splitter, migration script, cross-reference updates, and
comprehensive documentation-->
<!--completion_date: 2024-08-07-->
<!--implementation_notes: Implemented scripts/split_giant_guides.py to split 8 large guide files (1,400+ lines) into
focused 200-300 line modules, scripts/migrate_giant_guide_references.py to update cross-references, and comprehensive
migration summary. Consolidated 400_guides/400_contributing-guidelines.md into single file for solo developer workflow.
Excluded
project-specific deliverables (B-011, B-049, B-072 files) as they should remain intact. System improves AI comprehension
and reduces attention dilution by providing focused, digestible documentation modules.-->
| B-074 | Multi-Turn Process Enforcement | 📈 | 6 | todo | Implement mandatory checklist enforcement for high-risk
operations | Multi-turn prompts + validation | B-070 AI Constitution Implementation |
<!--score: {bv:4, tc:3, rr:4, le:3, effort:6, deps:[]}-->
<!--score_total: 2.8-->
<!--research: 500_research-analysis-summary.md - Mandatory process enforcement patterns prevent context misses-->
| B-075 | Quick Reference System Implementation | ⭐ | 3 | todo | Add 30-second scan sections to all critical files for
rapid context | Documentation templates + quick refs | B-071 Memory Context File Splitting |
<!--score: {bv:3, tc:2, rr:3, le:2, effort:3, deps:[]}-->
<!--score_total: 3.3-->
<!--research: 500_documentation-coherence-research.md - Quick reference patterns ensure key points are available-->
| B-076 | B-011 Project File Cleanup | ⭐ | 2 | todo | Archive B-011 project files and extract essential info to core
docs | File archiving + content extraction | B-073 Giant Guide File Splitting |
<!--score: {bv:2, tc:1, rr:2, le:1, effort:2, deps:[]}-->
<!--score_total: 4.0-->
<!--research: 500_maintenance-safety-research.md - Legacy file cleanup improves documentation coherence-->
| B-077 | Documentation Context Monitoring | 📈 | 4 | todo | Implement monitoring for context failures and documentation
QA loop | Monitoring + feedback system | B-072 Documentation Retrieval System Enhancement |
<!--score: {bv:3, tc:2, rr:4, le:3, effort:4, deps:[]}-->
<!--score_total: 3.0-->
<!--research: 500_research-analysis-summary.md - Ongoing QA loop prevents context drift-->
<!-- human_required: true -->
<!-- reason: Requires GitHub repository configuration and CI/CD setup decisions -->

| B-043 | LangExtract Pilot w/ Stratified 20-doc Set | 🔥 | 3 | todo | Evaluate LangExtract vs. manual extraction for
transcript pipeline | LangExtract + Gemini Flash + Validation | Extraction Pipeline |
<!--score: {bv:4, tc:3, rr:3, le:4, effort:3, deps:[]}-->
<!--score_total: 4.2-->
<!--research: 500_research-analysis-summary.md - LangExtract integration critical for structured extraction-->

| B-044 | n8n LangExtract Service (Stateless, Spillover, Override) | 📈 | 3 | todo | Build n8n node for LangExtract with
configurable extraction | n8n + LangExtract + POST /extract endpoint | B-043 LangExtract Pilot |
<!--score: {bv:4, tc:3, rr:3, le:4, effort:3, deps:["B-043"]}-->
<!--score_total: 4.2-->

| B-045 | RAG Schema Patch (Span*, Validated_flag, Raw_score) | 🔧 | 1 | todo | Update RAG schema for span-level
grounding and validation | PostgreSQL + Schema Migration + Zero Downtime | B-044 n8n LangExtract Service |
<!--score: {bv:3, tc:2, rr:2, le:4, effort:1, deps:["B-044"]}-->
<!--score_total: 3.0-->

| B-046 | Cursor Native AI Context Engineering with DSPy | 🔥 | 5 | OK done | Implement intelligent model routing for
Cursor's native AI models using DSPy context engineering | DSPy + Context Engineering + Model Routing | B-011 Cursor
Native AI Integration |
<!--score: {bv:5, tc:4, rr:5, le:5, effort:5, deps:["B-011"]}-->
<!--score_total: 4.8-->
<!--research: Leverages DSPy for intelligent model selection based on task characteristics and prompt patterns-->
<!--context: Integrates with existing DSPy RAG system for enhanced model routing capabilities-->
<!--progress: Complete implementation with context engineering router, validation system, monitoring dashboard,
comprehensive testing, and integration with existing DSPy RAG system-->
<!--completion_date: 2024-08-07-->
<!--implementation_notes: Implemented cursor_model_router.py with ModelRoutingValidator and ModelRoutingMonitor,
integrated with enhanced_rag_system.py, created test_validation_and_monitoring.py and monitor_context_engineering.py,
added comprehensive documentation in 400_cursor-context-engineering-guide.md (compatibility appendix), created
verify_setup_compatibility.py for setup verification-->

| B-047 | Auto-router (Inline vs Remote Extraction) | 🔧 | 2 | todo | Implement smart routing for extraction based on
document size | Router Logic + Config Flags + Latency Optimization | B-044 n8n LangExtract Service |
<!--score: {bv:3, tc:3, rr:2, le:3, effort:2, deps:["B-044"]}-->
<!--score_total: 3.3-->

| B-048 | Confidence Calibration (Blocked) | 🔧 | 3 | todo | Calibrate confidence scores with isotonic regression |
Calibration + 2k Gold Spans + Probability Mapping | B-046 4-way Benchmark |
<!--score: {bv:3, tc:2, rr:2, le:3, effort:3, deps:["B-046"]}-->
<!--score_total: 2.8-->

| B-049 | Convert 003 Process Task List to Python Script | 🔥 | 3 | OK done | Automate core execution engine for all
backlog items | Python CLI + State Management + Error Handling | Core Workflow |
<!--score: {bv:5, tc:4, rr:4, le:4, effort:3, deps:[]}-->
<!--score_total: 5.3-->
<!--progress: Complete implementation with comprehensive CLI script, backlog parser, state management, error handling,
and task execution engine-->

| B-076 | Research-Based DSPy Assertions Implementation | 🔥 | 3 | todo | Implement DSPy assertions for code validation
and reliability improvement | DSPy Assertions + Code Validation + Reliability Enhancement | B-011 Cursor Native AI
Integration |
<!--score: {bv:5, tc:4, rr:5, le:4, effort:3, deps:["B-011"]}-->
<!--score_total: 4.8-->
<!--research: 500_dspy-research.md - DSPy assertions provide 37% → 98% reliability improvement-->

| B-077 | Hybrid Search Implementation (Dense + Sparse) | 🔥 | 4 | OK done | Implement hybrid search combining PGVector and
PostgreSQL full-text | Hybrid Search + Span-Level Grounding + Intelligent Merging | B-045 RAG Schema Patch |
<!--acceptance: Meets EXCELLENT quality gates: Vector <100ms, Hybrid <200ms, Recall@10 ≥0.8, Memory Rehydration <5s-->
<!--score: {bv:5, tc:4, rr:5, le:4, effort:4, deps:["B-045"]}-->
<!--score_total: 4.5-->
<!--research: 500_rag-system-research.md - Hybrid search improves accuracy by 10-25%-->

| B-078 | LangExtract Structured Extraction Service | 🔥 | 3 | todo | Implement LangExtract with span-level grounding and
validation | LangExtract + Schema Design + Validation Layer | B-043 LangExtract Pilot |
<!--score: {bv:5, tc:4, rr:4, le:4, effort:3, deps:["B-043"]}-->
<!--score_total: 4.2-->
<!--research: 500_research-analysis-summary.md - Span-level grounding enables precise fact extraction-->

| B-079 | Teleprompter Optimization for Continuous Improvement | 📈 | 2 | todo | Implement automatic prompt optimization
using DSPy teleprompter | Teleprompter + Few-Shot Examples + Continuous Improvement | B-076 DSPy Assertions |
<!--score: {bv:4, tc:3, rr:4, le:3, effort:2, deps:["B-076"]}-->
<!--score_total: 4.0-->
<!--research: 500_dspy-research.md - Teleprompter optimization for continuous improvement-->

| B-080 | Research-Based Performance Monitoring | 📈 | 3 | todo | Implement research-based monitoring with OpenTelemetry
and metrics | OpenTelemetry + Performance Metrics + Research Validation | B-077 Hybrid Search |
<!--score: {bv:4, tc:3, rr:4, le:3, effort:3, deps:["B-077"]}-->
<!--score_total: 3.7-->
<!--research: 500_research-analysis-summary.md - Production monitoring critical for system reliability-->

| B-050 | Enhance 002 Task Generation with Automation | 📈 | 2 | todo | Add automation to task generation workflow | Task
Parsing + Dependency Analysis + Template Generation | B-049 003 Script |
<!--score: {bv:4, tc:3, rr:3, le:3, effort:2, deps:["B-049"]}-->
<!--score_total: 5.5-->

| B-051 | Create PRD Skeleton Generator for 001 | 🔧 | 1 | todo | Add light automation to PRD creation workflow |
Skeleton Generation + Template Pre-fill + Cursor Integration | B-050 002 Enhancement |
<!--score: {bv:3, tc:2, rr:2, le:2, effort:1, deps:["B-050"]}-->
<!--score_total: 4.0-->

| B-052-a | Safety & Lint Tests for repo-maintenance | 🔧 | 1 | OK done | Add pre-flight git check, word-boundary regex,
and unit tests | Git Safety + Regex Fix + Pytest Coverage | Maintenance Automation |
<!--score: {bv:4, tc:3, rr:3, le:3, effort:1, deps:[]}-->
<!--score_total: 9.0-->
<!--progress: Pre-flight git check, word-boundary regex, and comprehensive unit tests implemented-->

| B-052-b | Config Externalization to TOML + Ignore | 🔧 | 1 | todo | Move hard-coded patterns to TOML config and add
.maintenanceignore | TOML Config + Ignore File + Pattern Management | B-052-a Safety & Lint Tests |
<!--score: {bv:3, tc:2, rr:2, le:3, effort:1, deps:["B-052-a"]}-->
<!--score_total: 5.0-->

| B-052-c | Hash-Cache + Optional Threading | 🔧 | 1 | todo | Add hash caching and profile-based threading for
performance | Hash Caching + Performance Profiling + Threading | B-052-b Config Externalization |
<!--score: {bv:3, tc:2, rr:2, le:2, effort:1, deps:["B-052-b"]}-->
<!--score_total: 4.5-->

| B-052-d | CI GitHub Action (Dry-Run Gate) | 🔧 | 0.5 | todo | Add GitHub Action to run maintenance script on PRs |
GitHub Actions + Dry-Run + PR Gate | B-052-a Safety & Lint Tests |
<!--score: {bv:3, tc:2, rr:2, le:2, effort:0.5, deps:["B-052-a"]}-->
<!--score_total: 8.0-->

| B-052-e | Auto-Push Prompt for Repo Maintenance | 🔧 | 1 | OK done | Add interactive prompt to push changes to GitHub
after maintenance | Interactive Prompt + Git Status Check + User Confirmation | B-052-a Safety & Lint Tests |
<!--score: {bv:4, tc:3, rr:3, le:3, effort:1, deps:["B-052-a"]}-->
<!--score_total: 9.0-->
<!--progress: Complete implementation with interactive prompt, git status checks, user confirmation, and shell wrapper-->

| B-052-f | Enhanced Repository Maintenance Safety System | 🔥 | 3.5 | todo | Implement comprehensive safety system to
prevent critical file archiving | Reference Tracking + Critical File Protection + Git Hooks + Recovery | B-052-a Safety
& Lint Tests |
<!--score: {bv:5, tc:4, rr:5, le:4, effort:3.5, deps:["B-052-a"]}-->
<!--score_total: 5.1-->
<!--progress: Consensus reached on multi-layer safety approach with local-first implementation-->

| B-060 | Documentation Coherence Validation System | 🔥 | 2 | OK done | Implement lightweight doc-linter with Cursor AI
semantic checking | Local Pre-commit Hooks + Cursor AI + Reference Validation | B-052-a Safety & Lint Tests |
<!--score: {bv:5, tc:4, rr:4, le:4, effort:2, deps:["B-052-a"]}-->
<!--score_total: 5.3-->
<!--progress: Complete implementation with comprehensive validation system, pre-commit hooks, test suite, and
documentation-->

| B-061 | Memory Context Auto-Update Helper | 🔧 | 1 | OK done | Create script to update memory context from backlog with
fenced sections | Backlog → Memory Helper + Fenced Sections + Dry-run | B-060 Documentation Coherence Validation System
|
<!--score: {bv:4, tc:3, rr:3, le:3, effort:1, deps:["B-060"]}-->
<!--score_total: 9.0-->
<!--progress: Complete implementation with fenced sections, dry-run mode, improved parsing, and better error handling-->

| B-062 | Context Priority Guide Auto-Generation | 🔧 | 0.5 | todo | Create regen_guide.py to auto-generate context
priority guide from file headers | Guide Generation + Cross-Reference Aggregation + Tier Lists | B-060 Documentation
Coherence Validation System |
<!--score: {bv:3, tc:2, rr:2, le:2, effort:0.5, deps:["B-060"]}-->
<!--score_total: 8.0-->

| B-063 | Documentation Recovery & Rollback System | 🔧 | 1 | OK done | Implement rollback_doc.sh and git snapshot system
for doc recovery | Git Snapshots + Rollback Script + Dashboard Integration | B-060 Documentation Coherence Validation
System |
<!--score: {bv:4, tc:3, rr:3, le:3, effort:1, deps:["B-060"]}-->
<!--score_total: 9.0-->
<!--progress: Complete implementation with git snapshot system, rollback functionality, status monitoring, and proper error handling-->

| B-064 | Naming Convention Category Table | 🔧 | 0.5 | OK done | Add category table to 200_naming-conventions.md
clarifying current buckets | Category Documentation + Prefix Clarification + No Mass Renaming | B-060 Documentation
Coherence Validation System |
<!--score: {bv:3, tc:2, rr:2, le:2, effort:0.5, deps:["B-060"]}-->
<!--score_total: 8.0-->

| B-065 | Error Recovery & Troubleshooting Guide | 🔥 | 2 | OK done | Create comprehensive guide for handling common
issues and recovery procedures | Error Patterns + Recovery Procedures + Debugging Workflows | B-060 Documentation
Coherence Validation System |
<!--score: {bv:5, tc:4, rr:4, le:4, effort:2, deps:["B-060"]}-->
<!--score_total: 5.3-->
<!--progress: Complete implementation with comprehensive troubleshooting guide, automated recovery scripts, and
systematic workflows-->

| B-066 | Security Best Practices & Threat Model | 🔥 | 3 | OK done | Create comprehensive security documentation and
threat model | Threat Model + Security Guidelines + Incident Response | B-065 Error Recovery Guide |
<!--score: {bv:5, tc:4, rr:5, le:4, effort:3, deps:["B-065"]}-->
<!--score_total: 4.8-->
<!--progress: Complete implementation with comprehensive security documentation, threat model, incident response
procedures, and security monitoring guidelines-->

| B-067 | Performance Optimization & Monitoring Guide | 📈 | 2 | OK done | Create guide for system performance,
monitoring, and optimization | Performance Metrics + Optimization Strategies + Monitoring Setup | B-065 Error Recovery
Guide |
<!--score: {bv:4, tc:3, rr:3, le:3, effort:2, deps:["B-065"]}-->
<!--score_total: 4.5-->
<!--progress: Complete implementation with comprehensive performance metrics, optimization strategies, monitoring setup,
scaling guidelines, and performance testing tools-->

| B-068 | Integration Patterns & API Documentation | 📈 | 2 | OK done | Create documentation on how different components
integrate | API Documentation + Integration Patterns + Component Communication | B-067 Performance Optimization Guide |
<!--score: {bv:4, tc:3, rr:3, le:3, effort:2, deps:["B-067"]}-->
<!--score_total: 4.5-->
<!--progress: Complete implementation with comprehensive API design, component integration, communication patterns,
error handling, security integration, and deployment integration-->

| B-069 | Testing Strategy & Quality Assurance Guide | 📈 | 2 | OK done | Create comprehensive testing documentation and
quality assurance | Testing Approaches + Quality Gates + Test Automation | B-068 Integration Patterns Guide |
<!--score: {bv:4, tc:3, rr:3, le:3, effort:2, deps:["B-068"]}-->
<!--score_total: 4.5-->
<!--progress: Complete implementation with comprehensive testing strategy, quality gates, AI model testing, continuous
testing, and quality metrics-->

| B-070 | Deployment & Environment Management Guide | 📈 | 2 | OK done | Create guide for deployment processes and
environment setup | Deployment Procedures + Environment Management + Production Setup | B-069 Testing Strategy Guide |
<!--score: {bv:4, tc:3, rr:3, le:3, effort:2, deps:["B-069"]}-->
<!--score_total: 4.5-->
<!--progress: Complete implementation with comprehensive deployment procedures, environment management, production
setup, monitoring, rollback procedures, and deployment automation-->

| B-071 | Contributing Guidelines & Development Standards | 🔧 | 1 | OK done | Create guidelines for contributing to the
project and development standards | Code Standards + Contribution Process + Review Guidelines | B-070 Deployment Guide |
<!--score: {bv:3, tc:2, rr:2, le:2, effort:1, deps:["B-070"]}-->
<!--score_total: 6.0-->
<!--progress: Complete implementation with comprehensive development standards, code guidelines, contribution process,
review guidelines, documentation standards, testing standards, security standards, performance standards, deployment
standards, and quality assurance-->

| B-072 | Migration & Upgrade Procedures Guide | 🔧 | 1 | OK done | Create documentation on system migrations and upgrades
| Upgrade Procedures + Migration Strategies + Rollback Procedures | B-071 Contributing Guidelines |
<!--score: {bv:3, tc:2, rr:2, le:2, effort:1, deps:["B-071"]}-->
<!--score_total: 6.0-->
<!--progress: Complete implementation with comprehensive migration and upgrade procedures, validation framework,
automated scripts, rollback procedures, and emergency recovery procedures-->

| B-073 | Few-Shot Context Engineering Examples | 🔥 | 1 | OK done | Create AI context engineering examples for coherence
validation | Few-Shot Examples + AI Pattern Recognition + Context Engineering | B-060 Documentation Coherence Validation
System |
<!--score: {bv:5, tc:3, rr:4, le:4, effort:1, deps:["B-060"]}-->
<!--score_total: 6.7-->
<!--progress: Complete implementation with comprehensive few-shot examples for documentation coherence, backlog
analysis, memory context, code generation, error recovery, integration patterns, testing strategies, deployment
examples, and best practices-->

| B-074 | Few-Shot Integration with Documentation Tools | 🔧 | 0.5 | OK done | Integrate few-shot examples into doc-lint and
memory update scripts | Prompt Integration + Example Loading + AI Enhancement | B-073 Few-Shot Context Engineering
Examples |
<!--score: {bv:4, tc:2, rr:3, le:3, effort:0.5, deps:["B-073"]}-->
<!--score_total: 8.0-->
<!--progress: Simple integration using existing cursor.chat() patterns-->

| B-075 | Few-Shot Cognitive Scaffolding Integration | 🔧 | 0.5 | todo | Add few-shot examples to context priority guide
and memory context | Cross-Reference Integration + AI Discovery + Scaffolding Enhancement | B-074 Few-Shot Integration
with Documentation Tools |
<!--score: {bv:3, tc:2, rr:2, le:2, effort:0.5, deps:["B-074"]}-->
<!--score_total: 6.0-->
<!--progress: Integrate with existing HTML comment patterns for AI discovery-->

| B-081 | Research-Based Agent Orchestration Framework | 🔧 | 5 | todo | Implement multi-agent coordination with
specialized roles | Agent Orchestration + Natural Language Communication + Memory Management | B-076 DSPy Assertions |
<!--score: {bv:4, tc:3, rr:4, le:4, effort:5, deps:["B-076"]}-->
<!--score_total: 3.2-->
<!--research: 500_research-analysis-summary.md - Multi-agent approach is state-of-the-art-->

| B-082 | Research-Based Quality Evaluation Metrics | 🔧 | 2 | todo | Implement research-based evaluation metrics for
system quality | Quality Metrics + Precision/Recall + F1 Scoring | B-078 LangExtract Service |
<!--score: {bv:4, tc:3, rr:4, le:3, effort:2, deps:["B-078"]}-->
<!--score_total: 4.0-->
<!--research: 500_research-analysis-summary.md - Quality evaluation critical for validation-->

| B-083 | Research-Based Caching Strategy Implementation | 🔧 | 2 | todo | Implement research-based caching for
performance optimization | DSPy Caching + Redis Integration + Performance Optimization | B-079 Teleprompter Optimization
|
<!--score: {bv:4, tc:3, rr:3, le:3, effort:2, deps:["B-079"]}-->
<!--score_total: 3.8-->
<!--research: 500_dspy-research.md - DSPy caching provides 40-60% cost reduction-->

| B-084 | Research-Based Schema Design for Extraction | 🔧 | 1 | todo | Design structured schemas for backlog items and
documentation | Schema Design + Validation Rules + Span Tracking | B-078 LangExtract Service |
<!--score: {bv:4, tc:3, rr:3, le:3, effort:1, deps:["B-078"]}-->
<!--score_total: 6.0-->
<!--research: 500_research-analysis-summary.md - Schema design critical for structured extraction-->

- --

| B-014 | Agent Specialization Framework | 🔧 | 13 | todo | Enable domain-specific AI capabilities | Agent framework +
training | AI system |
<!--score: {bv:4, tc:1, rr:2, le:4, effort:13, deps:[]}-->
<!--score_total: 0.8-->
| B-015 | Learning Systems & Continuous Improvement | 🔧 | 13 | todo | System gets smarter over time | Pattern learning +
optimization | AI system |
<!--score: {bv:3, tc:1, rr:2, le:4, effort:13, deps:[]}-->
<!--score_total: 0.8-->
| B-016 | Advanced RAG Capabilities | 🔧 | 5 | todo | Enhance document processing and Q&A | Multi-modal + knowledge graph
| RAG system |
<!--score: {bv:4, tc:2, rr:3, le:3, effort:5, deps:[]}-->
<!--score_total: 2.4-->
| B-017 | Advanced DSPy Features | 🔧 | 5 | todo | Enhance AI reasoning capabilities | Multi-step chains + async | DSPy
system |
<!--score: {bv:4, tc:2, rr:2, le:3, effort:5, deps:[]}-->
<!--score_total: 2.2-->
| B-018 | Local Notification System | ⭐ | 2 | todo | Improve local development experience | Desktop notifications + logs
| Local system + APIs |
<!--score: {bv:3, tc:2, rr:2, le:2, effort:2, deps:[]}-->
<!--score_total: 4.5-->

- --

| B-019 | Code Quality Improvements | 🔧 | 5 | todo | Improve maintainability | Refactoring + documentation | Codebase |
<!--score: {bv:4, tc:3, rr:4, le:4, effort:5, lessons:4, deps:[]}-->
<!--score_total: 3.2-->
<!-- do_next: Audit codebase for technical debt and create refactoring plan -->
<!-- est_hours: 8 -->
<!-- acceptance: Code quality metrics improve by 20% and technical debt is documented -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#code-quality-patterns"] -->
<!-- reference_cards: ["500_reference-cards.md#refactoring-strategies"] -->
<!-- PRD: 001_create-prd.md#B-019 -->
| B-020 | Tokenizer Enhancements | 🔧 | 2 | todo | Improve text processing capabilities | SentencePiece + optimization |
Tokenizer |
| B-021 | Local Security Hardening | 🔧 | 3 | todo | Protect local development environment | Input validation + API
security | Local security + APIs |
| B-022 | Performance Monitoring | 🔧 | 2 | todo | Improve system observability | Metrics + alerts | Monitoring |
<!--score: {bv:3, tc:2, rr:3, le:3, effort:2, lessons:3, deps:[]}-->
<!--score_total: 4.5-->
<!-- do_next: Implement basic performance metrics collection and dashboard -->
<!-- est_hours: 4 -->
<!-- acceptance: System performance is measurable and alerts are configured -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#monitoring-patterns"] -->
<!-- reference_cards: ["500_reference-cards.md#observability-best-practices"] -->
| B-023 | Development Readiness Enhancements | 🔧 | 5 | todo | Ensure system stability for solo development | Performance
metrics + load testing | Development |
| B-024 | Automated Sprint Planning | 🔧 | 2 | todo | Automate sprint planning and backlog selection | AI planning +
automation | Backlog system |
| B-025 | Database Event-Driven Status Updates | 🔧 | 3 | todo | Automatically update backlog status via database events
| PostgreSQL triggers + event system | Event ledger |
| B-026 | Secrets Management | 🔥 | 2 | todo | Secure credential management with environment validation | Keyring + env
validation + startup checks | None |
<!-- human_required: true -->
<!-- reason: Requires business decisions on which secrets to manage and deployment configuration -->
| B-027 | Health & Readiness Endpoints | 🔥 | 2 | todo | Kubernetes-ready health checks with dependency monitoring |
/health + /ready endpoints + JSON status | None |
<!-- human_required: true -->
<!-- reason: Requires deployment environment configuration and business requirements for health checks -->
| B-028 | Implement regex prompt-sanitiser & whitelist | 🔥 | 3 | OK done | Enhanced prompt security with regex-based
sanitization | Regex patterns + whitelist logic + security validation | None |
| B-029 | Expose llm_timeout_seconds override in agents | 🔥 | 2 | OK done | Per-agent LLM timeout configuration for large
models | Agent timeout config | None |
| B-030 | Env override for SECURITY_MAX_FILE_MB | ⚙️ | 1 | OK done | Flexible file size limits with environment override
| File validation + env config + OOM prevention | None |
| B-031 | Vector Database Foundation Enhancement | 🔥 | 3 | todo | Improve RAG system with advanced vector database
capabilities | PostgreSQL + PGVector + advanced indexing | Enhanced RAG system |
| B-032 | Memory Context System Architecture Research | 🔥 | 8 | todo | Optimize memory hierarchy for different AI model
capabilities (7B vs 70B) | Literature review + benchmark harness + design recommendations | Improved retrieval F1 by
≥10% on 7B models |
| B-032-C1 | Implement generation cache (Postgres) & add cache columns to episodic_logs | 🔥 | 3 | todo | Add
cache-augmented generation support with similarity scoring | PostgreSQL + cache_hit + similarity_score + last_verified |
B-032 Memory Context System Architecture Research |
| B-033 | Documentation Reference Updates | 🔥 | 2 | OK done | Update outdated file references in documentation |
Documentation review + reference updates | File naming convention migration |
| B-001 | Implement Surgical Governance Testing Coverage | 🔄 pending | 3 | 8 | Add comprehensive test coverage for governance sys... | None |

- --

## 🚀 Future Model Roadmap

### **Advanced Agent Specialization (Q1 2025)**
- **B-034**: Deep Research Agent Integration
- **B-035**: Coder Agent Specialization
- **B-036**: General Query Agent Enhancement

### **System Integration & Optimization (Q2 2025)**
- **B-037**: External Model Integration (Future)
- **B-038**: Advanced Model Orchestration

### **Performance & Scaling (Q3 2025)**
- **B-039**: Performance Optimization Suite
- **B-040**: Advanced Caching & Memory Management

## 📚 Research & Development

### **Current Research Focus**
- **DSPy Integration**: Advanced reasoning and validation
- **RAG Optimization**: Hybrid search and entity expansion
- **Context Engineering**: Few-shot patterns and cognitive scaffolding

### **Research Integration**
- **Research Index**: `500_research/500_research-index.md`
- **Implementation Guides**: `400_guides/400_*` series
- **Memory Context**: `100_memory/104_dspy-development-context.md`

## 🔄 Maintenance & Updates

### **Regular Maintenance Tasks**
- **Monthly**: Backlog grooming and priority review
- **Quarterly**: Roadmap alignment and strategic planning
- **As Needed**: Context preservation and lessons learned updates

### **Quality Gates**
- **Validator Compliance**: All items must pass `doc_coherence_validator.py`
- **Documentation Alignment**: Cross-references must be maintained
- **Strategic Alignment**: Items must align with development roadmap

## Setup Required Items

List any setup prerequisites or required environment steps that must be completed before executing backlog workflows. If none are required, state that explicitly.

Currently, no additional setup is required beyond the instructions in `200_setup/202_setup-requirements.md`.

<!-- README_AUTOFIX_START -->
# Auto-generated sections for 000_backlog.md
# Generated: 2025-08-17T21:51:36.730486

## Missing sections to add:

## Last Reviewed

2025-08-17

## Owner

Core Team

## Purpose

Describe the purpose and scope of this document.

## Usage

Describe how to use this document or system.

<!-- README_AUTOFIX_END -->
