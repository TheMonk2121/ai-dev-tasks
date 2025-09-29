#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.schemas.eval import GoldCase, Mode
from src.utils.gold_loader import load_gold_cases

"""
Hypothesis Analysis for Gold Test Cases

This script performs a comprehensive analysis of gold test cases to identify:
1. Data quality issues
2. Schema validation problems
3. File existence issues
4. Query quality assessment
5. Answer quality assessment
6. Coverage analysis
7. Duplicate detection
8. Mode consistency
"""

# Add project root to path
sys.path.insert(0, ".")

class GoldCaseHypothesisAnalysis:
    """Comprehensive analysis of gold test cases."""

    def __init__(self, gold_file: str = "evals/gold/v1/gold_cases.jsonl"):
        self.gold_file = gold_file
        self.cases = load_gold_cases(gold_file)
        self.analysis_results = {}

    def run_analysis(self) -> dict[str, Any]:
        """Run comprehensive hypothesis analysis."""
        print("🔍 Running Gold Test Case Hypothesis Analysis...")
        print(f"📊 Analyzing {len(self.cases)} test cases from {self.gold_file}")
        print("=" * 80)

        # Run all analysis modules
        self.analysis_results = {
            "basic_stats": self._analyze_basic_stats(),
            "schema_validation": self._analyze_schema_validation(),
            "file_existence": self._analyze_file_existence(),
            "query_quality": self._analyze_query_quality(),
            "answer_quality": self._analyze_answer_quality(),
            "coverage_analysis": self._analyze_coverage(),
            "duplicate_detection": self._analyze_duplicates(),
            "mode_consistency": self._analyze_mode_consistency(),
            "tag_analysis": self._analyze_tags(),
            "hypothesis_violations": self._analyze_hypothesis_violations(),
        }

        return self.analysis_results

    def _analyze_basic_stats(self) -> dict[str, Any]:
        """Analyze basic statistics."""
        print("\n📈 Basic Statistics")
        print("-" * 40)

        stats = {
            "total_cases": len(self.cases),
            "modes": Counter(case.mode for case in self.cases),
            "tags": Counter(tag for case in self.cases for tag in case.tags),
            "categories": Counter(case.category for case in self.cases if case.category),
            "cases_with_gt_answer": sum(1 for case in self.cases if case.gt_answer),
            "cases_with_expected_files": sum(1 for case in self.cases if case.expected_files),
            "cases_with_globs": sum(1 for case in self.cases if case.globs),
            "cases_with_expected_decisions": sum(1 for case in self.cases if case.expected_decisions),
        }

        print(f"Total cases: {stats['total_cases']}")
        print(f"Modes: {dict(stats['modes'])}")
        print(f"Top 10 tags: {dict(stats['tags'].most_common(10))}")
        print(f"Categories: {dict(stats['categories'])}")
        print(f"Cases with ground truth answers: {stats['cases_with_gt_answer']}")
        print(f"Cases with expected files: {stats['cases_with_expected_files']}")
        print(f"Cases with globs: {stats['cases_with_globs']}")
        print(f"Cases with expected decisions: {stats['cases_with_expected_decisions']}")

        return stats
    def _analyze_schema_validation(self) -> dict[str, Any]:
        """Analyze schema validation issues."""
        print("\n🔍 Schema Validation Analysis")
        print("-" * 40)

        issues = {
            "missing_required_fields": [],
            "invalid_modes": [],
            "empty_queries": [],
            "empty_tags": [],
            "mode_requirement_violations": [],
        }

        for case in self.cases:
            # Check required fields
            if not case.id:
                issues["missing_required_fields"].append("Case missing ID")
            if not case.query:
                issues["missing_required_fields"].append(f"Case {case.id}: Missing query")
            if not case.tags:
                issues["missing_required_fields"].append(f"Case {case.id}: Missing tags")

            # Check mode requirements
            if case.mode == Mode.reader and not case.gt_answer:
                issues["mode_requirement_violations"].append(f"Case {case.id}: Reader mode missing ground truth answer")
            elif case.mode == Mode.retrieval and not case.expected_files and not case.globs:
                issues["mode_requirement_violations"].append(f"Case {case.id}: Retrieval mode missing expected_files or globs")
            elif case.mode == Mode.decision and not case.expected_decisions:
                issues["mode_requirement_violations"].append(f"Case {case.id}: Decision mode missing expected_decisions")

        total_issues = sum(len(v) for v in issues.values())
        print(f"Schema issues found: {total_issues}")
        if total_issues > 0:
            print("First 10 issues:")
            all_issues = []
            for issue_list in issues.values():
                all_issues.extend(issue_list)
            for issue in all_issues[:10]:
                print(f"  - {issue}")
            if total_issues > 10:
                print(f"  ... and {total_issues - 10} more")

        return {
            "validation_errors": issues,
            "total_issues": total_issues
        }
    def _analyze_file_existence(self) -> dict[str, Any]:
        """Analyze file existence issues."""
        print("\n📁 File Existence Analysis")
        print("-" * 40)

        missing_files = []
        existing_files = []

        for case in self.cases:
            if case.expected_files:
                for file_path in case.expected_files:
                    if Path(file_path).exists():
                        existing_files.append(file_path)
                    else:
                        missing_files.append((case.id, file_path))

        print(f"Expected files checked: {len(existing_files) + len(missing_files)}")
        print(f"Missing files: {len(missing_files)}")
        print(f"Existing files: {len(existing_files)}")
        print(f"File existence rate: {len(existing_files) / (len(existing_files) + len(missing_files)) * 100:.1f}%")

        if missing_files:
            print("\nMissing files (first 10):")
            for case_id, file_path in missing_files[:10]:
                print(f"  ❌ {case_id}: {file_path}")

        return {
            "missing_files": missing_files,
            "existing_files": existing_files,
            "existence_rate": (
                len(existing_files) / (len(existing_files) + len(missing_files))
                if (existing_files or missing_files)
                else 0
            ),
        }
    def _analyze_query_quality(self) -> dict[str, Any]:
        """Analyze query quality issues."""
        print("\n❓ Query Quality Analysis")
        print("-" * 40)

        issues = {
            "too_short": [],
            "too_long": [],
            "unclear_questions": [],
            "file_specific_questions": [],
            "generic_questions": [],
            "duplicate_queries": [],
        }

        query_lengths = []
        query_patterns = defaultdict(int)

        for case in self.cases:
            query = case.query.strip()
            query_lengths.append(len(query))

            # Check query length
            if len(query) < 10:
                issues["too_short"].append(case.id)
            elif len(query) > 200:
                issues["too_long"].append(case.id)

            # Check for unclear questions
            if not query.endswith("?"):
                issues["unclear_questions"].append(case.id)

            # Check for file-specific questions
            if any(pattern in query.lower() for pattern in [".md", ".py", ".json", "according to"]):
                issues["file_specific_questions"].append(case.id)

            # Check for generic questions
            generic_patterns = [r"^what is\s+\w+\?$", r"^how do\s+\w+\?$", r"^where are\s+\w+\?$", r"^which\s+\w+\?$"]
            if any(re.match(pattern, query.lower()) for pattern in generic_patterns):
                issues["generic_questions"].append(case.id)

            # Track query patterns
            query_patterns[query] += 1

        # Find duplicate queries
        for query, count in query_patterns.items():
            if count > 1:
                issues["duplicate_queries"].append(f"'{query}' appears {count} times")

        avg_length = sum(query_lengths) / len(query_lengths) if query_lengths else 0
        print(f"Average query length: {avg_length:.1f} characters")
        print(f"Too short queries: {len(issues['too_short'])}")
        print(f"Too long queries: {len(issues['too_long'])}")
        print(f"Unclear questions: {len(issues['unclear_questions'])}")
        print(f"File-specific questions: {len(issues['file_specific_questions'])}")
        print(f"Duplicate queries: {len(issues['duplicate_queries'])}")
        return {
            "query_lengths": query_lengths,
            "avg_length": avg_length,
            "issues": issues,
        }
    def _analyze_answer_quality(self) -> dict[str, Any]:
        """Analyze answer quality for reader mode cases."""
        print("\n💬 Answer Quality Analysis")
        print("-" * 40)

        reader_cases = [case for case in self.cases if case.mode == Mode.reader]

        issues = {
            "missing_answers": [],
            "too_short_answers": [],
            "too_long_answers": [],
            "incomplete_answers": [],
            "unclear_answers": [],
        }

        answer_lengths = []

        for case in reader_cases:
            if not case.gt_answer:
                issues["missing_answers"].append(case.id)
                continue

            answer = case.gt_answer.strip()
            answer_lengths.append(len(answer))

            # Check answer length
            if len(answer) < 20:
                issues["too_short"].append(case.id)
            elif len(answer) > 500:
                issues["too_long"].append(case.id)

            # Check for incomplete answers
            if answer.endswith("...") or "TODO" in answer or "FIXME" in answer:
                issues["incomplete"].append(case.id)

            # Check for unclear answers
            if answer.lower() in ["not in context.", "not found.", "unknown.", "n/a"]:
                issues["unclear"].append(case.id)

        avg_answer_length = sum(answer_lengths) / len(answer_lengths) if answer_lengths else 0

        print(f"Reader mode cases: {len(reader_cases)}")
        print(f"Average answer length: {avg_answer_length:.1f} characters")
        print(f"Missing answers: {len(issues['missing'])}")
        print(f"Too short answers: {len(issues['too_short'])}")
        print(f"Too long answers: {len(issues['too_long'])}")
        print(f"Incomplete answers: {len(issues['incomplete'])}")
        print(f"Unclear answers: {len(issues['unclear'])}")

        return {
            "reader_cases": len(reader_cases),
            "answer_lengths": answer_lengths,
            "avg_answer_length": avg_answer_length,
            "issues": issues,
        }

    def _analyze_coverage(self) -> dict[str, Any]:
        """Analyze coverage of different aspects."""
        print("\n📊 Coverage Analysis")
        print("-" * 40)

        coverage = {
            "mode_coverage": Counter(case.mode for case in self.cases),
            "tag_coverage": Counter(tag for case in self.cases for tag in case.tags),
            "file_coverage": set(),
            "directory_coverage": set(),
        }

        # Analyze file coverage
        for case in self.cases:
            if case.expected_files:
                for file_path in case.expected_files:
                    coverage["file_coverage"].add(file_path)
                    if "/" in file_path:
                        coverage["directory_coverage"].add(file_path.rsplit("/", 1)[0])

        print(f"Mode coverage: {dict(coverage['mode_coverage'])}")
        print(f"Unique files covered: {len(coverage['file_coverage'])}")
        print(f"Directories covered: {sorted(coverage['directory_coverage'])}")
        print(f"Tag distribution: {dict(coverage['tag_coverage'])}")

        return coverage
    def _analyze_duplicates(self) -> dict[str, Any]:
        """Analyze duplicate cases."""
        print("\n🔄 Duplicate Analysis")
        print("-" * 40)

        duplicates = {"duplicate_ids": [], "duplicate_queries": [], "duplicate_answers": []}

        # Check for duplicate IDs
        seen_ids = set()
        for case in self.cases:
            if case.id in seen_ids:
                duplicates["duplicate_ids"].append(case.id)
            seen_ids.add(case.id)

        # Check for duplicate queries
        query_counts = Counter(case.query for case in self.cases)
        for query, count in query_counts.items():
            if count > 1:
                duplicates["duplicate_queries"].append(query)

        # Check for duplicate answers (reader mode)
        reader_cases = [case for case in self.cases if case.mode == Mode.reader and case.gt_answer]
        answer_counts = Counter(case.gt_answer for case in reader_cases)
        for answer, count in answer_counts.items():
            if count > 1:
                duplicates["duplicate_answers"].append(answer)

        print(f"Duplicate IDs: {len(duplicates['duplicate_ids'])}")
        print(f"Duplicate queries: {len(duplicates['duplicate_queries'])}")
        print(f"Duplicate answers: {len(duplicates['duplicate_answers'])}")

        return duplicates
    def _analyze_mode_consistency(self) -> dict[str, Any]:
        """Analyze mode consistency issues."""
        print("\n🎯 Mode Consistency Analysis")
        print("-" * 40)

        issues = {
            "retrieval_without_files": [],
            "reader_without_answers": [],
            "decision_without_decisions": [],
            "inconsistent_supervision": [],
        }

        for case in self.cases:
            if case.mode == Mode.retrieval:
                if not case.expected_files and not case.globs:
                    issues["retrieval_without_files"].append(case.id)
            elif case.mode == Mode.reader:
                if not case.gt_answer:
                    issues["reader_without_answers"].append(case.id)
            elif case.mode == Mode.decision:
                if not case.expected_decisions:
                    issues["decision_without_decisions"].append(case.id)

        print(f"Retrieval without files: {len(issues['retrieval_without_files'])}")
        print(f"Reader without answers: {len(issues['reader_without_answers'])}")
        print(f"Decision without decisions: {len(issues['decision_without_decisions'])}")

        return issues
    def _analyze_tags(self) -> dict[str, Any]:
        """Analyze tag usage and consistency."""
        print("\n🏷️ Tag Analysis")
        print("-" * 40)

        tag_analysis = {
            "tag_frequency": Counter(tag for case in self.cases for tag in case.tags),
            "cases_per_tag": defaultdict(list),
            "tag_consistency": defaultdict(set),
            "unknown_tags": [],
        }

        # Known tags from validation
        known_tags = {
            "ops_health",
            "meta_ops",
            "rag_qa_single",
            "rag_qa_multi",
            "db_workflows",
            "negatives",
            "gates",
            "promotion",
            "quality",
            "negative",
            "mars",
            "api-key",
            "shell",
            "integration",
            "setup",
            "db",
            "migration",
            "resilience",
            "rrf",
            "fusion",
            "ranking",
            "chunking",
            "embeddings",
            "configuration",
            "reranker",
            "cross-encoder",
            "ragchecker",
            "metrics",
            "baseline",
            "ann",
            "blocking",
            "canary",
            "citations",
            "context",
            "cosine",
            "dependencies",
            "deployment",
            "documentation",
            "dspy",
            "evaluation",
            "evals",
            "memory",
            "prd",
            "workflow",
            "vector",
            "index",
            "ivfflat",
            "fts",
            "tsquery",
            "postgresql",
            "pgvector",
            "teleprompter",
            "optimization",
            "grounding",
            "multi-hop",
            "hyde",
            "prf",
            "provenance",
            "tracking",
            "leakage",
            "runbook",
            "manifests",
            "quantum",
            "entanglement",
            "time-travel",
            "percentage",
            "entanglement",
        }

        for case in self.cases:
            for tag in case.tags:
                tag_analysis["cases_per_tag"][tag].append(case.id)
                tag_analysis["tag_consistency"][tag].add(case.mode)

                if tag not in known_tags:
                    tag_analysis["unknown_tags"].append(tag)

        print(f"Total unique tags: {len(tag_analysis['tag_frequency'])}")
        print(f"Unknown tags: {len(set(tag_analysis['unknown_tags']))}")
        print(f"Most common tags: {dict(tag_analysis['tag_frequency'].most_common(10))}")

        if tag_analysis["unknown_tags"]:
            print(f"Unknown tags: {sorted(set(tag_analysis['unknown_tags']))}")

        return tag_analysis
    def _analyze_hypothesis_violations(self) -> dict[str, Any]:
        """Analyze violations of testing hypotheses."""
        print("\n🚨 Hypothesis Violations Analysis")
        print("-" * 40)

        violations = {
            "invalid_test_cases": [],
            "poor_quality_queries": [],
            "missing_supervision": [],
            "inconsistent_metadata": [],
            "coverage_gaps": [],
        }

        # Check for invalid test cases
        for case in self.cases:
            if not case.id or not case.query or not case.tags:
                violations["invalid_test_cases"].append(case.id)

            # Check for poor quality queries
            if len(case.query) < 10 or not case.query.endswith("?"):
                violations["poor_quality_queries"].append(case.id)

            # Check for missing supervision
            if case.mode == Mode.reader and not case.gt_answer:
                violations["missing_supervision"].append(case.id)
            elif case.mode == Mode.retrieval and not case.expected_files and not case.globs:
                violations["missing_supervision"].append(case.id)
            elif case.mode == Mode.decision and not case.expected_decisions:
                violations["missing_supervision"].append(case.id)

        print(f"Invalid test cases: {len(violations['invalid_test_cases'])}")
        print(f"Poor quality queries: {len(violations['poor_quality_queries'])}")
        print(f"Missing supervision: {len(violations['missing_supervision'])}")

        return violations
    def generate_report(self) -> str:
        """Generate a comprehensive analysis report."""
        report = []
        report.append("# Gold Test Case Hypothesis Analysis Report")
        report.append("=" * 60)
        report.append("")

        # Executive Summary
        report.append("## Executive Summary")
        report.append("")
        total_cases = len(self.cases)
        schema_issues = len(self.analysis_results.get("schema_validation", {}).get("validation_errors", []))
        file_issues = len(self.analysis_results.get("file_existence", {}).get("missing_files", []))
        query_issues = len(self.analysis_results.get("query_quality", {}).get("issues", {}).get("too_short", [])) + \
                      len(self.analysis_results.get("query_quality", {}).get("issues", {}).get("unclear", []))

        report.append(f"- **Total Cases**: {total_cases}")
        report.append(f"- **Schema Issues**: {schema_issues}")
        report.append(f"- **Missing Files**: {file_issues}")
        report.append(f"- **Query Quality Issues**: {query_issues}")
        report.append("")

        # Key Findings
        report.append("## Key Findings")
        report.append("")

        if schema_issues > 0:
            report.append(f"❌ **Critical**: {schema_issues} cases have schema validation issues")

        if file_issues > 0:
            report.append(f"⚠️ **Warning**: {file_issues} expected files are missing")

        if query_issues > 0:
            report.append(f"⚠️ **Warning**: {query_issues} queries have quality issues")

        # Recommendations
        report.append("")
        report.append("## Recommendations")
        report.append("")
        report.append("1. **Fix Schema Issues**: Address mode requirement violations")
        report.append("2. **Update File References**: Fix missing file paths")
        report.append("3. **Improve Query Quality**: Rewrite unclear or too-short queries")
        report.append("4. **Add Missing Supervision**: Ensure all modes have proper supervision")
        report.append("5. **Validate Tag Consistency**: Review and standardize tag usage")

        return "\n".join(report)

def main():
    """Main function to run the analysis."""
    analyzer = GoldCaseHypothesisAnalysis()
    results = analyzer.run_analysis()

    print("\n" + "=" * 80)
    print("📋 ANALYSIS COMPLETE")
    print("=" * 80)

    # Generate and save report
    report = analyzer.generate_report()

    # Save report to file
    report_file = "metrics/gold_case_analysis_report.md"
    Path("metrics").mkdir(exist_ok=True)
    with open(report_file, "w") as f:
        f.write(report)

    print(f"\n📄 Report saved to: {report_file}")

    # Print summary
    print("\n🎯 SUMMARY:")
    print(f"Total cases analyzed: {len(analyzer.cases)}")
    print(f"Schema violations: {len(analyzer.analysis_results.get('schema_validation', {}).get('validation_errors', []))}")
    print(f"Missing files: {len(analyzer.analysis_results.get('file_existence', {}).get('missing_files', []))}")
    print(f"Query quality issues: {len(analyzer.analysis_results.get('query_quality', {}).get('issues', {}).get('too_short', [])) + len(analyzer.analysis_results.get('query_quality', {}).get('issues', {}).get('unclear', []))}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
