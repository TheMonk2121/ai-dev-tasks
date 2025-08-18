#!/usr/bin/env python3.12.123.11
"""
Few-Shot Integration Framework

Reusable framework for loading and applying few-shot examples across documentation tools.
This enhances AI pattern recognition and validation accuracy using example-based learning.

Usage:
    from few_shot_integration import FewShotExampleLoader

    loader = FewShotExampleLoader()
    examples = loader.load_examples_by_category("documentation_coherence")
    patterns = loader.extract_patterns(examples)
"""

import json
import re
from pathlib import Path
from typing import Any


class FewShotExampleLoader:
    """Load and manage few-shot examples for AI pattern recognition."""

    def __init__(self, examples_file: str = "400_guides/400_few-shot-context-examples.md"):
        self.examples_file = Path(examples_file)
        self._examples_cache = None
        self._patterns_cache = {}

    def load_examples(self) -> dict[str, list[dict[str, Any]]]:
        """Load all few-shot examples from the examples file."""
        if self._examples_cache is not None:
            return self._examples_cache

        if not self.examples_file.exists():
            print(f"⚠️  Few-shot examples file not found: {self.examples_file}")
            return {}

        try:
            content = self.examples_file.read_text(encoding="utf-8")
            examples = self._parse_examples(content)
            self._examples_cache = examples
            return examples
        except Exception as e:
            print(f"❌ Error loading few-shot examples: {e}")
            return {}

    def _parse_examples(self, content: str) -> dict[str, list[dict[str, Any]]]:
        """Parse examples from markdown content."""
        examples = {"documentation_coherence": [], "backlog_analysis": [], "memory_context": []}

        current_category = None
        current_example = {}

        lines = content.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Detect category headers
            if line.startswith("## 📚 Documentation Coherence Examples"):
                current_category = "documentation_coherence"
                i += 1
                continue
            elif line.startswith("## 📋 Backlog Analysis Examples"):
                current_category = "backlog_analysis"
                i += 1
                continue
            elif line.startswith("## 🧠 Memory Context Examples"):
                current_category = "memory_context"
                i += 1
                continue
            elif line.startswith("## "):
                current_category = None
                i += 1
                continue

            # Detect example sections
            if line.startswith("### **") and current_category:
                # Start new example
                if current_example:
                    examples[current_category].append(current_example)

                current_example = {
                    "title": line.replace("### **", "").replace("**", "").strip(),
                    "context": "",
                    "input": "",
                    "expected_output": "",
                    "pattern": "",
                    "validation": "",
                }

                # Look for context, input, expected output, pattern, validation
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()

                    if next_line.startswith("### **"):
                        break
                    elif next_line.startswith("- *Context:**"):
                        current_example["context"] = next_line.replace("- *Context:**", "").strip()
                    elif next_line.startswith("- *Input:**"):
                        # Collect input until we hit the next section
                        input_lines = []
                        i += 1
                        while i < len(lines):
                            if lines[i].strip().startswith("- *Expected Output:**"):
                                break
                            input_lines.append(lines[i])
                            i += 1
                        current_example["input"] = "\n".join(input_lines).strip()
                        continue
                    elif next_line.startswith("- *Expected Output:**"):
                        # Collect expected output until we hit the next section
                        output_lines = []
                        i += 1
                        while i < len(lines):
                            if lines[i].strip().startswith("- *Pattern:**"):
                                break
                            output_lines.append(lines[i])
                            i += 1
                        current_example["expected_output"] = "\n".join(output_lines).strip()
                        continue
                    elif next_line.startswith("- *Pattern:**"):
                        current_example["pattern"] = next_line.replace("- *Pattern:**", "").strip()
                    elif next_line.startswith("- *Validation:**"):
                        current_example["validation"] = next_line.replace("- *Validation:**", "").strip()

                    i += 1
                continue

            i += 1

        # Add the last example
        if current_example and current_category:
            examples[current_category].append(current_example)

        return examples

    def load_examples_by_category(self, category: str) -> list[dict[str, Any]]:
        """Load examples for a specific category."""
        examples = self.load_examples()
        return examples.get(category, [])

    def extract_patterns(self, examples: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Extract patterns from examples for pattern matching."""
        patterns = []

        for example in examples:
            pattern = {
                "title": example.get("title", ""),
                "context": example.get("context", ""),
                "input_pattern": self._extract_input_pattern(example.get("input", "")),
                "output_pattern": self._extract_output_pattern(example.get("expected_output", "")),
                "validation_rules": self._extract_validation_rules(example.get("validation", "")),
                "pattern_description": example.get("pattern", ""),
            }
            patterns.append(pattern)

        return patterns

    def _extract_input_pattern(self, input_text: str) -> dict[str, Any]:
        """Extract input pattern from example input."""
        patterns = {
            "file_naming": r'filename:\s*"([^"]+)"',
            "cross_references": r"<!--\s*([A-Z_]+):\s*([^>]+?)\s*-->",
            "backlog_items": r"\|\s*B‑\d+\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|",
            "memory_context": r"<!--\s*MEMORY_CONTEXT:\s*([^>]+?)\s*-->",
            "structure_elements": r"^#{1,6}\s+([^\n]+)$",
            "json_structures": r"\{[^{}]*\}",
        }

        extracted = {}
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, input_text, re.MULTILINE)
            if matches:
                extracted[pattern_name] = matches

        return extracted

    def _extract_output_pattern(self, output_text: str) -> dict[str, Any]:
        """Extract output pattern from example expected output."""
        # Look for JSON structures in the output
        json_patterns = re.findall(r"\{[^{}]*\}", output_text)
        if json_patterns:
            try:
                # Try to parse the first JSON structure
                return {"json_structure": json.loads(json_patterns[0])}
            except:
                pass

        return {"raw_output": output_text.strip()}

    def _extract_validation_rules(self, validation_text: str) -> list[str]:
        """Extract validation rules from example validation."""
        rules = []

        # Extract validation patterns
        validation_patterns = [
            r"Check\s+for\s+([^\.]+)",
            r"Verify\s+([^\.]+)",
            r"Ensure\s+([^\.]+)",
            r"Validate\s+([^\.]+)",
        ]

        for pattern in validation_patterns:
            matches = re.findall(pattern, validation_text, re.IGNORECASE)
            rules.extend(matches)

        return rules

    def apply_patterns_to_content(self, content: str, patterns: list[dict[str, Any]]) -> dict[str, Any]:
        """Apply few-shot patterns to content for enhanced validation."""
        results = {"matched_patterns": [], "validation_suggestions": [], "confidence_scores": {}}

        for pattern in patterns:
            confidence = self._calculate_pattern_confidence(content, pattern)
            if confidence > 0.3:  # Threshold for pattern matching
                results["matched_patterns"].append(
                    {"pattern": pattern["title"], "confidence": confidence, "context": pattern["context"]}
                )

                # Generate validation suggestions based on pattern
                suggestions = self._generate_validation_suggestions(content, pattern)
                results["validation_suggestions"].extend(suggestions)

                results["confidence_scores"][pattern["title"]] = confidence

        return results

    def _calculate_pattern_confidence(self, content: str, pattern: dict[str, Any]) -> float:
        """Calculate confidence score for pattern matching."""
        confidence = 0.0

        # Check input patterns
        input_patterns = pattern.get("input_pattern", {})
        for pattern_type, matches in input_patterns.items():
            if pattern_type == "file_naming":
                # Check for file naming patterns
                if re.search(r'filename:\s*"([^"]+)"', content):
                    confidence += 0.2
            elif pattern_type == "cross_references":
                # Check for cross-reference patterns
                if re.search(r"<!--\s*([A-Z_]+):\s*([^>]+?)\s*-->", content):
                    confidence += 0.3
            elif pattern_type == "backlog_items":
                # Check for backlog item patterns
                if re.search(r"\|\s*B‑\d+\s*\|", content):
                    confidence += 0.2
            elif pattern_type == "memory_context":
                # Check for memory context patterns
                if re.search(r"<!--\s*MEMORY_CONTEXT:\s*([^>]+?)\s*-->", content):
                    confidence += 0.3
            elif pattern_type == "structure_elements":
                # Check for structure elements
                if re.search(r"^#{1,6}\s+([^\n]+)$", content, re.MULTILINE):
                    confidence += 0.1

        return min(confidence, 1.0)

    def _generate_validation_suggestions(self, content: str, pattern: dict[str, Any]) -> list[str]:
        """Generate validation suggestions based on matched patterns."""
        suggestions = []
        validation_rules = pattern.get("validation_rules", [])

        for rule in validation_rules:
            if "naming conventions" in rule.lower():
                suggestions.append("Check file naming conventions")
            elif "cross-references" in rule.lower():
                suggestions.append("Validate cross-references exist")
            elif "structure" in rule.lower():
                suggestions.append("Verify document structure completeness")
            elif "backlog" in rule.lower():
                suggestions.append("Check backlog item formatting")
            elif "memory" in rule.lower():
                suggestions.append("Validate memory context patterns")

        return suggestions


def get_few_shot_loader() -> FewShotExampleLoader:
    """Get a configured few-shot example loader."""
    return FewShotExampleLoader()
