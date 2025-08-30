\n+## 🧭 Backlog Hygiene
\n+- Start work when you begin a task, update status at meaningful changes, mark "✅ done" at completion.
- Use en dash in IDs (e.g., `B‑052‑d`), and keep `000_core/000_backlog.md` in sync.
\n+### Weekly Stale Item Review
- Run `python3 scripts/backlog_status_tracking.py --check-stale --stale-days 7`.
- Triage stale items and add remediation tasks to the backlog.
\n+## ✅ Constitution Checklist (Workflow)
\n+- Preserve chain: `000_backlog.md → 001_create-prd.md → 002_generate-tasks.md → 003_process-task-list.md`.
- Pre‑flight: run file analysis before edits; seek explicit approval for destructive ops.
- Post‑flight: validate tests, rollback plan, and cross‑ref coherence.
# Development Workflow and Standards

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Canonical development workflow and standards | Implementing features, planning changes, or reviewing process | Follow the workflow below; see 05 for code standards and 11 for deployment |

## 🎯 Purpose

Define the end-to-end development workflow (from idea to deployment) and the standards we enforce to keep quality high and changes safe.

## 📋 When to Use This Guide

- Starting a new feature or refactor
- Planning or reviewing implementation steps
- Aligning on commit, review, and testing standards
- Preparing changes for deployment

## ✅ Expected Outcomes

- Clear, repeatable workflow stages
- Consistent implementation and review standards
- Traceable commits tied to backlog items
- Changes that pass tests, link checks, and CI gates

## 🧭 Workflow (Idea → Live)

1) Backlog and Scope
- Open or select a backlog item in `000_core/000_backlog.md`
- Confirm dependencies and acceptance criteria

2) Planning
- Read context from `400_00_getting-started-and-index.md` and `400_03_system-overview-and-architecture.md`
- For docs work, consult `400_01_documentation-playbook.md`

3) Implementation
- Follow code standards in `400_05_coding-and-prompting-standards.md`
- Use evidence-first edits and keep commits atomic

4) Testing
- Apply testing strategy from `400_05_coding-and-prompting-standards.md#testing-strategy-and-quality-gates`
- Ensure unit/integration/E2E coverage as appropriate

5) Security & Compliance
- Review `400_10_security-compliance-and-access.md` for security checks

6) Deployment & Ops
- Use `400_11_deployments-ops-and-observability.md` for rollout and validation

## 🧱 Detailed Workflow Stages

### Stage 1: Setup & Context
- Environment check: `python3 scripts/venv_manager.py --check`
- Memory rehydration: `./scripts/memory_up.sh -q "your task"`
- Quick conflict check: `python scripts/quick_conflict_check.py`
- **Cursor Git Integration Fix**: If you see "🔍 Quick conflict check" messages during commits, use `git commit --no-verify` or `./scripts/commit_without_cursor.sh "message"` to bypass Cursor's built-in conflict detection

#### **Cursor Rules Integration**
- **Memory Rehydration Trigger**: `.cursorrules` automatically triggers `./scripts/memory_up.sh` at the start of new chats
- **Two Types of Cursor Rules**:
  - **Root Level**: `.cursorrules` - Contains memory rehydration trigger and core project rules
  - **Directory Level**: `.cursor/rules/` - Contains specialized rules for specific contexts
- **Automatic Context Loading**: Ensures AI has immediate access to project state, backlog, and system architecture
- **Role-Specific Context**: Memory rehydration includes role-specific information (planner, implementer, researcher, coder)

#### 10-minute triage (from Comprehensive Guide)
- Merge markers: `git grep -nE '^(<<<<<<<|=======|>>>>>>>)'`
- Python deps: `python -m pip check`
- Node deps: `npm ls --all`
- Deep audit pointers: `python scripts/conflict_audit.py --full`, `python scripts/system_health_check.py --deep`

### Stage 2: Planning
- Assess code criticality (Tier 1–3) and affected modules
- Decide on reuse vs build per `400_05_coding-and-prompting-standards.md`
- Define test plan and acceptance criteria

### Stage 3: Implementation
- Follow coding patterns and guardrails in 05 (types, errors, structure)
- Keep edits atomic and evidence-first; reference sources in commit body
- Useful commands: `ruff check .`, `pyright .`, `ruff format .`

### Stage 4: Testing
- Unit, integration, and system tests as appropriate
- Coverage targets and quality gates per 05 testing strategy
- Run: `pytest tests/ -q` (see markers/tiers in repo)

### Stage 5: Quality
- Code review checklist (function length, typing, errors, docs)
- CI dry-run validates lint, types, tests on PRs

### Stage 6: Deployment
- Pre-deploy checklist (tests/quality/perf/security) then rollout via 11

## 🧩 Standards

- Commits reference backlog IDs where applicable
- Documentation updated alongside code changes
- No broken links (link validation required)
- Consolidated guide links only (no links to archived 600_ files)
- Consistent section structure across guides

### Commit & Traceability
- Reference backlog IDs when applicable (e.g., B-xxxx)
- Summarize problem and resolution for housecleaning items

## 🔧 How-To (Common Tasks)

- Start a feature: align scope, create branch if required by policy, implement with small commits
- Update docs: follow `400_01_documentation-playbook.md` structure and cross-link patterns
- Add tests: consult testing gates in 05; keep tests fast and focused
- Run link validation: ensure all internal links resolve in 400_guides and 000/100/

### Development Commands
```bash
# Start development session
python3 scripts/single_doorway.py generate "feature description"

# Check code quality
ruff check . && pyright .

# Run tests
pytest tests/ -q
```

## 📝 Checklists

- [ ] Backlog item selected and scoped
- [ ] Code follows 05 standards; types and naming are clear
- [ ] Tests added/updated and pass locally
- [ ] Links valid across docs (no references to removed files)
- [ ] Security considerations reviewed (10)
- [ ] Deployment plan confirmed (11)

## 🔗 Interfaces

- Backlog: `000_core/000_backlog.md`
- Docs Index: `400_00_getting-started-and-index.md`
- Architecture: `400_03_system-overview-and-architecture.md`
- Coding & Testing: `400_05_coding-and-prompting-standards.md`
- Security: `400_10_security-compliance-and-access.md`
- Deployments/Ops: `400_11_deployments-ops-and-observability.md`

## 📚 References

- Documentation Playbook: `400_01_documentation-playbook.md`
- AI Frameworks (DSPy/MCP): `400_07_ai-frameworks-dspy.md`
- Integrations: `400_08_integrations-editor-and-models.md`
- Automation & Pipelines: `400_09_automation-and-pipelines.md`

## 🔗 Related

- Getting Started: `400_00_getting-started-and-index.md`
- Product & Roadmap: `400_12_product-management-and-roadmap.md`

## 📋 Changelog
- 2025-08-28: Restored consolidated development workflow and standards guide.
