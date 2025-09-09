#!/usr/bin/env python3
"""
README Context Manager
- Implements tiered documentation strategy
- Prevents bloat through smart consolidation
- Ensures compliance without overfitting
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path


class READMEContextManager:
    """Manages README context documentation with smart consolidation."""

    def __init__(self, readme_path: str = "README.md"):
        self.readme_path = Path(readme_path)
        self.backlog_path = Path("000_core/000_backlog.md")

    def analyze_backlog_items(self, days: int = 30) -> dict[str, dict]:
        """Analyze backlog items and categorize them for documentation."""
        import subprocess

        # Get recent commits with backlog references
        result = subprocess.run(["git", "log", f"--since={days} days ago", "--oneline"], capture_output=True, text=True)

        commits = result.stdout.strip().split("\n")
        backlog_items = {}

        for commit in commits:
            # Extract backlog IDs
            backlog_ids = re.findall(r"B-(\d+)", commit)
            for backlog_id in backlog_ids:
                full_id = f"B-{backlog_id}"
                if full_id not in backlog_items:
                    backlog_items[full_id] = {
                        "commits": [],
                        "impact_score": 0,
                        "complexity_score": 0,
                        "documentation_needed": False,
                    }
                backlog_items[full_id]["commits"].append(commit)

        return backlog_items

    def calculate_impact_score(self, backlog_id: str, commits: list[str]) -> int:
        """Calculate impact score based on commit patterns."""
        score = 0

        # High-impact patterns
        high_impact_patterns = [
            r"feat\(.*\):.*",  # New features
            r"BREAKING CHANGE",  # Breaking changes
            r"Complete.*System",  # System completions
            r"Implement.*Framework",  # Framework implementations
        ]

        # Medium-impact patterns
        medium_impact_patterns = [
            r"enhance.*",  # Enhancements
            r"improve.*",  # Improvements
            r"optimize.*",  # Optimizations
            r"integrate.*",  # Integrations
        ]

        for commit in commits:
            commit_lower = commit.lower()

            # Check high-impact patterns
            for pattern in high_impact_patterns:
                if re.search(pattern, commit, re.IGNORECASE):
                    score += 5
                    break

            # Check medium-impact patterns
            for pattern in medium_impact_patterns:
                if re.search(pattern, commit, re.IGNORECASE):
                    score += 3
                    break

            # Check for specific keywords
            if any(keyword in commit_lower for keyword in ["system", "framework", "architecture"]):
                score += 2
            if any(keyword in commit_lower for keyword in ["performance", "optimization", "scaling"]):
                score += 2
            if any(keyword in commit_lower for keyword in ["integration", "api", "database"]):
                score += 2

        return min(score, 10)  # Cap at 10

    def calculate_complexity_score(self, backlog_id: str, commits: list[str]) -> int:
        """Calculate complexity score based on file changes."""
        import subprocess

        score = 0

        # Get files changed for this backlog item
        for commit in commits:
            commit_hash = commit.split()[0]
            try:
                result = subprocess.run(
                    ["git", "show", "--name-only", "--format=", commit_hash], capture_output=True, text=True
                )

                files = result.stdout.strip().split("\n")

                for file in files:
                    if file.endswith(".py"):
                        score += 1
                    if file.endswith(".md"):
                        score += 1
                    if file.endswith(".sql"):
                        score += 2
                    if "dspy-rag-system" in file:
                        score += 2
                    if "scripts/" in file:
                        score += 1
                    if "100_memory/" in file:
                        score += 2
                    if "000_core/" in file:
                        score += 2

            except subprocess.CalledProcessError:
                continue

        return min(score, 10)  # Cap at 10

    def determine_documentation_needed(self, impact_score: int, complexity_score: int) -> bool:
        """Determine if documentation is needed based on scores."""
        # Documentation needed if:
        # - High impact (score >= 6) OR
        # - High complexity (score >= 6) OR
        # - Both medium (score >= 4 each)
        return impact_score >= 6 or complexity_score >= 6 or (impact_score >= 4 and complexity_score >= 4)

    def generate_consolidated_context(self, backlog_items: dict[str, dict]) -> str:
        """Generate consolidated context for high-priority items."""
        high_priority = []
        medium_priority = []

        for backlog_id, data in backlog_items.items():
            if data["documentation_needed"]:
                if data["impact_score"] >= 6 or data["complexity_score"] >= 6:
                    high_priority.append((backlog_id, data))
                else:
                    medium_priority.append((backlog_id, data))

        # Sort by impact score
        high_priority.sort(key=lambda x: x[1]["impact_score"], reverse=True)
        medium_priority.sort(key=lambda x: x[1]["impact_score"], reverse=True)

        context = []

        # High priority items get full documentation
        for backlog_id, data in high_priority[:5]:  # Limit to top 5
            context.append(self.generate_full_context(backlog_id, data))

        # Medium priority items get consolidated summary
        if medium_priority:
            context.append(self.generate_consolidated_summary(medium_priority))

        return "\n\n".join(context)

    def generate_full_context(self, backlog_id: str, data: dict) -> str:
        """Generate full context for high-priority item."""
        latest_commit = data["commits"][0] if data["commits"] else "Unknown commit"

        return f"""#### **{backlog_id}: High-Impact Implementation** ({datetime.now().strftime('%Y-%m-%d')})
**Commit**: `{latest_commit}`

