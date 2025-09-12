from __future__ import annotations
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List
from src.schemas.eval import GoldCase, Mode
from src.utils.gold_loader import load_gold_cases
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Fix Remaining Issues in Gold Test Cases

This script handles the remaining quality issues:
1. Remove remaining duplicate queries
2. Further generalize file-specific queries
3. Fix any remaining quality issues
"""

# Add project root to path
sys.path.insert(0, ".")

class RemainingIssuesFixer:
    """Fix remaining quality issues in gold test cases."""

    def __init__(self, gold_file: str = "evals/gold/v1/gold_cases.jsonl"):
        self.gold_file = gold_file
        self.cases = load_gold_cases(gold_file)
        self.fixes_applied = []
        self.backup_file = f"{gold_file}.backup4"

    def create_backup(self):
        """Create backup of current gold file."""
        print(f"📁 Creating backup: {self.backup_file}")
        with open(self.gold_file) as src, open(self.backup_file, "w") as dst:
            dst.write(src.read())
        print("✅ Backup created")

    def remove_remaining_duplicates(self) -> list[GoldCase]:
        """Remove any remaining duplicate queries."""
        print("\n🔄 Removing remaining duplicates...")

        seen_queries = set()
        unique_cases = []
        duplicates_removed = 0

        for case in self.cases:
            query_normalized = case.query.strip().lower()

            if query_normalized not in seen_queries:
                seen_queries.add(query_normalized)
                unique_cases.append(case)
            else:
                duplicates_removed += 1
                self.fixes_applied.append(f"Removed duplicate: {case.id} - '{case.query}'")

        print(f"✅ Removed {duplicates_removed} remaining duplicates")
        return unique_cases

    def further_generalize_queries(self) -> list[GoldCase]:
        """Further generalize file-specific queries."""
        print("\n📄 Further generalizing file-specific queries...")

        fixed_cases = []

        for case in self.cases:
            original_query = case.query
            generalized_query = self._further_generalize(original_query)

            if generalized_query != original_query:
                case.query = generalized_query
                self.fixes_applied.append(f"Further generalized: {case.id} -> {generalized_query}")

            fixed_cases.append(case)

        print("✅ Further generalized file-specific queries")
        return fixed_cases

    def _further_generalize(self, query: str) -> str:
        """Further generalize a query."""
        query_lower = query.lower()

        # More aggressive generalizations
        generalizations = {
            # Remove remaining file references
            r"400_09_ai-frameworks-dspy": "DSPy framework",
            r"400_02_memory-rehydration": "memory system",
            r"200_setup/200_naming-conventions": "naming conventions",
            r"100_memory/104_dspy-development-context": "DSPy development context",
            r"000_core/000_backlog": "backlog",
            r"400_ai-constitution": "AI constitution",
            r"100_memory/100_database-troubleshooting-patterns": "database troubleshooting",
            r"100_memory/103_memory-context-workflow": "memory context workflow",
            r"400_guides/400_guide-index": "guide index",
            r"200_setup/201_model-configuration": "model configuration",
            # Remove directory references
            r"under 200_setup": "for setup",
            r"under 100_memory": "for memory management",
            r"under 000_core": "for core workflows",
            r"under 400_guides": "for guides",
            # Clean up awkward phrasing
            r"what show the": "what is the",
            r"what give the": "what is the",
            r"what point me to": "what are",
            r"what show me the": "what are the",
        }

        generalized = query

        # Apply generalizations
        for pattern, replacement in generalizations.items():
            generalized = generalized.replace(pattern, replacement)

        # Clean up extra spaces and punctuation
        generalized = " ".join(generalized.split())
        if generalized.endswith(" ."):
            generalized = generalized[:-2] + "."
        if generalized.endswith(" ?"):
            generalized = generalized[:-2] + "?"

        return generalized

    def fix_awkward_questions(self) -> list[GoldCase]:
        """Fix awkwardly formed questions."""
        print("\n🔧 Fixing awkward questions...")

        fixed_cases = []

        for case in self.cases:
            original_query = case.query
            fixed_query = self._fix_awkward_question(original_query)

            if fixed_query != original_query:
                case.query = fixed_query
                self.fixes_applied.append(f"Fixed awkward question: {case.id} -> {fixed_query}")

            fixed_cases.append(case)

        print("✅ Fixed awkward questions")
        return fixed_cases

    def _fix_awkward_question(self, query: str) -> str:
        """Fix awkwardly formed questions."""
        query_lower = query.lower()

        # Fix common awkward patterns
        fixes = {
            "what show the dspy development context tl;dr.": "What is the DSPy development context TL;DR?",
            "what give the high-level getting started index.": "What is the high-level getting started index?",
            "what show me the setup docs under 200_setup.": "What are the setup documentation files?",
            "what point me to memory-related guides under 100_memory.": "What are the memory-related guides?",
        }

        if query_lower in fixes:
            return fixes[query_lower]

        return query

    def save_fixed_cases(self, cases: list[GoldCase]):
        """Save fixed cases back to the gold file."""
        print(f"\n💾 Saving fixed cases to {self.gold_file}")

        with open(self.gold_file, "w") as f:
            for case in cases:
                # Convert to dict and write as JSON line
                case_dict = case.model_dump(by_alias=True)
                f.write(json.dumps(case_dict) + "\n")

        print("✅ Fixed cases saved")

    def run_fixes(self):
        """Run all remaining fixes."""
        print("🔧 Starting Remaining Issues Fixes")
        print("=" * 50)

        # Create backup
        self.create_backup()

        # Apply all fixes in sequence
        fixed_cases = self.remove_remaining_duplicates()
        fixed_cases = self.further_generalize_queries()
        fixed_cases = self.fix_awkward_questions()

        # Save fixes
        self.save_fixed_cases(fixed_cases)

        # Report results
        print(f"\n📊 FIXES APPLIED: {len(self.fixes_applied)}")
        for fix in self.fixes_applied[:10]:  # Show first 10
            print(f"  ✅ {fix}")
        if len(self.fixes_applied) > 10:
            print(f"  ... and {len(self.fixes_applied) - 10} more fixes")

        print(f"\n✅ Remaining issues fixes complete! Backup saved to: {self.backup_file}")
        return len(self.fixes_applied)

def main():
    """Main function."""
    fixer = RemainingIssuesFixer()
    fixes_applied = fixer.run_fixes()

    print(f"\n🎯 PHASE 2.2 COMPLETE: {fixes_applied} remaining issues fixed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
