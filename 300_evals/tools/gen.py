# 300_evals/tools/gen.py
import csv
import hashlib
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from ..ssot.registry_core import SUITE

OUT = Path("300_evals/_generated")
TEMPLATES = Environment(loader=FileSystemLoader("300_evals/ssot/templates"), autoescape=False)


def _pass_hash(p) -> str:
    s = json.dumps(p.config.model_dump(), sort_keys=True).encode()
    return hashlib.sha1(s).hexdigest()[:10]


def load_latest_results() -> dict:
    p = Path("metrics/latest/metrics.json")
    return json.loads(p.read_text()) if p.exists() else {}


def render_markdown():
    OUT.mkdir(parents=True, exist_ok=True)
    tpl = TEMPLATES.get_template("suite.j2")
    md = tpl.render(suite=SUITE, results_map=load_latest_results())
    (OUT / "300_core.md").write_text(md, encoding="utf-8")


def write_manifest_json():
    results = load_latest_results()
    manifest = {
        "suite_id": SUITE.id,
        "title": SUITE.title,
        "passes": [
            {
                "id": p.id,
                "name": p.name,
                "tags": p.tags,
                "lifecycle": p.lifecycle,
                "config_layers": p.config_layers,
                "config_hash": _pass_hash(p),
                "config": p.config.model_dump(),
                "run": p.run.model_dump(),
                "metrics": [m.model_dump() for m in p.metrics],
                "latest_results": results.get(p.id, {}),
            }
            for p in SUITE.passes
        ],
    }
    (OUT / "300_core_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def write_results_csv():
    results = load_latest_results()
    rows = []
    for p in SUITE.passes:
        r = results.get(p.id, {})
        rows.append(
            {
                "pass_id": p.id,
                "name": p.name,
                "config_hash": _pass_hash(p),
                "layers": " + ".join(p.config_layers),
                "f1": r.get("f1"),
                "precision": r.get("precision"),
                "recall": r.get("recall"),
                "faithfulness": r.get("faithfulness"),
                "timestamp": r.get("timestamp"),
                "artifact": r.get("artifact_path"),
            }
        )
    with (OUT / "300_core_results.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [])
        w.writeheader()
        w.writerows(rows)


def main():
    render_markdown()
    write_manifest_json()
    write_results_csv()


if __name__ == "__main__":
    main()
