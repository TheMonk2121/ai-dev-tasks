\n+## ⚖️ Constitution Callout
\n+- **Documentation coherence**: keep cross‑references intact; use a single index (`400_00_getting-started-and-index.md`); remove legacy links.
- **Safety gate**: do not delete/archive without a dependency scan and explicit approval.
- **Governance**: use the condensed constitution in `400_02_governance-and-ai-constitution.md` as the single source.
# Documentation Playbook

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Canonical docs-about-docs playbook (structure, retrieval, cross-refs, metadata, validation) | Working on documentation, cross-references, or context | Follow structure and cross-ref standards below; validate links before commit |

## 🎯 Purpose

Define how we write, organize, cross-reference, validate, and ship documentation so authors and agents can find one canonical home per topic and avoid drift or duplication.

## 📋 When to Use This Guide

- Creating or updating any `400_guides/` document
- Consolidating or moving content between guides
- Adding cross-references or anchors
- Running link checks and docs validation in CI

## 🧱 Canonical Structure (All Guides)

- Title (H1) matches filename
- TL;DR table (what/read-when/do-next)
- Purpose → When to Use → Outcomes (optional) → Policies → How-To → Checklists → Interfaces → Examples → Diagnostics → References → Related → Changelog
- Keep sections present even if brief; favor adding links over duplicating text

### Required Sections and Anchors
- Stable anchors on major sections (e.g., `#tldr`, `#policies`, `#interfaces`)
- Changelog section at bottom with dated entries
- Cross-refs must point to consolidated 13 guides (see below)

## 🔗 Cross-Reference Policy

- One canonical home per topic; other guides link to it (no duplicate “truths”)
- Prefer relative links to consolidated guides:
  - 03: `400_03_system-overview-and-architecture.md`
  - 04: `400_04_development-workflow-and-standards.md`
  - 05: `400_05_coding-and-prompting-standards.md`
  - 06: `400_06_memory-and-context-systems.md`
  - 07: `400_07_ai-frameworks-dspy.md`
  - 08: `400_08_integrations-editor-and-models.md`
  - 09: `400_09_automation-and-pipelines.md`
  - 10: `400_10_security-compliance-and-access.md`
  - 11: `400_11_deployments-ops-and-observability.md`
  - 12: `400_12_product-management-and-roadmap.md`
- Do not link to `600_archives/**` from consolidated guides
- If content is moved, leave a short stub in the old location with a `moved_to:` notice (in archives only)

### Inventory and Navigation
- Prefer the index: `400_00_getting-started-and-index.md` (Quick-Find, portals, complete index)
- Use the detailed inventory: `400_documentation-reference.md` for full lists and roles
- Use `400_03_system-overview-and-architecture.md` for the architectural map; defer deep details to topic homes

## 🏷️ Metadata & Anchors

- Headings become stable anchors; keep headings concise and stable over time
- Use descriptive subsection headings for deep links (e.g., `#testing-strategy-and-quality-gates`)
- Optional front-matter may be used by tooling; avoid heavy YAML blocks

### Comment Metadata for AI Systems
- `<!-- ANCHOR_KEY: unique-key -->`, `<!-- ANCHOR_PRIORITY: number -->`, `<!-- ROLE_PINS: ["role1", "role2"] -->` required at top of each guide
- `<!-- CONTEXT_REFERENCE: path -->` in key files consumed by memory rehydrator
- `<!-- MODULE_REFERENCE: path -->` to link code modules to guides
- Keep metadata comments short and machine-friendly

## ✅ Validation & CI

- Link validation must pass for changes that touch docs
- No broken internal links to `400_guides/**`
- Check that all 13 canonical guides exist and remain tracked
- CI blocks PRs that remove/rename any canonical file without explicit override

### Local Validation Commands
```bash
python3 scripts/validate_links.py
python3 scripts/doc_coherence_validator.py
pytest tests/test_broken_link_validation.py::TestRealProjectBrokenLinks::test_no_broken_links_in_project -q
```

## 🚚 Migrations & Consolidation

- Before moving content, confirm its canonical home (which of the 13?)
- Update links in dependent docs
- Add a short deprecation/stub only in archives; never in active 400_ guides

### Provenance & Migration Map
- Track original sources in `400_guides/migration_map.csv`
- When consolidating, cite the source sections in the target guide’s changelog

## 🧪 Authoring Checklist

- [ ] Title matches filename; TL;DR table present
- [ ] Sections ordered per canonical template
- [ ] Links point to consolidated guides (not archives)
- [ ] No duplication; link to canonical home instead
- [ ] Link validation passes locally and in CI

## 🧱 Documentation Tiering (Summary)

- Tier 1 (Priority 0–10) — NEVER delete; archive instead. Core memory/context and core workflow files.
- Tier 2 (Priority 15–20) — Important guides; require extensive analysis before changes.
- Tier 3 (Priority 25–30) — Implementation/specialized topics; normal review.
- Tier 4 (Priority 35–40) — PRDs, research, examples.

Creation checklist (condensed):
- Pre‑create: search `400_guides/` for existing content; confirm tier/placement per `200_naming-conventions.md`.
- Create: add `ANCHOR_PRIORITY`, `ROLE_PINS`, TL;DR table, and cross‑refs; follow naming conventions.
- Post‑create: update related cross‑refs; run `python scripts/doc_coherence_validator.py`; update memory context if core.

## 📋 Policies

- One canonical home per topic; link out instead of duplicating
- Evidence-first edits: include a reference or brief citation when moving material
- Keep files reasonably sized; move long examples to dedicated guides or appendices

## 🔧 How-To: Common Tasks

- Add a new subsection: create heading → add anchor references in related guides
- Move content: update links in all referencing files → run link validation
- Add examples: prefer minimal inline examples; link to code or test files when long

### Create a New Section with Stable Anchor
1. Add a heading with concise title
2. Immediately link it from related guides if needed
3. Add to `400_00_getting-started-and-index.md` if it’s a high-traffic section

## 🔗 Interfaces

- Index: `400_00_getting-started-and-index.md`
- System Overview: `400_03_system-overview-and-architecture.md`
- Coding & Testing: `400_05_coding-and-prompting-standards.md`
- Security: `400_10_security-compliance-and-access.md`
- Deployments/Ops: `400_11_deployments-ops-and-observability.md`

## 📚 References

- AI Frameworks (DSPy/MCP): `400_07_ai-frameworks-dspy.md`
- Integrations: `400_08_integrations-editor-and-models.md`
- Automation & Pipelines: `400_09_automation-and-pipelines.md`

### Detailed Inventories
- Documentation Inventory: `400_documentation-reference.md`
- Guide Index: `400_guide-index.md`

## 🧪 Diagnostics

- Run link validator before commit
- Ensure H1 matches filename exactly
- Confirm TL;DR table exists and renders

## 📋 Changelog
- 2025-08-28: Reconstructed and expanded canonical playbook from documentation inventory and index.
