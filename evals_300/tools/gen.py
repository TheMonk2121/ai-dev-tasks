# 300_evals/tools/gen.py
import csv
import hashlib
import json
from datetime import UTC, datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from ..ssot.registry_core import SUITE
from .audit import bump_version, created_updated_from_git, load_versions, repo_head, save_versions, suite_file_path

OUT = Path("evals_300/_generated")
TEMPLATES = Environment(loader=FileSystemLoader("evals_300/ssot/templates"), autoescape=False)


def _pass_hash(p) -> str:
    s = json.dumps(
        {"cfg": p.config.model_dump(), "run": p.run.model_dump(), "metrics": [m.model_dump() for m in p.metrics]},
        sort_keys=True,
    ).encode()
    return hashlib.sha1(s).hexdigest()[:12]


def _version_scope(old, p, prev_signature: dict) -> str:
    """
    Decide bump scope by comparing signature buckets.
    """
    new_sig = {
        "run": p.run.model_dump(),
        "metrics": [m.model_dump() for m in p.metrics],
        "config": p.config.model_dump(),
    }
    if not prev_signature:
        return "major"
    if new_sig["run"] != prev_signature.get("run"):
        return "major"
    if new_sig["metrics"] != prev_signature.get("metrics"):
        return "minor"
    if new_sig["config"] != prev_signature.get("config"):
        return "patch"
    return "patch"


def _prepare_versions():
    state = load_versions()
    changed = False
    for p in SUITE.passes:
        pid = p.id
        ph = _pass_hash(p)
        rec = state.get(pid, {})
        prev_sig = rec.get("signature", {})
        scope = _version_scope(rec.get("version"), p, prev_sig)
        if ph != rec.get("config_hash"):
            # bump
            new_v = bump_version(rec.get("version"), scope)
            state[pid] = {
                "version": new_v,
                "config_hash": ph,
                "signature": {
                    "run": p.run.model_dump(),
                    "metrics": [m.model_dump() for m in p.metrics],
                    "config": p.config.model_dump(),
                },
                "updated_at": datetime.now(UTC).isoformat(),
                "created_at": rec.get("created_at") or datetime.now(UTC).isoformat(),
            }
            changed = True
        else:
            # keep as-is
            if "version" not in rec:
                state[pid] = {
                    **rec,
                    "version": "1.0.0",
                    "updated_at": datetime.now(UTC).isoformat(),
                    "created_at": rec.get("created_at") or datetime.now(UTC).isoformat(),
                }
                changed = True
    if changed:
        save_versions(state)
    return state


def load_latest_results() -> dict:
    p = Path("metrics/latest/metrics.json")
    return json.loads(p.read_text()) if p.exists() else {}


def render_markdown(versions: dict):
    OUT.mkdir(parents=True, exist_ok=True)
    tpl = TEMPLATES.get_template("suite.j2")
    results = load_latest_results()
    # decorate with git-derived timestamps for display (no code mutation)
    sf = suite_file_path()
    suite_created, suite_updated = created_updated_from_git("EvalSuite(", sf)
    md = tpl.render(
        suite=SUITE,
        results_map=results,
        versions=versions,
        repo=repo_head(),
        suite_created=suite_created,
        suite_updated=suite_updated,
        generated_at=datetime.now(UTC).isoformat(),
    )
    (OUT / "300_core.md").write_text(md, encoding="utf-8")


def write_manifest_json(versions: dict):
    results = load_latest_results()
    head = repo_head()
    suite_created, suite_updated = created_updated_from_git("EvalSuite(", suite_file_path())
    manifest = {
        "suite_id": SUITE.id,
        "title": SUITE.title,
        "generated_at": datetime.now(UTC).isoformat(),
        "git": head,
        "suite_created_at": suite_created,
        "suite_updated_at": suite_updated,
        "passes": [],
    }
    for p in SUITE.passes:
        pid = p.id
        created, updated = created_updated_from_git(pid, suite_file_path())
        vrec = versions.get(pid, {})
        latest = results.get(pid, {})
        manifest["passes"].append(
            {
                "id": pid,
                "name": p.name,
                "version": vrec.get("version"),
                "config_hash": vrec.get("config_hash"),
                "created_at": created or vrec.get("created_at"),
                "updated_at": updated or vrec.get("updated_at"),
                "last_run_at": latest.get("timestamp"),
                "config_layers": p.config_layers,
                "config": p.config.model_dump(),
                "run": p.run.model_dump(),
                "metrics": [m.model_dump() for m in p.metrics],
                "latest_results": latest,
            }
        )
    (OUT / "300_core_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def write_results_csv(versions: dict):
    results = load_latest_results()
    rows = []
    for p in SUITE.passes:
        pid = p.id
        vrec = versions.get(pid, {})
        r = results.get(pid, {})
        rows.append(
            {
                "pass_id": pid,
                "name": p.name,
                "version": vrec.get("version"),
                "config_hash": vrec.get("config_hash"),
                "layers": " + ".join(p.config_layers),
                "f1": r.get("f1"),
                "precision": r.get("precision"),
                "recall": r.get("recall"),
                "faithfulness": r.get("faithfulness"),
                "timestamp": r.get("timestamp"),
                "artifact": r.get("artifact_path"),
            }
        )
    out = OUT / "300_core_results.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        if rows:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)


def main():
    versions = _prepare_versions()
    render_markdown(versions)
    write_manifest_json(versions)
    write_results_csv(versions)


if __name__ == "__main__":
    main()
