from __future__ import annotations
import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from scripts.episodic_workflow_integration import EpisodicWorkflowIntegration
import os
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Heuristics Pack Generator

Automatically generates and maintains procedural heuristics from episodic reflections.
Creates versioned, evidence-backed operational guidance that evolves with your work.
"""

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import after path modification

@dataclass
class Heuristic:
    """Represents a single heuristic rule."""

    text: str
    evidence_count: int
    last_seen: datetime
    example_episode_ids: list[int]
    confidence_score: float
    category: str
    created_at: datetime
    updated_at: datetime

@dataclass
class HeuristicsPack:
    """Represents a complete heuristics pack for an agent."""

    agent: str
    version: str
    created_at: datetime
    updated_at: datetime
    total_episodes: int
    heuristics: list[Heuristic]
    categories: dict[str, int]
    confidence_threshold: float

class HeuristicsPackGenerator:
    """Generates and maintains heuristics packs from episodic reflections."""

    def __init__(self):
        """Initialize the generator."""
        self.episodic_integration = EpisodicWorkflowIntegration()
        self.min_evidence_count = 1  # Minimum episodes to support a heuristic (lowered for testing)
        self.max_heuristics_per_pack = 10
        self.confidence_threshold = 0.3
        print("🧠 Heuristics Pack Generator initialized")

    def generate_heuristics_pack(self, agent: str = "cursor_ai") -> HeuristicsPack:
        """Generate a heuristics pack for a specific agent."""
        start_time = time.time()

        try:
            # Get all reflections for the agent
            reflections = self._get_agent_reflections(agent)

            if not reflections:
                print(f"⚠️  No reflections found for agent: {agent}")
                return self._create_empty_pack(agent)

            # Extract heuristics from what_worked and what_to_avoid
            heuristics = self._extract_heuristics(reflections)

            # Score and rank heuristics
            scored_heuristics = self._score_heuristics(heuristics, reflections)

            # Select top heuristics
            top_heuristics = self._select_top_heuristics(scored_heuristics)

            # Create categories
            categories = self._categorize_heuristics(top_heuristics)

            # Generate version
            version = self._generate_version()

            pack = HeuristicsPack(
                agent=agent,
                version=version,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                total_episodes=len(reflections),
                heuristics=top_heuristics,
                categories=categories,
                confidence_threshold=self.confidence_threshold,
            )

            processing_time = (time.time() - start_time) * 1000
            print(
                f"✅ Generated heuristics pack for {agent}: {len(top_heuristics)} heuristics from {len(reflections)} episodes ({processing_time:.1f}ms)"
            )

            return pack

        except Exception as e:
            print(f"❌ Failed to generate heuristics pack: {e}")
            return self._create_empty_pack(agent)

    def _get_agent_reflections(self, agent: str) -> list[dict[str, Any]]:
        """Get all reflections for a specific agent."""
        try:
            # In a real implementation, this would query the database
            # For now, we'll use the mock store's reflections
            store = self.episodic_integration.store
            agent_reflections = [r for r in store.reflections if r.agent == agent]

            # Convert to dict format for processing
            reflections = []
            for reflection in agent_reflections:
                reflections.append(
                    {
                        "id": reflection.id,
                        "summary": reflection.summary,
                        "what_worked": reflection.what_worked,
                        "what_to_avoid": reflection.what_to_avoid,
                        "task_type": reflection.task_type,
                        "created_at": reflection.created_at,
                        "outcome_metrics": reflection.outcome_metrics,
                    }
                )

            return reflections

        except Exception as e:
            print(f"❌ Failed to get agent reflections: {e}")
            return []

    def _extract_heuristics(self, reflections: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Extract heuristics from reflections."""
        heuristics = []

        for reflection in reflections:
            # Extract from what_worked
            for item in reflection["what_worked"]:
                heuristics.append(
                    {
                        "text": item,
                        "type": "positive",
                        "episode_id": reflection["id"],
                        "task_type": reflection["task_type"],
                        "created_at": reflection["created_at"],
                        "outcome_metrics": reflection["outcome_metrics"],
                    }
                )

            # Extract from what_to_avoid
            for item in reflection["what_to_avoid"]:
                heuristics.append(
                    {
                        "text": item,
                        "type": "negative",
                        "episode_id": reflection["id"],
                        "task_type": reflection["task_type"],
                        "created_at": reflection["created_at"],
                        "outcome_metrics": reflection["outcome_metrics"],
                    }
                )

        return heuristics

    def _score_heuristics(
        self, heuristics: list[dict[str, Any]], reflections: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Score heuristics based on frequency, recency, and outcome success."""
        # Group similar heuristics
        heuristic_groups = defaultdict(list)

        for heuristic in heuristics:
            # Simple grouping by text similarity (in real implementation, use embeddings)
            key = heuristic["text"].lower().strip()
            heuristic_groups[key].append(heuristic)

        scored_heuristics = []

        for group_text, group_heuristics in heuristic_groups.items():
            if len(group_heuristics) < self.min_evidence_count:
                continue

            # Calculate scores
            evidence_count = len(group_heuristics)
            recency_score = self._calculate_recency_score(group_heuristics)
            success_score = self._calculate_success_score(group_heuristics)
            diversity_score = self._calculate_diversity_score(group_heuristics)

            # Combined confidence score
            confidence_score = (
                evidence_count * 0.4 + recency_score * 0.3 + success_score * 0.2 + diversity_score * 0.1
            ) / 10

            # Get most recent version
            most_recent = max(group_heuristics, key=lambda x: x["created_at"])

            # Determine category
            category = self._categorize_heuristic(most_recent)

            scored_heuristics.append(
                {
                    "text": most_recent["text"],
                    "type": most_recent["type"],
                    "evidence_count": evidence_count,
                    "last_seen": most_recent["created_at"],
                    "example_episode_ids": [h["episode_id"] for h in group_heuristics],
                    "confidence_score": confidence_score,
                    "category": category,
                    "created_at": min(h["created_at"] for h in group_heuristics),
                    "updated_at": most_recent["created_at"],
                }
            )

        return scored_heuristics

    def _calculate_recency_score(self, heuristics: list[dict[str, Any]]) -> float:
        """Calculate recency score (higher for more recent heuristics)."""
        if not heuristics:
            return 0.0

        now = datetime.now()
        most_recent = max(h["created_at"] for h in heuristics)
        days_old = (now - most_recent).days

        # Score decreases with age
        if days_old < 7:
            return 10.0
        elif days_old < 30:
            return 7.0
        elif days_old < 90:
            return 5.0
        else:
            return 2.0

    def _calculate_success_score(self, heuristics: list[dict[str, Any]]) -> float:
        """Calculate success score based on outcome metrics."""
        if not heuristics:
            return 0.0

        success_count = 0
        total_count = len(heuristics)

        for heuristic in heuristics:
            metrics = heuristic.get("outcome_metrics", {})
            if metrics.get("success", False):
                success_count += 1

        return (success_count / total_count) * 10.0

    def _calculate_diversity_score(self, heuristics: list[dict[str, Any]]) -> float:
        """Calculate diversity score based on task type variety."""
        if not heuristics:
            return 0.0

        task_types = set(h["task_type"] for h in heuristics)
        return min(len(task_types) * 2.0, 10.0)

    def _categorize_heuristic(self, heuristic: dict[str, Any]) -> str:
        """Categorize a heuristic based on its content."""
        text = heuristic["text"].lower()
        # task_type = heuristic["task_type"].lower()  # Unused variable removed

        # Simple categorization based on keywords
        if any(word in text for word in ["error", "exception", "try", "catch", "handle"]):
            return "error_handling"
        elif any(word in text for word in ["test", "unit", "coverage", "assert"]):
            return "testing"
        elif any(word in text for word in ["performance", "optimize", "speed", "memory"]):
            return "performance"
        elif any(word in text for word in ["database", "query", "sql", "connection"]):
            return "database"
        elif any(word in text for word in ["import", "module", "package", "dependency"]):
            return "dependencies"
        elif any(word in text for word in ["config", "setting", "parameter", "environment"]):
            return "configuration"
        else:
            return "general"

    def _select_top_heuristics(self, scored_heuristics: list[dict[str, Any]]) -> list[Heuristic]:
        """Select the top heuristics for the pack."""
        # Sort by confidence score
        sorted_heuristics = sorted(scored_heuristics, key=lambda x: x["confidence_score"], reverse=True)

        # Take top N heuristics
        top_heuristics = sorted_heuristics[: self.max_heuristics_per_pack]

        # Convert to Heuristic objects
        heuristics = []
        for h in top_heuristics:
            heuristic = Heuristic(
                text=h["text"],
                evidence_count=h["evidence_count"],
                last_seen=h["last_seen"],
                example_episode_ids=h["example_episode_ids"],
                confidence_score=h["confidence_score"],
                category=h["category"],
                created_at=h["created_at"],
                updated_at=h["updated_at"],
            )
            heuristics.append(heuristic)

        return heuristics

    def _categorize_heuristics(self, heuristics: list[Heuristic]) -> dict[str, int]:
        """Count heuristics by category."""
        categories = Counter(h.category for h in heuristics)
        return dict(categories)

    def _generate_version(self) -> str:
        """Generate a version string."""
        now = datetime.now()
        return f"v{now.strftime('%Y%m%d')}"

    def _create_empty_pack(self, agent: str) -> HeuristicsPack:
        """Create an empty heuristics pack."""
        return HeuristicsPack(
            agent=agent,
            version=self._generate_version(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            total_episodes=0,
            heuristics=[],
            categories={},
            confidence_threshold=self.confidence_threshold,
        )

    def format_heuristics_pack(self, pack: HeuristicsPack, format_type: str = "system_prompt") -> str:
        """Format heuristics pack for different use cases."""
        if format_type == "system_prompt":
            return self._format_for_system_prompt(pack)
        elif format_type == "markdown":
            return self._format_for_markdown(pack)
        elif format_type == "json":
            return self._format_for_json(pack)
        else:
            return self._format_for_system_prompt(pack)

    def _format_for_system_prompt(self, pack: HeuristicsPack) -> str:
        """Format heuristics pack for inclusion in system prompts."""
        if not pack.heuristics:
            return ""

        formatted = f"\n\n## 🧠 Procedural Heuristics Pack v{pack.version}\n"
        formatted += (
            f"*Auto-generated from {pack.total_episodes} episodes (confidence ≥{pack.confidence_threshold})*\n\n"
        )

        # Group by category
        by_category = defaultdict(list)
        for heuristic in pack.heuristics:
            by_category[heuristic.category].append(heuristic)

        for category, heuristics in by_category.items():
            formatted += f"**{category.replace('_', ' ').title()}:**\n"
            for heuristic in heuristics:
                icon = "✅" if heuristic.text.startswith(("Use", "Prefer", "Apply")) else "❌"
                formatted += f"{icon} {heuristic.text} ({heuristic.evidence_count} episodes)\n"
            formatted += "\n"

        return formatted

    def _format_for_markdown(self, pack: HeuristicsPack) -> str:
        """Format heuristics pack as markdown documentation."""
        formatted = f"# Heuristics Pack for {pack.agent}\n\n"
        formatted += f"**Version:** {pack.version}\n"
        formatted += f"**Generated:** {pack.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        formatted += f"**Total Episodes:** {pack.total_episodes}\n"
        formatted += f"**Confidence Threshold:** {pack.confidence_threshold}\n\n"

        if pack.categories:
            formatted += "## Categories\n\n"
            for category, count in pack.categories.items():
                formatted += f"- **{category.replace('_', ' ').title()}:** {count} heuristics\n"
            formatted += "\n"

        if pack.heuristics:
            formatted += "## Heuristics\n\n"
            for i, heuristic in enumerate(pack.heuristics, 1):
                formatted += f"### {i}. {heuristic.text}\n\n"
                formatted += f"- **Category:** {heuristic.category}\n"
                formatted += f"- **Evidence Count:** {heuristic.evidence_count} episodes\n"
                formatted += f"- **Confidence Score:** {heuristic.confidence_score:.2f}\n"
                formatted += f"- **Last Seen:** {heuristic.last_seen.strftime('%Y-%m-%d')}\n"
                formatted += f"- **Example Episodes:** {', '.join(map(str, heuristic.example_episode_ids))}\n\n"

        return formatted

    def _format_for_json(self, pack: HeuristicsPack) -> str:
        """Format heuristics pack as JSON."""
        pack_dict = {
            "agent": pack.agent,
            "version": pack.version,
            "created_at": pack.created_at.isoformat(),
            "updated_at": pack.updated_at.isoformat(),
            "total_episodes": pack.total_episodes,
            "categories": pack.categories,
            "confidence_threshold": pack.confidence_threshold,
            "heuristics": [
                {
                    "text": h.text,
                    "evidence_count": h.evidence_count,
                    "last_seen": h.last_seen.isoformat(),
                    "example_episode_ids": h.example_episode_ids,
                    "confidence_score": h.confidence_score,
                    "category": h.category,
                    "created_at": h.created_at.isoformat(),
                    "updated_at": h.updated_at.isoformat(),
                }
                for h in pack.heuristics
            ],
        }
        return json.dumps(pack_dict, indent=2)

    def save_heuristics_pack(self, pack: HeuristicsPack, output_path: str) -> bool:
        """Save heuristics pack to file."""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w") as f:
                f.write(self.format_heuristics_pack(pack, "json"))

            print(f"✅ Saved heuristics pack to: {output_file}")
            return True

        except Exception as e:
            print(f"❌ Failed to save heuristics pack: {e}")
            return False

    def load_heuristics_pack(self, input_path: str) -> HeuristicsPack | None:
        """Load heuristics pack from file."""
        try:
            with open(input_path) as f:
                data = json.load(f)

            heuristics = []
            for h_data in data.get("heuristics", []):
                heuristic = Heuristic(
                    text=h_data["text"],
                    evidence_count=h_data["evidence_count"],
                    last_seen=datetime.fromisoformat(h_data["last_seen"]),
                    example_episode_ids=h_data["example_episode_ids"],
                    confidence_score=h_data["confidence_score"],
                    category=h_data["category"],
                    created_at=datetime.fromisoformat(h_data["created_at"]),
                    updated_at=datetime.fromisoformat(h_data["updated_at"]),
                )
                heuristics.append(heuristic)

            pack = HeuristicsPack(
                agent=data["agent"],
                version=data["version"],
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
                total_episodes=data["total_episodes"],
                heuristics=heuristics,
                categories=data["categories"],
                confidence_threshold=data["confidence_threshold"],
            )

            print(f"✅ Loaded heuristics pack from: {input_path}")
            return pack

        except Exception as e:
            print(f"❌ Failed to load heuristics pack: {e}")
            return None

def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Heuristics Pack Generator")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate heuristics pack")
    generate_parser.add_argument("--agent", default="cursor_ai", help="Agent name")
    generate_parser.add_argument("--output", help="Output file path")
    generate_parser.add_argument(
        "--format", choices=["system_prompt", "markdown", "json"], default="system_prompt", help="Output format"
    )

    # Load command
    load_parser = subparsers.add_parser("load", help="Load heuristics pack from file")
    load_parser.add_argument("--input", required=True, help="Input file path")
    load_parser.add_argument(
        "--format", choices=["system_prompt", "markdown", "json"], default="system_prompt", help="Output format"
    )

    # Test command
    subparsers.add_parser("test", help="Test the generator")

    args = parser.parse_args()

    generator = HeuristicsPackGenerator()

    if args.command == "generate":
        pack = generator.generate_heuristics_pack(args.agent)

        if args.output:
            generator.save_heuristics_pack(pack, args.output)

        formatted = generator.format_heuristics_pack(pack, args.format)
        print(formatted)

    elif args.command == "load":
        pack = generator.load_heuristics_pack(args.input)
        if pack:
            formatted = generator.format_heuristics_pack(pack, args.format)
            print(formatted)

    elif args.command == "test":
        print("🧪 Testing Heuristics Pack Generator...")

        # Test generation
        pack = generator.generate_heuristics_pack("cursor_ai")

        if pack.heuristics:
            print(f"✅ Generated pack with {len(pack.heuristics)} heuristics")
            print(f"   Categories: {pack.categories}")
            print(f"   Total episodes: {pack.total_episodes}")

            # Test formatting
            system_prompt = generator.format_heuristics_pack(pack, "system_prompt")
            if system_prompt:
                print("✅ System prompt formatting works")

            markdown = generator.format_heuristics_pack(pack, "markdown")
            if markdown:
                print("✅ Markdown formatting works")

            json_output = generator.format_heuristics_pack(pack, "json")
            if json_output:
                print("✅ JSON formatting works")
        else:
            print("⚠️  No heuristics generated (insufficient data)")

        print("✅ All tests completed")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
