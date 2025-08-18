# 📚 Documentation Guide

<!-- DATABASE_SYNC: REQUIRED -->

<!-- CONTEXT_REFERENCE: 400_guides/400_cursor-context-engineering-guide.md -->

<!-- MODULE_REFERENCE: 100_memory/100_cursor-memory-context.md -->

## 🔎 TL;DR

| what this file is | read when | do next |
|----|----|----|
| Canonical documentation guide (inventory + retrieval + validation) | Finding docs, getting context, or validating docs | Use Reference → Retrieval → Validation sections below |

## 📚 Reference

- **Critical files (read first)**: `400_guides/400_project-overview.md`,
  `100_memory/100_cursor-memory-context.md`, `000_core/000_backlog.md`,
  `400_guides/400_system-overview.md`.
- **Workflows**: `000_core/001_create-prd.md`,
  `000_core/002_generate-tasks.md`, `000_core/003_process-task-list.md`,
  `100_memory/100_backlog-guide.md`.
- **Operational guides**: Testing, Security, Performance, Deployment,
  Migration, Integration in `400_guides/`.
- For a full inventory, see the sections in this file; the older
  inventory file has been deprecated.

## 🔎 Retrieval

- Index documentation: `python scripts/documentation_indexer.py`
- Search (CLI):
  `python scripts/documentation_retrieval_cli.py search "query" --category guides --limit 10`
- Get task context:
  `python scripts/documentation_retrieval_cli.py task "implement indexing" --task-type development`
- Programmatic API:
  `dspy-rag-system/src/dspy_modules/documentation_retrieval.py`

## ✅ Validation

- Dry-run coherence check: `python scripts/doc_coherence_validator.py`
- Apply fixes: `python scripts/doc_coherence_validator.py --no-dry-run`
- Pre-commit: `./scripts/pre_commit_doc_validation.sh --install`

## ✍️ Authoring guidelines for anchors and headings

- Heading levels:
  - Exactly one H1 `#` per file; it should match the filename’s title.
  - Use H2+ (`##`, `###`, …) for internal sections.
- Anchor slugs:
  - Slugs are GitHub-style; emojis/punctuation are stripped. Example:
    “⚡ Quick reference” → `quick-reference`.
  - Prefer linking by heading anchors instead of inline HTML anchors.
- Cross-folder links:
  - Use relative paths and verify anchors exist. Example:
    `../400_guides/400_metadata-collection-guide.md#quick-reference`.
- Validate before commit:
  - Run:
    `python3 scripts/link_check.py --root . --scope . --changed-files --json`.
  - On CI/PRs, the repo runs the same check and fails on broken anchors.

Quick reference commands:

``` bash
# Repo-wide (human-readable)
python3 scripts/link_check.py --root . --scope .

# Changed files (JSON report)
git diff --name-only origin/main...HEAD | grep '\.md$' > changed_md.txt || true
python3 scripts/link_check.py --root . --scope . --changed-files-from changed_md.txt --json --output linkcheck_report.json
```

## 🧭 README File Organization

- Use `README.md` for user-facing overview, quick start, features,
  high-level architecture.
- Use `README-dev.md` for developer workflows, testing, internal
  patterns.
- Cross-link both ways; keep anchors stable per
  `200_setup/200_naming-conventions.md`.

## 🔗 Stable anchors

- tldr
- authoring-anchors
- readme-file-organization

<!-- README_AUTOFIX_START -->

## Auto-generated sections for 400_documentation-guide.md

## Generated: 2025-08-18T08:03:22.739820

## Missing sections to add:

## Last Reviewed

2025-08-18

## Owner

Documentation Team

## Purpose

Describe the purpose and scope of this document

## Usage

Describe how to use this document or system

<!-- README_AUTOFIX_END -->
