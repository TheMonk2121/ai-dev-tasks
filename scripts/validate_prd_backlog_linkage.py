#!/usr/bin/env python3.12.123.11
"""
PRD-Backlog Linkage Validator

Validates that PRDs properly reference their backlog items and vice versa,
including enhanced dependency tracking and impact scope documentation.
"""

import re
import sys
from pathlib import Path


class PRDBacklogLinkageValidator:
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.backlog_file = self.repo_root / "000_core" / "000_backlog.md"
        # Exclude archived PRDs
        self.prd_files = [
            f
            for f in self.repo_root.glob("PRD-B-*.md")
            if not str(f).startswith(str(self.repo_root / "600_archives"))
        ]
        self.errors = []
        self.warnings = []

    def validate_all(self) -> bool:
        """Run all validation checks."""
        print("🔍 Validating PRD-Backlog Linkage...")

        # Load backlog items
        backlog_items = self._parse_backlog_items()

        # Validate PRDs
        prd_items = self._validate_prds(backlog_items)

        # Validate backlog references
        self._validate_backlog_references(backlog_items, prd_items)

        # Validate dependency consistency
        self._validate_dependency_consistency(backlog_items, prd_items)

        # Report results
        self._report_results()

        return len(self.errors) == 0

    def _parse_backlog_items(self) -> dict[str, dict]:
        """Parse backlog items from 000_backlog.md."""
        backlog_items = {}

        if not self.backlog_file.exists():
            self.errors.append(f"Backlog file not found: {self.backlog_file}")
            return backlog_items

        content = self.backlog_file.read_text()

        # Find backlog items (B-XXX format)
        backlog_pattern = r"\| (B-\d+) \| ([^|]+) \| [^|]+ \| \d+ \| ([^|]+) \|"
        matches = re.findall(backlog_pattern, content)

        for item_id, title, status in matches:
            backlog_items[item_id] = {
                "title": title.strip(),
                "status": status.strip(),
                "prd_reference": None,
                "dependencies": [],
            }

            # Extract PRD reference from metadata
            prd_pattern = (
                rf'<!-- reference_cards: \[[^\]]*"PRD-{item_id}[^"]*"[^\]]*\] -->'
            )
            if re.search(prd_pattern, content):
                backlog_items[item_id]["prd_reference"] = f"PRD-{item_id}"

        return backlog_items

    def _validate_prds(self, backlog_items: dict[str, dict]) -> dict[str, dict]:
        """Validate PRD files and extract their information."""
        prd_items = {}

        for prd_file in self.prd_files:
            content = prd_file.read_text()
            prd_name = prd_file.stem

            # Extract backlog item reference
            backlog_match = re.search(r"\*\*Backlog Item\*\*: (B-\d+)", content)
            if not backlog_match:
                self.errors.append(f"PRD {prd_name} missing backlog item reference")
                continue

            backlog_id = backlog_match.group(1)
            prd_items[backlog_id] = {
                "file": prd_file,
                "name": prd_name,
                "backlog_id": backlog_id,
                "status": self._extract_status(content),
                "dependencies": self._extract_dependencies(content),
                "impact_scope": self._extract_impact_scope(content),
            }

            # Check if backlog item exists
            if backlog_id not in backlog_items:
                self.errors.append(
                    f"PRD {prd_name} references non-existent backlog item {backlog_id}"
                )
            else:
                backlog_items[backlog_id]["prd_reference"] = prd_name

        return prd_items

    def _extract_status(self, content: str) -> str:
        """Extract status from PRD content."""
        status_match = re.search(r"\*\*Status\*\*: ([^\n]+)", content)
        return status_match.group(1).strip() if status_match else "Unknown"

    def _extract_dependencies(self, content: str) -> dict[str, list[str]]:
        """Extract dependencies from PRD content."""
        dependencies = {"upstream": [], "downstream": [], "blocking": []}

        # Extract upstream dependencies
        upstream_match = re.search(r"\*\*Upstream\*\*: ([^\n]+)", content)
        if upstream_match:
            upstream_text = upstream_match.group(1)
            dependencies["upstream"] = self._extract_item_ids(upstream_text)

        # Extract downstream dependencies
        downstream_match = re.search(r"\*\*Downstream\*\*: ([^\n]+)", content)
        if downstream_match:
            downstream_text = downstream_match.group(1)
            dependencies["downstream"] = self._extract_item_ids(downstream_text)

        # Extract blocking dependencies
        blocking_match = re.search(r"\*\*Blocking\*\*: ([^\n]+)", content)
        if blocking_match:
            blocking_text = blocking_match.group(1)
            dependencies["blocking"] = self._extract_item_ids(blocking_text)

        return dependencies

    def _extract_impact_scope(self, content: str) -> dict[str, str]:
        """Extract impact scope from PRD content."""
        impact_scope = {"direct": "", "indirect": "", "public_contracts": ""}

        # Extract direct impact
        direct_match = re.search(r"\*\*Direct\*\*: ([^\n]+)", content)
        if direct_match:
            impact_scope["direct"] = direct_match.group(1).strip()

        # Extract indirect impact
        indirect_match = re.search(r"\*\*Indirect\*\*: ([^\n]+)", content)
        if indirect_match:
            impact_scope["indirect"] = indirect_match.group(1).strip()

        # Extract public contracts impact
        public_match = re.search(r"\*\*Public Contracts\*\*: ([^\n]+)", content)
        if public_match:
            impact_scope["public_contracts"] = public_match.group(1).strip()

        return impact_scope

    def _extract_item_ids(self, text: str) -> list[str]:
        """Extract B-XXX item IDs from text."""
        return re.findall(r"B-\d+", text)

    def _validate_backlog_references(
        self, backlog_items: dict[str, dict], prd_items: dict[str, dict]
    ):
        """Validate that backlog items properly reference their PRDs."""
        for item_id, item_data in backlog_items.items():
            if item_id in prd_items:
                # Backlog item has PRD, check if it's referenced
                if not item_data["prd_reference"]:
                    self.warnings.append(
                        f"Backlog item {item_id} has PRD but no reference in backlog metadata"
                    )
            else:
                # Backlog item has no PRD, check if it should have one
                if item_data["status"] == "todo" and "PRD" in item_data["title"]:
                    self.warnings.append(
                        f"Backlog item {item_id} mentions PRD but no PRD file found"
                    )

    def _validate_dependency_consistency(
        self, backlog_items: dict[str, dict], prd_items: dict[str, dict]
    ):
        """Validate that dependencies are consistent between backlog and PRDs."""
        for item_id, prd_data in prd_items.items():
            # Check upstream dependencies exist
            for upstream_id in prd_data["dependencies"]["upstream"]:
                if upstream_id not in backlog_items:
                    self.errors.append(
                        f"PRD {prd_data['name']} references non-existent upstream dependency {upstream_id}"
                    )

            # Check downstream dependencies exist
            for downstream_id in prd_data["dependencies"]["downstream"]:
                if downstream_id not in backlog_items:
                    self.warnings.append(
                        f"PRD {prd_data['name']} references non-existent downstream dependency {downstream_id}"
                    )

    def _report_results(self):
        """Report validation results."""
        print("\n📊 Validation Results:")
        print(f"   PRD files found: {len(self.prd_files)}")
        print(f"   Errors: {len(self.errors)}")
        print(f"   Warnings: {len(self.warnings)}")

        if self.errors:
            print("\n❌ Errors:")
            for error in self.errors:
                print(f"   - {error}")

        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   - {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All PRD-Backlog linkages are valid!")
        elif not self.errors:
            print("\n✅ No critical errors found, but check warnings above.")
        else:
            print("\n❌ Critical errors found. Please fix before proceeding.")


def main():
    """Main entry point."""
    validator = PRDBacklogLinkageValidator()
    success = validator.validate_all()

    if not success:
        print("\n💡 To fix these issues:")
        print("   1. Ensure all PRDs have '**Backlog Item**: B-XXX' in their header")
        print("   2. Ensure all backlog items with PRDs reference the PRD file")
        print("   3. Include dependency information (upstream, downstream, blocking)")
        print("   4. Include impact scope (direct, indirect, public contracts)")
        sys.exit(1)

    print("\n🎉 PRD-Backlog linkage validation passed!")


if __name__ == "__main__":
    main()
