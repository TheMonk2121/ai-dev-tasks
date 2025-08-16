#!/usr/bin/env python3
"""
Few-Shot Cognitive Scaffolding Integration
------------------------------------------
Integrates few-shot examples into the cognitive scaffolding system for AI agents
to improve context understanding and response quality.

This module provides:
1. Few-shot example extraction and categorization
2. Dynamic few-shot injection into memory rehydration
3. Pattern-based example selection
4. Context-aware example filtering

Usage:
    python3 scripts/few_shot_cognitive_scaffolding.py --role implementer --task "code review"
    python3 scripts/few_shot_cognitive_scaffolding.py --extract-examples
    python3 scripts/few_shot_cognitive_scaffolding.py --validate-patterns
"""

import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add the dspy-rag-system src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dspy-rag-system", "src"))


@dataclass
class FewShotExample:
    """Represents a few-shot example with metadata."""

    pattern: str
    context: str
    input_example: str
    expected_output: str
    validation_criteria: str
    category: str
    priority: int = 1
    tags: List[str] = field(default_factory=list)
    source_file: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class CognitiveScaffold:
    """Represents a cognitive scaffold with few-shot examples."""

    role: str
    task_type: str
    base_context: str
    few_shot_examples: List[FewShotExample] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class FewShotCognitiveScaffolding:
    """Handles few-shot cognitive scaffolding for AI agents."""

    def __init__(self):
        self.examples_file = Path("data/few_shot_examples.jsonl")
        self.patterns_file = Path("data/cognitive_patterns.json")
        self.scaffolds_file = Path("data/cognitive_scaffolds.json")

        # Ensure data directory exists
        self.examples_file.parent.mkdir(exist_ok=True)

        # Load existing data
        self.examples = self._load_examples()
        self.patterns = self._load_patterns()
        self.scaffolds = self._load_scaffolds()

    def _load_examples(self) -> List[FewShotExample]:
        """Load few-shot examples from JSONL file."""
        examples = []
        if self.examples_file.exists():
            with open(self.examples_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        examples.append(FewShotExample(**data))
        return examples

    def _load_patterns(self) -> Dict[str, Any]:
        """Load cognitive patterns from JSON file."""
        if self.patterns_file.exists():
            with open(self.patterns_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _load_scaffolds(self) -> Dict[str, CognitiveScaffold]:
        """Load cognitive scaffolds from JSON file."""
        if self.scaffolds_file.exists():
            with open(self.scaffolds_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                scaffolds = {}
                for key, scaffold_data in data.items():
                    examples = [FewShotExample(**ex) for ex in scaffold_data.get("few_shot_examples", [])]
                    scaffolds[key] = CognitiveScaffold(
                        role=scaffold_data["role"],
                        task_type=scaffold_data["task_type"],
                        base_context=scaffold_data["base_context"],
                        few_shot_examples=examples,
                        patterns=scaffold_data.get("patterns", []),
                        metadata=scaffold_data.get("metadata", {}),
                    )
                return scaffolds
        return {}

    def extract_examples_from_docs(self) -> List[FewShotExample]:
        """Extract few-shot examples from documentation files."""
        examples = []

        # Extract from few-shot examples guide
        few_shot_file = Path("400_guides/400_few-shot-context-examples.md")
        if few_shot_file.exists():
            examples.extend(self._parse_few_shot_guide(few_shot_file))

        # Extract from other documentation files
        for file_path in Path("400_guides").glob("400_*.md"):
            if file_path.name != "400_few-shot-context-examples.md":
                examples.extend(self._parse_doc_for_examples(file_path))

        return examples

    def _parse_few_shot_guide(self, file_path: Path) -> List[FewShotExample]:
        """Parse the few-shot examples guide for structured examples."""
        examples = []
        content = file_path.read_text(encoding="utf-8")

        # Pattern to match structured examples
        example_pattern = r"### \*\*(\d+)\.\s*(.*?)\*\*\s*\n\n\*\*Context:\*\*(.*?)\*\*Input:\*\*```(?:markdown|text)?\n(.*?)```\s*\*\*Expected Output:\*\*```(?:json|text)?\n(.*?)```\s*\*\*Pattern:\*\*(.*?)\*\*Validation:\*\*(.*?)(?=\n###|\Z)"

        matches = re.finditer(example_pattern, content, re.DOTALL)

        for match in matches:
            example = FewShotExample(
                pattern=match.group(2).strip(),
                context=match.group(3).strip(),
                input_example=match.group(4).strip(),
                expected_output=match.group(5).strip(),
                validation_criteria=match.group(7).strip(),
                category="documentation_coherence",
                priority=1,
                tags=["documentation", "validation"],
                source_file=str(file_path),
                line_number=content[: match.start()].count("\n") + 1,
            )
            examples.append(example)

        return examples

    def _parse_doc_for_examples(self, file_path: Path) -> List[FewShotExample]:
        """Parse documentation files for implicit examples."""
        examples = []
        content = file_path.read_text(encoding="utf-8")

        # Look for code blocks that might be examples
        code_block_pattern = r"```(?:python|bash|json|yaml)\n(.*?)```"
        code_blocks = re.finditer(code_block_pattern, content, re.DOTALL)

        for i, match in enumerate(code_blocks):
            code = match.group(1).strip()

            # Skip if it's just a simple command or configuration
            if len(code.split("\n")) < 3:
                continue

            # Try to infer context from surrounding text
            start_pos = max(0, match.start() - 200)
            end_pos = min(len(content), match.end() + 200)
            context = content[start_pos:end_pos]

            # Extract heading if available
            heading_match = re.search(r"^#+\s*(.*?)$", context, re.MULTILINE)
            heading = heading_match.group(1) if heading_match else file_path.stem

            example = FewShotExample(
                pattern=f"{heading} example",
                context=f"Example from {file_path.name}",
                input_example=code,
                expected_output="Code execution or configuration",
                validation_criteria="Code runs without errors",
                category="code_example",
                priority=2,
                tags=["code", file_path.stem],
                source_file=str(file_path),
                line_number=content[: match.start()].count("\n") + 1,
            )
            examples.append(example)

        return examples

    def save_examples(self) -> None:
        """Save examples to JSONL file."""
        with open(self.examples_file, "w", encoding="utf-8") as f:
            for example in self.examples:
                f.write(json.dumps(example.__dict__, ensure_ascii=False) + "\n")

    def create_cognitive_scaffold(self, role: str, task_type: str, base_context: str) -> CognitiveScaffold:
        """Create a cognitive scaffold for a specific role and task type."""

        # Select relevant examples based on role and task
        relevant_examples = self._select_relevant_examples(role, task_type)

        # Generate patterns based on examples
        patterns = self._generate_patterns(relevant_examples)

        scaffold = CognitiveScaffold(
            role=role,
            task_type=task_type,
            base_context=base_context,
            few_shot_examples=relevant_examples,
            patterns=patterns,
            metadata={
                "created_at": datetime.now().isoformat(),
                "example_count": len(relevant_examples),
                "pattern_count": len(patterns),
            },
        )

        return scaffold

    def _select_relevant_examples(self, role: str, task_type: str) -> List[FewShotExample]:
        """Select relevant examples based on role and task type."""
        relevant_examples = []

        # Role-based filtering
        role_keywords = {
            "planner": ["plan", "strategy", "priorit", "roadmap", "backlog", "sprint"],
            "implementer": ["code", "implement", "develop", "refactor", "debug", "test"],
            "researcher": ["research", "analyze", "study", "investigate", "explore"],
        }

        task_keywords = role_keywords.get(role, [])

        for example in self.examples:
            # Check if example matches role keywords
            example_text = f"{example.pattern} {example.context} {example.input_example}".lower()
            relevance_score = sum(1 for keyword in task_keywords if keyword in example_text)

            # Also check tags
            if any(keyword in tag.lower() for tag in example.tags for keyword in task_keywords):
                relevance_score += 2

            if relevance_score > 0:
                # Sort by relevance score and priority
                example.metadata = {"relevance_score": relevance_score}
                relevant_examples.append(example)

        # Sort by relevance score (descending) and priority (ascending)
        relevant_examples.sort(key=lambda x: (x.metadata.get("relevance_score", 0), -x.priority), reverse=True)

        # Return top examples (limit to prevent context bloat)
        return relevant_examples[:5]

    def _generate_patterns(self, examples: List[FewShotExample]) -> List[str]:
        """Generate patterns from examples."""
        patterns = []

        for example in examples:
            # Extract common patterns from input examples
            if example.input_example:
                # Look for common structures
                if "```" in example.input_example:
                    patterns.append("code_block_processing")
                if "json" in example.expected_output.lower():
                    patterns.append("json_output_format")
                if "validation" in example.validation_criteria.lower():
                    patterns.append("validation_pattern")

        return list(set(patterns))

    def inject_into_memory_rehydration(self, scaffold: CognitiveScaffold, bundle_text: str) -> str:
        """Inject few-shot examples into memory rehydration bundle."""

        if not scaffold.few_shot_examples:
            return bundle_text

        # Create few-shot section
        few_shot_section = self._create_few_shot_section(scaffold)

        # Insert after the TL;DR section or at the beginning
        if "## 🔎 TL;DR" in bundle_text:
            # Insert after TL;DR
            parts = bundle_text.split("## 🔎 TL;DR", 1)
            if len(parts) == 2:
                tldr_parts = parts[1].split("\n\n", 1)
                if len(tldr_parts) == 2:
                    return parts[0] + "## 🔎 TL;DR" + tldr_parts[0] + "\n\n" + few_shot_section + "\n\n" + tldr_parts[1]

        # If no TL;DR section, insert at beginning
        return few_shot_section + "\n\n" + bundle_text

    def _create_few_shot_section(self, scaffold: CognitiveScaffold) -> str:
        """Create a formatted few-shot examples section."""
        lines = [
            "## 🎯 Few-Shot Cognitive Scaffolding",
            "",
            f"**Role**: {scaffold.role.title()}",
            f"**Task Type**: {scaffold.task_type}",
            f"**Examples**: {len(scaffold.few_shot_examples)} relevant patterns",
            "",
            "### Relevant Examples:",
            "",
        ]

        for i, example in enumerate(scaffold.few_shot_examples, 1):
            lines.extend(
                [
                    f"#### Example {i}: {example.pattern}",
                    "",
                    f"**Context**: {example.context}",
                    "",
                    "**Input**:",
                    "```",
                    example.input_example,
                    "```",
                    "",
                    "**Expected Output**:",
                    "```",
                    example.expected_output,
                    "```",
                    "",
                    f"**Validation**: {example.validation_criteria}",
                    "",
                ]
            )

        if scaffold.patterns:
            lines.extend(["### Cognitive Patterns:", "", *[f"- {pattern}" for pattern in scaffold.patterns], ""])

        return "\n".join(lines)

    def validate_patterns(self) -> Dict[str, Any]:
        """Validate that patterns are working correctly."""
        validation_results = {
            "total_examples": len(self.examples),
            "total_patterns": len(self.patterns),
            "total_scaffolds": len(self.scaffolds),
            "validation_errors": [],
            "warnings": [],
        }

        # Check for duplicate patterns
        pattern_counts = {}
        for example in self.examples:
            pattern_counts[example.pattern] = pattern_counts.get(example.pattern, 0) + 1

        for pattern, count in pattern_counts.items():
            if count > 1:
                validation_results["warnings"].append(f"Duplicate pattern: {pattern} ({count} times)")

        # Check for missing validation criteria
        for example in self.examples:
            if not example.validation_criteria or example.validation_criteria.strip() == "":
                validation_results["validation_errors"].append(f"Missing validation criteria for: {example.pattern}")

        # Check for invalid JSON in expected output
        for example in self.examples:
            if "json" in example.expected_output.lower():
                try:
                    json.loads(example.expected_output)
                except json.JSONDecodeError:
                    validation_results["validation_errors"].append(
                        f"Invalid JSON in expected output for: {example.pattern}"
                    )

        return validation_results


def main():
    """Main entry point for few-shot cognitive scaffolding."""
    import argparse

    parser = argparse.ArgumentParser(description="Few-Shot Cognitive Scaffolding Integration")
    parser.add_argument("--role", choices=["planner", "implementer", "researcher"], help="Role for scaffold generation")
    parser.add_argument("--task", help="Task description for context")
    parser.add_argument("--extract-examples", action="store_true", help="Extract examples from documentation")
    parser.add_argument("--validate-patterns", action="store_true", help="Validate existing patterns")
    parser.add_argument("--create-scaffold", action="store_true", help="Create a cognitive scaffold")
    parser.add_argument("--output-file", help="Output file for scaffold")

    args = parser.parse_args()

    scaffolding = FewShotCognitiveScaffolding()

    if args.extract_examples:
        print("Extracting few-shot examples from documentation...")
        new_examples = scaffolding.extract_examples_from_docs()
        scaffolding.examples.extend(new_examples)
        scaffolding.save_examples()
        print(f"Extracted {len(new_examples)} new examples")
        print(f"Total examples: {len(scaffolding.examples)}")

    if args.validate_patterns:
        print("Validating patterns...")
        results = scaffolding.validate_patterns()
        print(f"Total examples: {results['total_examples']}")
        print(f"Total patterns: {results['total_patterns']}")
        print(f"Total scaffolds: {results['total_scaffolds']}")

        if results["validation_errors"]:
            print("\nValidation Errors:")
            for error in results["validation_errors"]:
                print(f"  ❌ {error}")

        if results["warnings"]:
            print("\nWarnings:")
            for warning in results["warnings"]:
                print(f"  ⚠️ {warning}")

    if args.create_scaffold and args.role and args.task:
        print(f"Creating cognitive scaffold for {args.role} role...")
        scaffold = scaffolding.create_cognitive_scaffold(args.role, args.task, "Base context")

        if args.output_file:
            with open(args.output_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "role": scaffold.role,
                        "task_type": scaffold.task_type,
                        "base_context": scaffold.base_context,
                        "few_shot_examples": [ex.__dict__ for ex in scaffold.few_shot_examples],
                        "patterns": scaffold.patterns,
                        "metadata": scaffold.metadata,
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
            print(f"Scaffold saved to {args.output_file}")
        else:
            print("Scaffold created successfully")
            print(f"Examples: {len(scaffold.few_shot_examples)}")
            print(f"Patterns: {len(scaffold.patterns)}")

    if not any([args.extract_examples, args.validate_patterns, args.create_scaffold]):
        print("Few-Shot Cognitive Scaffolding Integration")
        print("Use --help for available options")
        print("\nExample usage:")
        print("  python3 scripts/few_shot_cognitive_scaffolding.py --extract-examples")
        print("  python3 scripts/few_shot_cognitive_scaffolding.py --validate-patterns")
        print(
            "  python3 scripts/few_shot_cognitive_scaffolding.py --create-scaffold --role implementer --task 'code review'"
        )


if __name__ == "__main__":
    main()
