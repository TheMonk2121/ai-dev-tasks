<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 400_testing-strategy-guide.md -->
<!-- MEMORY_CONTEXT: MEDIUM - Cross-reference policy and validation -->
# 🔗 Cross-Reference Strengthening Plan (v2)


## 🔗 Cross-Reference Strengthening Plan (v2)

{#tldr}

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
|  |  |  |

- **what this file is**: Quick summary of 🔗 Cross-Reference Strengthening Plan (v2).

- **read when**: When you need a fast orientation or before using this file in a workflow.

- **do next**: Scan the headings below and follow any 'Quick Start' or 'Usage' sections.

## 🎯 **Current Status**-**Status**: ✅ **ACTIVE**- Cross-reference policy enforced

- **Priority**: 📋 Medium - Documentation integrity

- **Points**: 2 - Low complexity, maintenance focus

- **Dependencies**: 400_context-priority-guide.md, 400_testing-strategy-guide.md

- **Next Steps**: Monitor compliance and update policy as needed

## Policy

- Minimal header schema only:
  - Keep: `<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->`
  - Allow ≤ 3 `MODULE_REFERENCE` lines to consolidated `400_*` guides
  - Exceptions allowed for core non-400 docs explicitly listed in the matrix (e.g., `000_backlog.md`)
  - No anchors in headers; anchors must be in-body

- In-body anchors: use stable IDs like `tldr`, `quick-start`, `architecture`, `workflow`, `testing`, `security`

- Avoid: split-module filenames (e.g., `_section.md`) and deliverable files (`B-011*`, `B-049*`, `B-072*`) in headers

## Cross-reference matrix

- Primary entry points
  - `100_cursor-memory-context.md` → modules: `400_context-priority-guide.md`, `400_system-overview.md`, `000_backlog.md`
  - `400_context-priority-guide.md` → modules: `400_system-overview.md`, `400_testing-strategy-guide.md`, `400_deployment-environment-guide.md`

- System and project overview
  - `400_system-overview.md` → modules: `100_cursor-memory-context.md`, `000_backlog.md`, `400_context-priority-guide.md`
  - `400_project-overview.md` → modules: `100_cursor-memory-context.md`, `000_backlog.md`, `400_system-overview.md`
  - `000_backlog.md` → modules: `100_cursor-memory-context.md`, `400_system-overview.md`, `400_project-overview.md`

- Workflow
  - `001_create-prd.md` → modules: `400_testing-strategy-guide.md`, `400_deployment-environment-guide.md`, `400_migration-upgrade-guide.md`
  - `002_generate-tasks.md` → modules: `000_backlog.md`, `400_system-overview.md`, `400_testing-strategy-guide.md`
  - `003_process-task-list.md` → modules: `000_backlog.md`, `400_system-overview.md`, `400_deployment-environment-guide.md`

- Implementation essentials
  - `104_dspy-development-context.md` → modules: `400_system-overview.md`, `400_testing-strategy-guide.md`, `000_backlog.md`
  - `202_setup-requirements.md` → modules: `400_deployment-environment-guide.md`, `400_system-overview.md`

- Consolidated reference guides
  - Each `400_*` guide → modules: `400_system-overview.md` plus 1–2 relevant peers (e.g., testing/performance for integration)

## Automation & guardrails

- Validate:
  - `python3 scripts/doc_coherence_validator.py --check-all`

- Normalize headers:
  - `python3 scripts/normalize_metadata_headers.py --root .`

- Migrate old references:
  - `python3 scripts/migrate_giant_guide_references.py`

- CI hook recommendation:
  - Run the three commands above; fail on new split-module or deliverable refs in headers

## What not to do

- Don’t add more than 3 `MODULE_REFERENCE` lines

- Don’t encode anchors in headers

- Don’t reference `_advanced_features.md`, `_additional_resources.md`, or `_lens_` files

## Checklist for new/edited docs

- H1 and TL;DR are present

- Minimal header schema applied

- Stable in-body anchors used where helpful

- Body text links out to relevant consolidated guides
