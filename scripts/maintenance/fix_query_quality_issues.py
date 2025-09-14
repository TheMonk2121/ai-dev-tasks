from __future__ import annotations

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Optional, Union

from src.schemas.eval import GoldCase, Mode
from src.utils.gold_loader import load_gold_cases

#!/usr/bin/env python3
"""
Fix Query Quality Issues in Gold Test Cases

This script fixes query quality problems:
1. Convert non-questions to proper questions ending with '?'
2. Expand queries that are too short
3. Remove duplicate queries
4. Generalize file-specific queries to be more general
"""

# Add project root to path
sys.path.insert(0, ".")

class QueryQualityFixer:
    """Fix query quality issues in gold test cases."""

    def __init__(self, gold_file: str = "evals/gold/v1/gold_cases.jsonl"):
        self.gold_file = gold_file
        self.cases = load_gold_cases(gold_file)
        self.fixes_applied = []
        self.backup_file = f"{gold_file}.backup3"

    def create_backup(self):
        """Create backup of current gold file."""
        print(f"📁 Creating backup: {self.backup_file}")
        with open(self.gold_file) as src, open(self.backup_file, "w") as dst:
            dst.write(src.read())
        print("✅ Backup created")

    def fix_non_questions(self) -> list[GoldCase]:
        """Convert non-questions to proper questions ending with '?'."""
        print("\n❓ Fixing non-questions...")

        fixed_cases = []
        non_question_patterns = {
            # Common non-question patterns and their question equivalents
            "show the dspy development context tl;dr": "What is the DSPy development context TL;DR?",
            "give the high-level getting started index": "What is the high-level getting started index?",
            "show me the setup docs under 200_setup": "What are the setup docs under 200_setup?",
            "point me to memory-related guides under 100_memory": "What are the memory-related guides under 100_memory?",
            "postgresql": "What database technology should be used?",
            "hybrid search": "What search architecture should be implemented?",
            "vector search": "How should vector search be implemented?",
            "database choice": "What database should be chosen?",
            "search optimization": "How should search be optimized?",
            "pgvector": "What vector extension should be used?",
            "bm25": "What text search algorithm should be used?",
            "memory system": "What memory system architecture should be used?",
            "api design": "What API design should be implemented?",
        }

        for case in self.cases:
            query_lower = case.query.lower().strip()

            # Check if it's a non-question
            if not case.query.endswith("?"):
                # Try to find a pattern match
                if query_lower in non_question_patterns:
                    case.query = non_question_patterns[query_lower]
                    self.fixes_applied.append(f"Converted non-question: {case.id} -> {case.query}")
                else:
                    # Generic conversion
                    if query_lower.startswith(("show", "give", "point")):
                        case.query = f"What {case.query.lower()}?"
                    elif query_lower.startswith(("where", "how", "what", "which", "when", "why")):
                        case.query = f"{case.query}?"
                    else:
                        case.query = f"What is {case.query.lower()}?"
                    self.fixes_applied.append(f"Converted to question: {case.id} -> {case.query}")

            fixed_cases.append(case)

        print(f"✅ Fixed {len([c for c in self.cases if not c.query.endswith('?')])} non-questions")
        return fixed_cases

    def fix_short_queries(self) -> list[GoldCase]:
        """Expand queries that are too short (< 10 characters)."""
        print("\n📏 Fixing short queries...")

        fixed_cases = []
        short_query_expansions = {
            "pgvector": "What vector extension should be used for PostgreSQL?",
            "bm25": "What text search algorithm should be used for full-text search?",
        }

        for case in self.cases:
            if len(case.query.strip()) < 10:
                query_lower = case.query.lower().strip()

                if query_lower in short_query_expansions:
                    case.query = short_query_expansions[query_lower]
                    self.fixes_applied.append(f"Expanded short query: {case.id} -> {case.query}")
                else:
                    # Generic expansion
                    case.query = f"What is {case.query}?"
                    self.fixes_applied.append(f"Expanded short query: {case.id} -> {case.query}")

            fixed_cases.append(case)

        print(f"✅ Fixed {len([c for c in self.cases if len(c.query.strip()) < 10])} short queries")
        return fixed_cases

    def remove_duplicate_queries(self) -> list[GoldCase]:
        """Remove duplicate queries, keeping the first occurrence."""
        print("\n🔄 Removing duplicate queries...")

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

        print(f"✅ Removed {duplicates_removed} duplicate queries")
        return unique_cases

    def generalize_file_specific_queries(self) -> list[GoldCase]:
        """Generalize file-specific queries to be more general."""
        print("\n📄 Generalizing file-specific queries...")

        fixed_cases = []

        for case in self.cases:
            original_query = case.query
            generalized_query = self._generalize_query(original_query)

            if generalized_query != original_query:
                case.query = generalized_query
                self.fixes_applied.append(f"Generalized query: {case.id} -> {generalized_query}")

            fixed_cases.append(case)

        print("✅ Generalized file-specific queries")
        return fixed_cases

    def _generalize_query(self, query: str) -> str:
        """Generalize a file-specific query to be more general."""

        # Remove file-specific references
        generalizations = {
            # Remove "according to [file]" patterns
            r"according to [^,]+, ": "",
            r"according to [^?]+\?": r"\1",  # Will be handled separately
            # Remove specific file references
            r"400_09_ai-frameworks-dspy\.md": "the DSPy framework documentation",
            r"400_02_memory-rehydration-context-management\.md": "the memory system documentation",
            r"200_setup/200_naming-conventions\.md": "the naming conventions",
            r"100_memory/104_dspy-development-context\.md": "the DSPy development context",
            r"000_core/000_backlog\.md": "the backlog documentation",
            r"400_ai-constitution\.md": "the AI constitution",
            r"100_memory/100_database-troubleshooting-patterns\.md": "the database troubleshooting patterns",
            r"100_memory/103_memory-context-workflow\.md": "the memory context workflow",
            r"400_guides/400_guide-index\.md": "the guide index",
            r"200_setup/201_model-configuration\.md": "the model configuration",
            # Remove "see [directory]" patterns
            r"\(see [^)]+\)": "",
            r"see [^?]+\?": r"\1",  # Will be handled separately
            # Generalize directory references
            r"under 200_setup": "for setup",
            r"under 100_memory": "for memory management",
            r"under 000_core": "for core workflows",
            r"under 400_guides": "for guides",
        }

        generalized = query

        # Apply generalizations
        for pattern, replacement in generalizations.items():
            if replacement == r"\1":  # Special case for complex replacements
                # Handle "according to [file]" patterns
                if "according to" in pattern:
                    generalized = re.sub(
                        r"according to [^?]+\?",
                        lambda m: m.group(0).split("according to ")[1].split("?")[0] + "?",
                        generalized,
                    )
                # Handle "see [directory]" patterns
                elif "see" in pattern:
                    generalized = re.sub(
                        r"see [^?]+\?", lambda m: m.group(0).split("see ")[1].split("?")[0] + "?", generalized
                    )
            else:
                generalized = re.sub(pattern, replacement, generalized)

        # Clean up extra spaces and punctuation
        generalized = " ".join(generalized.split())
        if generalized.endswith(" ."):
            generalized = generalized[:-2] + "."
        if generalized.endswith(" ?"):
            generalized = generalized[:-2] + "?"

        return generalized

    def improve_query_clarity(self) -> list[GoldCase]:
        """Improve query clarity and specificity."""
        print("\n✨ Improving query clarity...")

        fixed_cases = []

        for case in self.cases:
            original_query = case.query
            improved_query = self._improve_clarity(original_query)

            if improved_query != original_query:
                case.query = improved_query
                self.fixes_applied.append(f"Improved clarity: {case.id} -> {improved_query}")

            fixed_cases.append(case)

        print("✅ Improved query clarity")
        return fixed_cases

    def _improve_clarity(self, query: str) -> str:
        """Improve the clarity of a query."""
        query_lower = query.lower()

        # Add context where needed
        improvements = {
            "what is dspy": "What is DSPy and how is it used in this project?",
            "how do i run the evals": "How do I run the evaluation tests?",
            "what is the memory rehydration protocol": "What is the memory rehydration protocol and how do I use it?",
            "how do i create a prd": "How do I create a Product Requirements Document (PRD)?",
            "what are the ragchecker baseline metrics": "What are the RAGChecker baseline performance metrics?",
            "how do i set up shell integration": "How do I set up shell integration for this project?",
            "what is the canary deployment percentage limit": "What is the canary deployment percentage limit and how is it configured?",
        }

        for pattern, improvement in improvements.items():
            if pattern in query_lower:
                return improvement

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
        """Run all query quality fixes."""
        print("🔧 Starting Query Quality Fixes")
        print("=" * 50)

        # Create backup
        self.create_backup()

        # Apply all fixes in sequence
        fixed_cases = self.fix_non_questions()
        fixed_cases = self.fix_short_queries()
        fixed_cases = self.remove_duplicate_queries()
        fixed_cases = self.generalize_file_specific_queries()
        fixed_cases = self.improve_query_clarity()

        # Save fixes
        self.save_fixed_cases(fixed_cases)

        # Report results
        print(f"\n📊 FIXES APPLIED: {len(self.fixes_applied)}")
        for fix in self.fixes_applied[:10]:  # Show first 10
            print(f"  ✅ {fix}")
        if len(self.fixes_applied) > 10:
            print(f"  ... and {len(self.fixes_applied) - 10} more fixes")

        print(f"\n✅ Query quality fixes complete! Backup saved to: {self.backup_file}")
        return len(self.fixes_applied)

def main():
    """Main function."""
    fixer = QueryQualityFixer()
    fixes_applied = fixer.run_fixes()

    print(f"\n🎯 PHASE 2.1 COMPLETE: {fixes_applied} query quality issues fixed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
