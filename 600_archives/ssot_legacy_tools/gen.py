# evals/tools/gen.py
# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportAny=false
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from ..ssot.registry_core import SUITE  # type: ignore[import-untyped]

OUT = Path("evals/_generated")
TEMPLATES = Environment(loader=FileSystemLoader("evals/ssot/templates"), autoescape=False)


def _pass_hash(p: Any) -> str:
    s = json.dumps(p.config.model_dump(), sort_keys=True).encode()
    return hashlib.sha1(s).hexdigest()[:10]


def load_latest_results() -> dict[str, Any]:
    p = Path("evals/metrics/latest/metrics.json")
    return json.loads(p.read_text()) if p.exists() else {}


def render_markdown():
    OUT.mkdir(parents=True, exist_ok=True)
    tpl = TEMPLATES.get_template("suite.j2")
    md = tpl.render(suite=SUITE, results_map=load_latest_results())
    _ = (OUT / "300_core.md").write_text(md, encoding="utf-8")


def write_manifest_json():
    results = load_latest_results()
    manifest: dict[str, Any] = {
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
                "metrics": [m.model_dump() for m in p.metrics],  # pyright: ignore[reportUnknownVariableType]
                "latest_results": load_latest_results().get(p.id, {}),
            }
            for p in SUITE.passes
        ],
    }
    _ = (OUT / "300_core_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def write_results_csv():
    results = load_latest_results()
    rows: list[dict[str, Any]] = []
    for p in SUITE.passes:
        r = load_latest_results().get(p.id, {})
        rows.append(
            {
                "pass_id": p.id,
                "name": p.name,
                "config_hash": _pass_hash(p),
                "layers": " + ".join(p.config_layers),
                "f1": result.get("f1", ""),
                "precision": result.get("precision", ""),
                "recall": result.get("recall", ""),
                "faithfulness": result.get("faithfulness", ""),
                "timestamp": result.get("timestamp", ""),
                "artifact": result.get("artifact", ""),
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
