<!-- template_version: 1.2  |  runs_with: 003_process-task-list.md -->
<!-- purpose: One‑shot repo tidy‑up after model or workflow changes -->

# 🔧 Repository Maintenance – Cursor‑First Edition

### Why run this?
Whenever you switch default models, tweak the PRD‑skip rule, or shuffle core files, run this checklist to realign docs and delete cruft.

---

## Settings
| Key | Value |
|-----|-------|
| dry_run | false  <!-- change to false to auto‑apply edits --> |
| auto_commit | false |
| prd_threshold_points | 5 |
| prd_skip_if_score_ge | 3.0 |

---

<!--
AI-TASK-PAYLOAD:
backlog_id: B-999
tasks:
  - id: T‑1
    title: Align model references to "Cursor‑Native AI (default); Mistral & Yi optional"
    agent: plan
    points: 2
    done_when: >
      400_system-overview_advanced_features.md, 201_model-configuration.md, and
      both 100_cursor-memory-context.md copies reference Cursor as default.

  - id: T‑2
    title: Clarify 003 role across docs
    agent: plan
    points: 2
    depends_on: [T‑1]
    done_when: >
      All docs say "003_process-task-list.md is the execution engine;
      it loads whether or not a PRD was created."

  - id: T‑3
    title: Remove or archive duplicate files
    agent: plan
    points: 1
    done_when: >
      Only one canonical copy of 000_backlog.md and 003_process-task-list.md
      remains in the main tree; older copies moved to /docs/legacy or deleted.

  - id: T‑4
    title: Validate PRD‑skip rule wording
    agent: plan
    points: 1
    done_when: >
      100_cursor-memory-context.md and 100_backlog-guide.md both state:
      "Skip PRD when points<5 AND score_total≥3.0".

  - id: T‑5
    title: Contradiction scan
    agent: code
    points: 2
    done_when: >
      Repo grep shows zero hits for
      /(yi-coder.*default|mistral 7b instruct.*default|003 optional)/
      outside /docs/legacy.

  - id: T‑6
    title: Commit (manual ok)
    agent: plan
    points: 0.5
    done_when: >
      All edits staged and you have either committed or chosen to commit later.
-->

---

### Quick Human Checklist
| ✅ | Cursor = default model everywhere |
| ✅ | 003 described correctly (execution engine, PRD conditional) |
| ✅ | Duplicate files archived |
| ✅ | PRD‑skip rule identical across docs |
| ✅ | No stale "Yi‑Coder default" claims |

---

### When to run
* After **changing default models**, **adjusting PRD rules**, or **merging large doc refactors**.  
* Once per sprint for hygiene.

### How to run
* **Python Script** (Recommended): `python3 scripts/repo_maintenance.py --apply`
* **Dry Run**: `python3 scripts/repo_maintenance.py --dry-run`
* **Auto Commit**: `python3 scripts/repo_maintenance.py --apply --auto-commit`

### Where to document
* **`100_cursor-memory-context.md`** → add under *Maintenance Rituals*:  
  > "Run `python3 scripts/repo_maintenance.py --apply` after model or doc changes."  
* **README / 400_project-overview.md** → final step in Quick‑Start.  
* Reserve **backlog IDs 900‑999** for maintenance scripts.

---

*Tip: leave `dry_run:true` for the first run – you'll get a full diff but no files will change.*  
Switch it to `false` when you're ready to apply and (optionally) auto‑commit.

## What this script does not do (by design)
No default_executor meta‑tag. 003 runs every time; it just decides to skip PRD work when the threshold rule says so.

No diagram regeneration mandate. If you prefer ASCII diagrams, keep them; the task only updates wording.

No automatic archive. You confirm the duplicate‑file move so nothing important disappears by accident.

After you run it
Review the diff Cursor shows (or look at staged changes if you set auto_commit:false).

Commit with a message like chore: cursor‑first doc alignment.

Delete or archive 999_repo‑maintenance.md until the next architectural tweak.

That's it—your documentation, workflow description, and file tree will all march in step with the Cursor‑native, PRD‑conditional reality you and Cursor both want. 