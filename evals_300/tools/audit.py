import json
import subprocess
import time
from pathlib import Path
from typing import Optional, Tuple

STATE_DIR = Path("evals_300/_state")
VERSIONS = STATE_DIR / "versions.json"
CHANGELOG = STATE_DIR / "changelog.ndjson"

STATE_DIR.mkdir(parents=True, exist_ok=True)
if not VERSIONS.exists():
    VERSIONS.write_text("{}", encoding="utf-8")
if not CHANGELOG.exists():
    CHANGELOG.write_text("", encoding="utf-8")


def _git(cmd: list[str]) -> str:
    return subprocess.check_output(cmd).decode().strip()


def repo_head() -> dict:
    try:
        return {
            "commit": _git(["git", "rev-parse", "HEAD"]),
            "branch": _git(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
        }
    except Exception:
        return {"commit": None, "branch": None}


def suite_file_path() -> str:
    return "evals_300/ssot/registry_core.py"


def created_updated_from_git(search_token: str, path: str) -> Tuple[Optional[str], Optional[str]]:
    """Return ISO timestamps for first and last commits touching token."""
    try:
        log = _git(["git", "log", "-S", search_token, "--format=%H %cI", "--", path])
    except Exception:
        return None, None
    if not log:
        return None, None
    lines = [ln for ln in log.splitlines() if ln.strip()]
    latest = lines[0].split(" ", 1)[1] if lines else None
    earliest = lines[-1].split(" ", 1)[1] if lines else None
    return earliest, latest


def load_versions() -> dict:
    try:
        return json.loads(VERSIONS.read_text())
    except Exception:
        return {}


def save_versions(data: dict) -> None:
    VERSIONS.write_text(json.dumps(data, indent=2), encoding="utf-8")


def bump_version(old: Optional[str], scope: str) -> str:
    """Scope: major (run), minor (metrics), patch (config)."""
    maj, minr, pat = (1, 0, 0) if not old else [int(x) for x in old.split(".")]
    if scope == "major":
        maj, minr, pat = (maj + 1, 0, 0)
    elif scope == "minor":
        minr, pat = (minr + 1, 0)
    else:
        pat += 1
    return f"{maj}.{minr}.{pat}"


def append_changelog(event: dict) -> None:
    event = dict(event)
    event.setdefault("ts", time.strftime("%Y-%m-%dT%H:%M:%S"))
    with CHANGELOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
