#!/usr/bin/env python3
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
from typing import Any, Dict, List


class FewShotExampleLoader:
    """Load and manage few-shot examples for AI pattern recognition."""

    def __init__(self, examples_file: str = "data/few_shot_examples.jsonl"):
        self.examples_file = Path(examples_file)
        self._examples_cache = None
        self._patterns_cache = {}

        # Check if file exists, if not, try the old markdown location
        if not self.examples_file.exists():
            # Try the old markdown location
            old_file = Path("400_guides/400_few-shot-context-examples.md")
            if old_file.exists():
                self.examples_file = old_file
                print(f"✅ Using few-shot examples from: {self.examples_file}")
            else:
                print(f"⚠️  Few-shot examples file not found: {self.examples_file}")
                print("   Few-shot integration disabled - content covered by core guides")
                self._disabled = True
                return
        else:
            print(f"✅ Using few-shot examples from: {self.examples_file}")

        self._disabled = False

    def load_examples(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load all few-shot examples from the examples file."""
        if self._examples_cache is not None:
            return self._examples_cache

        # If disabled, return empty examples
        if hasattr(self, "_disabled") and self._disabled:
            return {}

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

    def _parse_examples(self, content: str) -> Dict[str, List[Dict[str, Any]]]:
        """Parse examples from markdown or JSONL content."""
        examples = {"documentation_coherence": [], "backlog_analysis": [], "memory_context": []}

        # Check if it's JSONL format
        if self.examples_file.suffix == ".jsonl":
            return self._parse_jsonl_examples(content)

        # Otherwise parse as markdown
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

    def _parse_jsonl_examples(self, content: str) -> Dict[str, List[Dict[str, Any]]]:
        """Parse examples from JSONL content."""
        examples = {"documentation_coherence": [], "backlog_analysis": [], "memory_context": []}

        try:
            import json

            lines = content.strip().split("\n")
            for line in lines:
                if line.strip():
                    example = json.loads(line)

                    # Normalize JSONL keys to match extract_patterns expectations
                    example["input"] = example.get("input_example", "")
                    example["validation"] = example.get("validation_criteria", "")
                    example["title"] = example.get("pattern", "")
                    # Keep original pattern for pattern_description
                    example["pattern_description"] = example.get("pattern", "")

                    category = example.get("category", "documentation_coherence")

                    # Map categories to our expected categories
                    if category in ["code_example", "documentation"]:
                        examples["documentation_coherence"].append(example)
                    elif category in ["backlog", "task"]:
                        examples["backlog_analysis"].append(example)
                    elif category in ["memory", "context"]:
                        examples["memory_context"].append(example)
                    else:
                        # Default to documentation_coherence
                        examples["documentation_coherence"].append(example)
        except Exception as e:
            print(f"❌ Error parsing JSONL examples: {e}")

        # Log counts per category for diagnostics
        for category, items in examples.items():
            if items:
                print(f"✅ Loaded {len(items)} few-shot examples for {category}")

        return examples

    def load_examples_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Load examples for a specific category."""
        examples = self.load_examples()
        return examples.get(category, [])

    def extract_patterns(self, examples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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

    def _extract_input_pattern(self, input_text: str) -> Dict[str, Any]:
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

    def _extract_output_pattern(self, output_text: str) -> Dict[str, Any]:
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

    def _extract_validation_rules(self, validation_text: str) -> List[str]:
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

    def apply_patterns_to_content(
        self, content: str, patterns: List[Dict[str, Any]], threshold: float = 0.3
    ) -> Dict[str, Any]:
        """Apply few-shot patterns to content for enhanced validation.

        threshold: minimum confidence required to consider a pattern matched.
        """
        results = {"matched_patterns": [], "validation_suggestions": [], "confidence_scores": {}}

        for pattern in patterns:
            confidence = self._calculate_pattern_confidence(content, pattern)
            if confidence > threshold:
                results["matched_patterns"].append(
                    {"pattern": pattern["title"], "confidence": confidence, "context": pattern["context"]}
                )

                # Generate validation suggestions based on pattern
                suggestions = self._generate_validation_suggestions(content, pattern)
                results["validation_suggestions"].extend(suggestions)

                results["confidence_scores"][pattern["title"]] = confidence

        return results

    def _calculate_pattern_confidence(self, content: str, pattern: Dict[str, Any]) -> float:
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

        # Small base score if descriptive pattern text appears in content (case-insensitive)
        try:
            desc = (pattern.get("pattern_description", "") or "").strip()
            if desc and desc.lower() in content.lower():
                confidence += 0.1
        except Exception:
            pass

        return min(confidence, 1.0)

    def _generate_validation_suggestions(self, content: str, pattern: Dict[str, Any]) -> List[str]:
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
