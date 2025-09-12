from __future__ import annotations
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any
import yaml
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Evolution Tracker - Tracks configuration evolution and generates evolution maps
"""

def load_config_metadata(config_path: str) -> dict[str, Any] | None:
    """Load metadata from a config sidecar file"""
    meta_path = config_path.replace(".env", ".meta.yml")
    if not os.path.exists(meta_path):
        return None

    try:
        with open(meta_path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Warning: Could not load metadata from {meta_path}: {e}")
        return None

def scan_configs(configs_dir: str = "configs") -> list[dict[str, Any]]:
    """Scan all configuration files and their metadata"""
    configs = []

    if not os.path.exists(configs_dir):
        return configs

    for file in os.listdir(configs_dir):
        if file.endswith(".env"):
            config_path = os.path.join(configs_dir, file)
            metadata = load_config_metadata(config_path)

            config_info = {
                "id": file,
                "path": config_path,
                "created_at": None,
                "derived_from": None,
                "objective_bias": None,
                "decision_log": [],
            }

            if metadata:
                # Convert datetime objects to strings for JSON serialization
                created_at = metadata.get("created_at")
                if hasattr(created_at, "isoformat"):
                    created_at = created_at.isoformat()

                config_info.update(
                    {
                        "created_at": created_at,
                        "derived_from": metadata.get("derived_from"),
                        "objective_bias": metadata.get("objective_bias"),
                        "decision_log": metadata.get("decision_log", []),
                    }
                )

            configs.append(config_info)

    return configs

def build_evolution_graph(configs: list[dict[str, Any]]) -> dict[str, Any]:
    """Build evolution graph from configuration metadata"""
    nodes = []
    edges = []

    # Create nodes
    for config in configs:
        node = {
            "id": config["id"],
            "created_at": config["created_at"],
            "objective_bias": config["objective_bias"],
            "has_metadata": config["derived_from"] is not None,
        }
        nodes.append(node)

    # Create edges based on derivation relationships
    for config in configs:
        if config["derived_from"]:
            # Find the source config
            source_id = None
            for other_config in configs:
                if other_config["path"].endswith(config["derived_from"]):
                    source_id = other_config["id"]
                    break

            if source_id:
                # Extract rationale from decision log
                rationale = "Configuration evolution"
                if config["decision_log"]:
                    latest_decision = config["decision_log"][-1]
                    rationale = latest_decision.get("why", rationale)

                edge = {"from": source_id, "to": config["id"], "why": rationale, "created_at": config["created_at"]}
                edges.append(edge)

    return {"nodes": nodes, "edges": edges, "generated_at": datetime.now().isoformat(), "total_configs": len(configs)}

def generate_mermaid_diagram(evolution_graph: dict[str, Any]) -> str:
    """Generate Mermaid diagram from evolution graph"""
    mermaid = ["graph TD"]

    # Add nodes with styling
    for node in evolution_graph["nodes"]:
        node_id = node["id"].replace(".env", "").replace("_", " ")
        style = "fill:#e1f5fe" if node["has_metadata"] else "fill:#f5f5f5"
        mermaid.append(f'    {node["id"]}["{node_id}"]')

    # Add edges
    for edge in evolution_graph["edges"]:
        mermaid.append(f'    {edge["from"]} --> {edge["to"]}')

    return "\n".join(mermaid)

def generate_evolution_report(evolution_graph: dict[str, Any], output_dir: str = "configs") -> str:
    """Generate comprehensive evolution report"""
    report_lines = [
        "# Configuration Evolution Report",
        "",
        f"**Generated**: {evolution_graph['generated_at']}",
        f"**Total Configurations**: {evolution_graph['total_configs']}",
        "",
        "## Evolution Graph",
        "",
        "```mermaid",
        generate_mermaid_diagram(evolution_graph),
        "```",
        "",
        "## Configuration Details",
        "",
    ]

    # Add configuration details
    for node in evolution_graph["nodes"]:
        report_lines.extend(
            [
                f"### {node['id']}",
                "",
                f"- **Created**: {node['created_at'] or 'Unknown'}",
                f"- **Objective**: {node['objective_bias'] or 'Unknown'}",
                f"- **Has Metadata**: {'Yes' if node['has_metadata'] else 'No'}",
                "",
            ]
        )

    # Add evolution relationships
    if evolution_graph["edges"]:
        report_lines.extend(
            ["## Evolution Relationships", "", "| From | To | Rationale |", "|------|----|-----------|"]
        )

        for edge in evolution_graph["edges"]:
            report_lines.append(f"| {edge['from']} | {edge['to']} | {edge['why']} |")

    return "\n".join(report_lines)

def main():
    """Main function to generate evolution tracking files"""
    print("🔄 Scanning configuration files...")

    # Scan configurations
    configs = scan_configs()
    print(f"📊 Found {len(configs)} configuration files")

    # Build evolution graph
    evolution_graph = build_evolution_graph(configs)
    print(f"🔗 Found {len(evolution_graph['edges'])} evolution relationships")

    # Generate outputs
    output_dir = "configs"

    # Save evolution graph as JSON
    evolution_json_path = os.path.join(output_dir, "EVOLUTION.json")
    with open(evolution_json_path, "w") as f:
        json.dump(evolution_graph, f, indent=2)
    print(f"💾 Evolution graph saved to: {evolution_json_path}")

    # Generate and save evolution report
    evolution_report = generate_evolution_report(evolution_graph, output_dir)
    evolution_md_path = os.path.join(output_dir, "EVOLUTION.md")
    with open(evolution_md_path, "w") as f:
        f.write(evolution_report)
    print(f"📋 Evolution report saved to: {evolution_md_path}")

    # Print summary
    print("\n📈 Evolution Summary:")
    print(f"  • Total configurations: {len(configs)}")
    print(f"  • With metadata: {sum(1 for c in configs if c['derived_from'])}")
    print(f"  • Evolution relationships: {len(evolution_graph['edges'])}")

    return evolution_graph

if __name__ == "__main__":
    main()
