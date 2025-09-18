#!/usr/bin/env python3
"""
Atlas Self-Healing Navigation System
Detects and repairs broken references, citations, and connections
"""

import json
import os

# Add project paths
import sys
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import psycopg
from psycopg.rows import dict_row

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from sentence_transformers import SentenceTransformer


class CitationState(Enum):
    """Citation state machine for self-healing."""

    CANDIDATE = "candidate"
    VALIDATED = "validated"
    BROKEN = "broken"
    REPAIRED = "repaired"
    PUBLISHED = "published"


class SelfHealingNavigator:
    """Self-healing navigation system for Atlas graph."""

    def __init__(self, dsn: str | None = None) -> None:
        self.dsn: str = dsn or os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
        self.embedder: SentenceTransformer = SentenceTransformer("BAAI/bge-large-en-v1.5")
        self.embedding_dim: int = 1024

    def detect_broken_references(self) -> list[dict[str, Any]]:
        """Detect broken references in the Atlas graph."""
        broken_refs = []

        with psycopg.connect(self.dsn) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Find edges pointing to non-existent nodes
                _ = cur.execute(
                    """
                    SELECT e.*, n1.title as source_title, n1.node_type as source_type
                    FROM atlas_edge e
                    LEFT JOIN atlas_node n1 ON e.source_node_id = n1.node_id
                    LEFT JOIN atlas_node n2 ON e.target_node_id = n2.node_id
                    WHERE n2.node_id IS NULL
                """
                )

                for row in cur.fetchall():
                    broken_refs.append(
                        {
                            "type": "missing_target",
                            "edge_id": row["edge_id"],
                            "source_node": row["source_node_id"],
                            "target_node": row["target_node_id"],
                            "edge_type": row["edge_type"],
                            "source_title": row["source_title"],
                            "source_type": row["source_type"],
                            "severity": "high",
                        }
                    )

                # Find nodes with no connections (orphaned)
                _ = cur.execute(
                    """
                    SELECT n.*
                    FROM atlas_node n
                    LEFT JOIN atlas_edge e1 ON n.node_id = e1.source_node_id
                    LEFT JOIN atlas_edge e2 ON n.node_id = e2.target_node_id
                    WHERE e1.edge_id IS NULL AND e2.edge_id IS NULL
                    AND n.node_type != 'concept'
                """
                )

                for row in cur.fetchall():
                    broken_refs.append(
                        {
                            "type": "orphaned_node",
                            "node_id": row["node_id"],
                            "node_type": row["node_type"],
                            "title": row["title"],
                            "severity": "medium",
                        }
                    )

                # Find edges with low confidence
                _ = cur.execute(
                    """
                    SELECT e.*, n1.title as source_title, n2.title as target_title
                    FROM atlas_edge e
                    JOIN atlas_node n1 ON e.source_node_id = n1.node_id
                    JOIN atlas_node n2 ON e.target_node_id = n2.node_id
                    WHERE e.weight < 0.3
                """
                )

                for row in cur.fetchall():
                    broken_refs.append(
                        {
                            "type": "low_confidence",
                            "edge_id": row["edge_id"],
                            "source_node": row["source_node_id"],
                            "target_node": row["target_node_id"],
                            "edge_type": row["edge_type"],
                            "weight": row["weight"],
                            "source_title": row["source_title"],
                            "target_title": row["target_title"],
                            "severity": "low",
                        }
                    )

        return broken_refs

    def repair_broken_references(self, broken_refs: list[dict[str, Any]]) -> dict[str, Any]:
        """Repair broken references using various strategies."""
        repair_results: dict[str, Any] = {"repaired": 0, "failed": 0, "skipped": 0, "repairs": []}

        for ref in broken_refs:
            try:
                if ref["type"] == "missing_target":
                    repair = self._repair_missing_target(ref)
                elif ref["type"] == "orphaned_node":
                    repair = self._repair_orphaned_node(ref)
                elif ref["type"] == "low_confidence":
                    repair = self._repair_low_confidence(ref)
                else:
                    repair = {"status": "skipped", "reason": "unknown_type"}

                repair_results["repairs"].append({"reference": ref, "repair": repair})

                if repair["status"] == "repaired":
                    repair_results["repaired"] = repair_results["repaired"] + 1
                elif repair["status"] == "failed":
                    repair_results["failed"] = repair_results["failed"] + 1
                else:
                    repair_results["skipped"] = repair_results["skipped"] + 1

            except Exception as e:
                repair_results["repairs"].append({"reference": ref, "repair": {"status": "failed", "error": str(e)}})
                repair_results["failed"] = repair_results["failed"] + 1

        return repair_results

    def _repair_missing_target(self, ref: dict[str, Any]) -> dict[str, Any]:
        """Repair missing target nodes by finding similar nodes."""
        try:
            # Search for similar nodes
            similar_nodes = self._find_similar_nodes(ref["target_node"])

            if similar_nodes:
                # Update the edge to point to the most similar node
                best_match = similar_nodes[0]

                with psycopg.connect(self.dsn) as conn:
                    with conn.cursor() as cur:
                        _ = cur.execute(
                            """
                            UPDATE atlas_edge 
                            SET target_node_id = %s, 
                                evidence = %s,
                                weight = %s
                            WHERE edge_id = %s
                        """,
                            (
                                best_match["node_id"],
                                f"Auto-repaired: {ref['target_node']} -> {best_match['node_id']} (similarity: {best_match['similarity']:.3f})",
                                best_match["similarity"],
                                ref["edge_id"],
                            ),
                        )
                        conn.commit()

                return {
                    "status": "repaired",
                    "new_target": best_match["node_id"],
                    "similarity": best_match["similarity"],
                    "method": "similarity_search",
                }
            else:
                # Create a placeholder node
                placeholder_id = f"placeholder_{ref['target_node']}_{int(time.time())}"
                self._create_placeholder_node(placeholder_id, ref["target_node"])

                with psycopg.connect(self.dsn) as conn:
                    with conn.cursor() as cur:
                        _ = cur.execute(
                            """
                            UPDATE atlas_edge 
                            SET target_node_id = %s,
                                evidence = %s
                            WHERE edge_id = %s
                        """,
                            (
                                placeholder_id,
                                f"Auto-repaired: created placeholder for {ref['target_node']}",
                                ref["edge_id"],
                            ),
                        )
                        conn.commit()

                return {"status": "repaired", "new_target": placeholder_id, "method": "placeholder_creation"}

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def _repair_orphaned_node(self, ref: dict[str, Any]) -> dict[str, Any]:
        """Repair orphaned nodes by finding similar nodes to connect to."""
        try:
            # Find similar nodes to connect to
            similar_nodes = self._find_similar_nodes(ref["title"])

            if similar_nodes:
                # Create connections to similar nodes
                connections_created = 0

                with psycopg.connect(self.dsn) as conn:
                    with conn.cursor() as cur:
                        for similar in similar_nodes[:3]:  # Connect to top 3 similar nodes
                            _ = cur.execute(
                                """
                                INSERT INTO atlas_edge (source_node_id, target_node_id, edge_type, evidence, weight)
                                VALUES (%s, %s, %s, %s, %s)
                                ON CONFLICT (source_node_id, target_node_id, edge_type) DO NOTHING
                            """,
                                (
                                    ref["node_id"],
                                    similar["node_id"],
                                    "similar_to",
                                    f"Auto-connected: similarity {similar['similarity']:.3f}",
                                    similar["similarity"],
                                ),
                            )
                            connections_created = connections_created + 1
                        conn.commit()

                return {
                    "status": "repaired",
                    "connections_created": connections_created,
                    "method": "similarity_connection",
                }
            else:
                return {"status": "skipped", "reason": "no_similar_nodes_found"}

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def _repair_low_confidence(self, ref: dict[str, Any]) -> dict[str, Any]:
        """Repair low confidence edges by strengthening or removing them."""
        try:
            # If weight is very low, remove the edge
            if ref["weight"] < 0.1:
                with psycopg.connect(self.dsn) as conn:
                    with conn.cursor() as cur:
                        _ = cur.execute("DELETE FROM atlas_edge WHERE edge_id = %s", (ref["edge_id"],))
                        conn.commit()

                return {"status": "repaired", "action": "removed_low_confidence_edge", "method": "edge_removal"}
            else:
                # Strengthen the edge by updating evidence
                with psycopg.connect(self.dsn) as conn:
                    with conn.cursor() as cur:
                        _ = cur.execute(
                            """
                            UPDATE atlas_edge 
                            SET evidence = %s,
                                weight = %s
                            WHERE edge_id = %s
                        """,
                            (
                                f"Auto-strengthened: original weight {ref['weight']:.3f}",
                                min(ref["weight"] * 1.5, 1.0),  # Increase weight but cap at 1.0
                                ref["edge_id"],
                            ),
                        )
                        conn.commit()

                return {
                    "status": "repaired",
                    "action": "strengthened_edge",
                    "new_weight": min(ref["weight"] * 1.5, 1.0),
                    "method": "weight_boost",
                }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def _find_similar_nodes(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Find nodes similar to the query using embedding similarity."""
        try:
            query_embedding = self.embedder.encode(query)

            with psycopg.connect(self.dsn) as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    _ = cur.execute(
                        """
                        SELECT n.*, 
                               (n.embedding <=> %s::vector) as distance,
                               (1 - (n.embedding <=> %s::vector)) as similarity
                        FROM atlas_node n
                        WHERE n.embedding IS NOT NULL
                        ORDER BY n.embedding <=> %s::vector
                        LIMIT %s
                    """,
                        (query_embedding.tolist(), query_embedding.tolist(), query_embedding.tolist(), limit),
                    )

                    results = []
                    for row in cur.fetchall():
                        results.append(
                            {
                                "node_id": row["node_id"],
                                "title": row["title"],
                                "node_type": row["node_type"],
                                "similarity": float(row["similarity"]),
                                "distance": float(row["distance"]),
                            }
                        )

                    return results

        except Exception as e:
            print(f"❌ Error finding similar nodes: {e}")
            return []

    def _create_placeholder_node(self, node_id: str, original_id: str):
        """Create a placeholder node for missing references."""
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                _ = cur.execute(
                    """
                    INSERT INTO atlas_node (node_id, node_type, title, content, metadata, embedding, expires_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (node_id) DO NOTHING
                """,
                    (
                        node_id,
                        "placeholder",
                        f"Placeholder for {original_id}",
                        f"Auto-generated placeholder for missing node: {original_id}",
                        json.dumps({"original_id": original_id, "placeholder": True}),
                        self.embedder.encode(f"placeholder {original_id}").tolist(),
                        datetime.now() + timedelta(days=7),  # Placeholders expire in 7 days
                    ),
                )
                conn.commit()

    def get_graph_health_report(self) -> dict[str, Any]:
        """Get a comprehensive health report for the Atlas graph."""
        try:
            broken_refs = self.detect_broken_references()

            # Categorize by severity
            high_severity = [r for r in broken_refs if r["severity"] == "high"]
            medium_severity = [r for r in broken_refs if r["severity"] == "medium"]
            low_severity = [r for r in broken_refs if r["severity"] == "low"]

            # Get graph statistics
            with psycopg.connect(self.dsn) as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    _ = cur.execute("SELECT COUNT(*) as total_nodes FROM atlas_node")
                    row = cur.fetchone()
                    total_nodes = row["total_nodes"] if row else 0

                    _ = cur.execute("SELECT COUNT(*) as total_edges FROM atlas_edge")
                    row = cur.fetchone()
                    total_edges = row["total_edges"] if row else 0

                    _ = cur.execute("SELECT AVG(weight) as avg_weight FROM atlas_edge")
                    row = cur.fetchone()
                    avg_weight = row["avg_weight"] if row else 0

                    _ = cur.execute(
                        """
                        SELECT COUNT(*) as orphaned_count
                        FROM atlas_node n
                        LEFT JOIN atlas_edge e1 ON n.node_id = e1.source_node_id
                        LEFT JOIN atlas_edge e2 ON n.node_id = e2.target_node_id
                        WHERE e1.edge_id IS NULL AND e2.edge_id IS NULL
                        AND n.node_type != 'concept'
                    """
                    )
                    row = cur.fetchone()
                    orphaned_count = row["orphaned_count"] if row else 0

            return {
                "total_nodes": total_nodes,
                "total_edges": total_edges,
                "avg_edge_weight": float(avg_weight),
                "orphaned_nodes": orphaned_count,
                "broken_references": {
                    "total": len(broken_refs),
                    "high_severity": len(high_severity),
                    "medium_severity": len(medium_severity),
                    "low_severity": len(low_severity),
                },
                "health_score": self._calculate_health_score(total_nodes, total_edges, len(broken_refs)),
                "recommendations": self._generate_recommendations(broken_refs),
            }

        except Exception as e:
            return {"error": str(e)}

    def _calculate_health_score(self, total_nodes: int, total_edges: int, broken_refs: int) -> float:
        """Calculate a health score for the graph (0-100)."""
        if total_nodes == 0:
            return 0.0

        # Base score from connectivity
        connectivity_score = min(100, (total_edges / max(total_nodes, 1)) * 50)

        # Penalty for broken references
        broken_penalty = min(50, (broken_refs / max(total_nodes, 1)) * 100)

        return max(0, connectivity_score - broken_penalty)

    def _generate_recommendations(self, broken_refs: list[dict[str, Any]]) -> list[str]:
        """Generate recommendations for improving graph health."""
        recommendations = []

        if not broken_refs:
            recommendations.append("✅ Graph is healthy - no broken references detected")
            return recommendations

        high_severity = [r for r in broken_refs if r["severity"] == "high"]
        medium_severity = [r for r in broken_refs if r["severity"] == "medium"]
        low_severity = [r for r in broken_refs if r["severity"] == "low"]

        if high_severity:
            recommendations.append(f"🔴 High Priority: Fix {len(high_severity)} broken references (missing targets)")

        if medium_severity:
            recommendations.append(f"🟡 Medium Priority: Connect {len(medium_severity)} orphaned nodes")

        if low_severity:
            recommendations.append(f"🟢 Low Priority: Review {len(low_severity)} low-confidence edges")

        recommendations.append("💡 Run self-healing repair to automatically fix issues")

        return recommendations


def main():
    """Test the self-healing navigation system."""
    print("🔧 Testing Atlas Self-Healing Navigation System")

    navigator = SelfHealingNavigator()

    # Get health report
    health_report = navigator.get_graph_health_report()
    print("\n📊 Graph Health Report:")
    print(f"Total Nodes: {health_report['total_nodes']}")
    print(f"Total Edges: {health_report['total_edges']}")
    print(f"Health Score: {health_report['health_score']:.1f}/100")
    print(f"Broken References: {health_report['broken_references']['total']}")

    print("\n💡 Recommendations:")
    for rec in health_report["recommendations"]:
        print(f"  {rec}")

    # Detect and repair broken references
    print("\n🔍 Detecting broken references...")
    broken_refs = navigator.detect_broken_references()
    print(f"Found {len(broken_refs)} broken references")

    if broken_refs:
        print("\n🔧 Repairing broken references...")
        repair_results = navigator.repair_broken_references(broken_refs)
        print(f"Repaired: {repair_results['repaired']}")
        print(f"Failed: {repair_results['failed']}")
        print(f"Skipped: {repair_results['skipped']}")

    print("🎯 Self-healing navigation system is working!")


if __name__ == "__main__":
    main()
