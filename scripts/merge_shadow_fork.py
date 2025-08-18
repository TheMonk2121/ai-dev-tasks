#!/usr/bin/env python3.12.123.11
"""
Shadow Fork Merge Script

Merges enhanced/optimized files into their canonical locations and archives the duplicates.
Handles import updates and creates diffs for manual review when conflicts exist.
"""

import difflib
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "600_archives" / "shadow_forks"
ARCH.mkdir(parents=True, exist_ok=True)


def update_imports(old: Path, new: Path):
    """Update imports that reference the old filename to the new canonical."""
    old_mod = old.with_suffix("").as_posix()
    new_mod = new.with_suffix("").as_posix()
    # Make repo-relative module strings (strip leading root and convert slashes to dots)
    old_rel = old_mod.replace(ROOT.as_posix() + "/", "").replace("/", ".").replace(" ", "")
    new_rel = new_mod.replace(ROOT.as_posix() + "/", "").replace("/", ".").replace(" ", "")

    print(f"  Updating imports: {old_rel} → {new_rel}")

    # Conservative: only update obvious `from … import` or `import …` lines
    updated_files = []
    for p in ROOT.rglob("*.py"):
        if p == old or p == new:  # Skip the files being merged
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
            replaced = txt.replace(f"from {old_rel}", f"from {new_rel}").replace(
                f"import {old_rel}", f"import {new_rel}"
            )
            if replaced != txt:
                p.write_text(replaced, encoding="utf-8")
                updated_files.append(str(p))
        except Exception as e:
            print(f"    Warning: Could not update {p}: {e}")

    if updated_files:
        print(f"    Updated imports in {len(updated_files)} files")
        for f in updated_files[:5]:  # Show first 5
            print(f"      {f}")
        if len(updated_files) > 5:
            print(f"      ... and {len(updated_files) - 5} more")


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/merge_shadow_fork.py scripts/shadow_fork_cleanup_map.yaml")
        sys.exit(2)

    mapping_file = Path(sys.argv[1])
    if not mapping_file.exists():
        print(f"Error: Mapping file not found: {mapping_file}")
        sys.exit(1)

    mapping = yaml.safe_load(mapping_file.read_text())
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")

    print(f"Shadow Fork Cleanup - {ts}")
    print("=" * 50)

    for shadow, canon in mapping.items():
        s = ROOT / shadow
        c = ROOT / canon

        print(f"\nProcessing: {shadow} → {canon}")

        if not s.exists():
            print(f"  [SKIP] Missing shadow: {s}")
            continue

        c.parent.mkdir(parents=True, exist_ok=True)

        if not c.exists():
            print(f"  [NEW ] Creating canonical from shadow: {c}")
            shutil.copy2(s, c)
        else:
            # Show a unified diff for manual reconciliation
            try:
                s_lines = s.read_text(encoding="utf-8", errors="ignore").splitlines(True)
                c_lines = c.read_text(encoding="utf-8", errors="ignore").splitlines(True)
                diff = "".join(difflib.unified_diff(c_lines, s_lines, fromfile=str(c), tofile=str(s)))
                if diff:
                    patch = ARCH / f"{c.name}.{ts}.diff"
                    patch.write_text(diff, encoding="utf-8")
                    print(f"  [DIFF] {c} ← {s} (review {patch})")
                    print(f"    Manual merge required. Diff saved to: {patch}")
                    print(f"    Please merge improvements from {s} into {c} manually")
                    # Don't proceed with archiving until manual merge is done
                    continue
                else:
                    print("  [SAME] Files are identical, no merge needed")
            except Exception as e:
                print(f"  [ERROR] Could not compare files: {e}")
                continue

        # Update imports pointing to shadow filename -> canonical
        update_imports(s, c)

        # Archive shadow file
        dst = ARCH / f"{s.name}.{ts}"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(s), str(dst))
        print(f"  [ARCH] {s} → {dst}")

    print("\n" + "=" * 50)
    print("Cleanup completed!")

    # Run validator to confirm WARNs cleared for handled files
    print("\nRunning validator to check results...")
    try:
        result = subprocess.run(
            ["python", "scripts/doc_coherence_validator.py"], capture_output=True, text=True, cwd=ROOT
        )
        if result.returncode == 0:
            print("OK Validator passed - no shadow fork violations remaining")
        else:
            print("!️  Validator found remaining issues:")
            print(result.stdout)
    except Exception as e:
        print(f"!️  Could not run validator: {e}")


if __name__ == "__main__":
    main()