**Rich Context:**
- **Impact Score**: {data['impact_score']}/10
- **Complexity Score**: {data['complexity_score']}/10
- **Implementation Details**: [Add specific technical decisions]
- **Key Features**: [Add main features implemented]
- **Performance Impact**: [Add performance metrics]
- **Integration Points**: [Add integration details]"""

    def generate_consolidated_summary(self, medium_priority: list[tuple[str, dict]]) -> str:
        """Generate consolidated summary for medium-priority items."""
        summary = f"""#### **Consolidated Medium-Impact Changes** ({datetime.now().strftime('%Y-%m-%d')})
**Items**: {', '.join(item[0] for item in medium_priority[:10])}

**Summary**: {len(medium_priority)} medium-impact changes implemented with focus on:
- **System Improvements**: Performance optimizations and bug fixes
- **Documentation Updates**: Enhanced guides and context management
- **Tooling Enhancements**: Script improvements and validation systems
- **Integration Refinements**: Better system connectivity and data flow

**Key Patterns**: [Add recurring patterns or insights from these changes]"""

        return summary

    def cleanup_old_context(self, max_age_days: int = 90) -> list[str]:
        """Identify old context entries for potential cleanup."""
        if not self.readme_path.exists():
            return []

        content = self.readme_path.read_text()

        # Find all context entries with dates
        pattern = r"#### \*\*([^:]+):[^*]*\*\* \((\d{4}-\d{2}-\d{2})\)"
        matches = re.findall(pattern, content)

        old_entries = []
        cutoff_date = datetime.now() - timedelta(days=max_age_days)

        for match in matches:
            try:
                entry_date = datetime.strptime(match[1], "%Y-%m-%d")
                if entry_date < cutoff_date:
                    old_entries.append(match[0])
            except ValueError:
                continue

        return old_entries

    def suggest_consolidation(self) -> dict[str, list[str]]:
        """Suggest consolidation strategies for README context."""
        suggestions = {"archive_old": [], "consolidate_similar": [], "prioritize_recent": []}

        # Find old entries
        old_entries = self.cleanup_old_context(90)
        if old_entries:
            suggestions["archive_old"] = old_entries

        # Analyze current context for similar patterns
        if self.readme_path.exists():
            content = self.readme_path.read_text()

            # Look for similar themes
            themes = {
                "performance": re.findall(r"B-\d+.*[Pp]erformance", content),
                "documentation": re.findall(r"B-\d+.*[Dd]ocumentation", content),
                "hooks": re.findall(r"B-\d+.*[Hh]ooks?", content),
                "memory": re.findall(r"B-\d+.*[Mm]emory", content),
            }

            for theme, items in themes.items():
                if len(items) > 2:
                    suggestions["consolidate_similar"].extend(items)

        return suggestions

    def generate_management_report(self) -> str:
        """Generate a comprehensive management report."""
        backlog_items = self.analyze_backlog_items(30)

        # Calculate scores
        for backlog_id, data in backlog_items.items():
            data["impact_score"] = self.calculate_impact_score(backlog_id, data["commits"])
            data["complexity_score"] = self.calculate_complexity_score(backlog_id, data["commits"])
            data["documentation_needed"] = self.determine_documentation_needed(
                data["impact_score"], data["complexity_score"]
            )

        # Generate suggestions
        suggestions = self.suggest_consolidation()

        report = f"""# README Context Management Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Current State
- **Total Backlog Items**: {len(backlog_items)}
- **Need Documentation**: {sum(1 for item in backlog_items.values() if item['documentation_needed'])}
- **High Priority**: {sum(1 for item in backlog_items.values() if item.get('impact_score', 0) >= 6)}
- **Medium Priority**: {sum(1 for item in backlog_items.values() if 4 <= item.get('impact_score', 0) < 6)}

## Recommendations

### 1. Document These High-Priority Items:
"""

        high_priority = [
            (bid, data)
            for bid, data in backlog_items.items()
            if data["documentation_needed"] and (data["impact_score"] >= 6 or data["complexity_score"] >= 6)
        ]
        high_priority.sort(key=lambda x: x[1]["impact_score"], reverse=True)

        for backlog_id, data in high_priority[:5]:
            report += (
                f"- **{backlog_id}**: Impact {data['impact_score']}/10, Complexity {data['complexity_score']}/10\n"
            )

        report += "\n### 2. Consolidation Opportunities:\n"
        if suggestions["consolidate_similar"]:
            for item in suggestions["consolidate_similar"][:5]:
                report += f"- {item}\n"
        else:
            report += "- No consolidation opportunities identified\n"

        report += "\n### 3. Cleanup Candidates:\n"
        if suggestions["archive_old"]:
            for item in suggestions["archive_old"][:5]:
                report += f"- {item} (old entry)\n"
        else:
            report += "- No old entries identified for cleanup\n"

        return report


def main():
    """Main function for README context management."""
    import argparse

    parser = argparse.ArgumentParser(description="Manage README context documentation")
    parser.add_argument("--analyze", action="store_true", help="Analyze current state")
    parser.add_argument("--report", action="store_true", help="Generate management report")
    parser.add_argument("--consolidate", action="store_true", help="Suggest consolidation")
    parser.add_argument("--days", type=int, default=30, help="Days to analyze")

    args = parser.parse_args()

    manager = READMEContextManager()

    if args.report:
        print(manager.generate_management_report())
    elif args.consolidate:
        suggestions = manager.suggest_consolidation()
        print(json.dumps(suggestions, indent=2))
    else:
        # Default: analyze
        backlog_items = manager.analyze_backlog_items(args.days)
        print(f"Analyzed {len(backlog_items)} backlog items")
        print(
            f"Need documentation: {sum(1 for item in backlog_items.values() if item.get('documentation_needed', False))}"
        )


if __name__ == "__main__":
    main()
