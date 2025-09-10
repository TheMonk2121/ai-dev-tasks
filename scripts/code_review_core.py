#!/usr/bin/env python3
"""
Code Review Core Implementation

Core functionality for the Code Review Process Upgrade with Performance Reporting.
Implements the formalized code review workflow with integrated performance monitoring.
"""

import json
import logging
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CodeReviewMetrics:
    """Performance metrics for code review process."""

    review_id: str
    start_time: datetime
    end_time: datetime | None = None
    files_reviewed: int = 0
    lines_reviewed: int = 0
    issues_found: int = 0
    critical_issues: int = 0
    review_duration_seconds: float = 0.0
    performance_score: float = 0.0
    quality_score: float = 0.0


@dataclass
class CodeReviewIssue:
    """Code review issue record."""

    issue_id: str
    severity: str  # critical, high, medium, low
    category: str  # security, performance, maintainability, style
    file_path: str
    line_number: int
    description: str
    suggestion: str
    status: str = "open"  # open, resolved, ignored


class CodeReviewCore:
    """Core code review process implementation."""

    def __init__(self, project_root: str | None = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.reviews_dir = self.project_root / ".cache" / "code_reviews"
        self.reviews_dir.mkdir(parents=True, exist_ok=True)
        self.current_review: CodeReviewMetrics | None = None
        self.issues: list[CodeReviewIssue] = []

        # Performance monitoring
        self.performance_monitor = None
        try:
            from scripts.workflow_performance_monitor import WorkflowPerformanceMonitor

            self.performance_monitor = WorkflowPerformanceMonitor()
        except ImportError:
            logger.warning("Performance monitoring not available")

    def start_review(self, review_id: str, target_paths: list[str] | None = None) -> CodeReviewMetrics:
        """Start a new code review session."""
        logger.info(f"🔍 Starting code review: {review_id}")

        self.current_review = CodeReviewMetrics(review_id=review_id, start_time=datetime.now())

        # Initialize performance monitoring
        if self.performance_monitor:
            self.performance_monitor.measure_workflow_component(
                "code_review_start", self._start_review_internal, review_id, target_paths
            )
        else:
            self._start_review_internal(review_id, target_paths)

        return self.current_review

    def _start_review_internal(self, review_id: str, target_paths: list[str] | None = None):
        """Internal review start implementation."""
        if target_paths is None:
            target_paths = ["scripts/", "dspy-rag-system/src/"]

        # Analyze target files
        files_to_review = self._get_files_to_review(target_paths)
        self.current_review.files_reviewed = len(files_to_review)
        self.current_review.lines_reviewed = sum(self._count_lines(f) for f in files_to_review)

        logger.info(f"📁 Reviewing {len(files_to_review)} files ({self.current_review.lines_reviewed} lines)")

    def _get_files_to_review(self, target_paths: list[str]) -> list[Path]:
        """Get list of files to review."""
        files = []
        for path in target_paths:
            target = self.project_root / path
            if target.is_file():
                files.append(target)
            elif target.is_dir():
                for file_path in target.rglob("*.py"):
                    if not any(part.startswith(".") for part in file_path.parts):
                        files.append(file_path)
        return files

    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                return len(f.readlines())
        except Exception as e:
            logger.warning(f"Could not count lines in {file_path}: {e}")
            return 0

    def run_security_analysis(self) -> list[CodeReviewIssue]:
        """Run security analysis on the codebase."""
        logger.info("🔒 Running security analysis...")

        issues = []

        # Run security tools
        security_issues = self._run_security_tools()
        issues.extend(security_issues)

        # Run custom security checks
        custom_issues = self._run_custom_security_checks()
        issues.extend(custom_issues)

        self.issues.extend(issues)
        self.current_review.issues_found += len(issues)
        self.current_review.critical_issues += len([i for i in issues if i.severity == "critical"])

        return issues

    def _run_security_tools(self) -> list[CodeReviewIssue]:
        """Run external security analysis tools."""
        issues = []

        try:
            # Run bandit security analysis
            result = subprocess.run(
                [sys.executable, "-m", "bandit", "-r", "scripts/", "-f", "json"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode in [0, 1]:  # Bandit returns 1 for issues found
                try:
                    bandit_data = json.loads(result.stdout)
                    for issue in bandit_data.get("results", []):
                        review_issue = CodeReviewIssue(
                            issue_id=f"bandit_{issue.get('test_id', 'unknown')}",
                            severity=issue.get("issue_severity", "medium"),
                            category="security",
                            file_path=issue.get("filename", "unknown"),
                            line_number=issue.get("line_number", 0),
                            description=issue.get("issue_text", "Security issue detected"),
                            suggestion=issue.get("more_info", "Review and fix security issue"),
                        )
                        issues.append(review_issue)
                except json.JSONDecodeError:
                    logger.warning("Could not parse bandit output")

        except Exception as e:
            logger.error(f"Security tools analysis failed: {e}")

        return issues

    def _run_custom_security_checks(self) -> list[CodeReviewIssue]:
        """Run custom security validation checks."""
        issues = []

        try:
            # Import enhanced security validation
            sys.path.insert(0, str(self.project_root))

            # Test critical files for security issues
            critical_files = [
                "scripts/single_doorway.py",
                "scripts/process_tasks.py",
                "dspy-rag-system/src/dspy_modules/cursor_model_router.py",
            ]

            for file_path in critical_files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    try:
                        content = full_path.read_text()

                        # Check for potential security issues
                        if "eval(" in content or "exec(" in content:
                            issues.append(
                                CodeReviewIssue(
                                    issue_id=f"custom_eval_{file_path}",
                                    severity="high",
                                    category="security",
                                    file_path=str(file_path),
                                    line_number=0,
                                    description="Potential code execution vulnerability",
                                    suggestion="Replace eval/exec with safer alternatives",
                                )
                            )

                        if "password" in content.lower() and "hardcoded" in content.lower():
                            issues.append(
                                CodeReviewIssue(
                                    issue_id=f"custom_password_{file_path}",
                                    severity="critical",
                                    category="security",
                                    file_path=str(file_path),
                                    line_number=0,
                                    description="Potential hardcoded credentials",
                                    suggestion="Use environment variables or secure credential management",
                                )
                            )

                    except Exception as e:
                        logger.warning(f"Could not analyze {file_path}: {e}")

        except Exception as e:
            logger.error(f"Custom security checks failed: {e}")

        return issues

    def run_performance_analysis(self) -> list[CodeReviewIssue]:
        """Run performance analysis on the codebase."""
        logger.info("⚡ Running performance analysis...")

        issues = []

        # Analyze performance patterns
        performance_issues = self._analyze_performance_patterns()
        issues.extend(performance_issues)

        # Run performance benchmarks
        benchmark_issues = self._run_performance_benchmarks()
        issues.extend(benchmark_issues)

        self.issues.extend(issues)
        self.current_review.issues_found += len(issues)

        return issues

    def _analyze_performance_patterns(self) -> list[CodeReviewIssue]:
        """Analyze code for performance anti-patterns."""
        issues = []

        try:
            # Check for common performance issues
            performance_patterns = [
                (
                    r"for.*in.*for.*in",
                    "Nested loops detected",
                    "Consider using list comprehensions or vectorized operations",
                ),
                (r"\.append\(.*\)", "List append in loops", "Consider list comprehensions or pre-allocated lists"),
                (r"import \*", "Wildcard imports", "Use specific imports to improve performance"),
                (r"time\.sleep\(", "Blocking sleep calls", "Consider async/await or non-blocking alternatives"),
            ]

            import re

            for pattern, description, suggestion in performance_patterns:
                for file_path in self.project_root.rglob("*.py"):
                    if not any(part.startswith(".") for part in file_path.parts):
                        try:
                            content = file_path.read_text()
                            matches = re.finditer(pattern, content, re.MULTILINE)
                            for match in matches:
                                line_number = content[: match.start()].count("\n") + 1
                                issues.append(
                                    CodeReviewIssue(
                                        issue_id=f"perf_{pattern}_{file_path.name}",
                                        severity="medium",
                                        category="performance",
                                        file_path=str(file_path.relative_to(self.project_root)),
                                        line_number=line_number,
                                        description=description,
                                        suggestion=suggestion,
                                    )
                                )
                        except Exception as e:
                            logger.warning(f"Could not analyze {file_path}: {e}")

        except Exception as e:
            logger.error(f"Performance pattern analysis failed: {e}")

        return issues

    def _run_performance_benchmarks(self) -> list[CodeReviewIssue]:
        """Run performance benchmarks on critical components."""
        issues = []

        try:
            # Run performance benchmark
            result = subprocess.run(
                [sys.executable, "scripts/performance_benchmark.py", "--script", "single_doorway", "--iterations", "3"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode == 0:
                # Parse benchmark results
                if "Avg time:" in result.stdout:
                    # Extract timing information
                    lines = result.stdout.split("\n")
                    for line in lines:
                        if "Avg time:" in line:
                            time_str = line.split("Avg time:")[1].split()[0]
                            try:
                                avg_time = float(time_str.replace("s", ""))
                                if avg_time > 1.0:  # Threshold for performance issues
                                    issues.append(
                                        CodeReviewIssue(
                                            issue_id="perf_benchmark_slow",
                                            severity="medium",
                                            category="performance",
                                            file_path="scripts/single_doorway.py",
                                            line_number=0,
                                            description=f"Slow performance detected: {avg_time}s average",
                                            suggestion="Optimize workflow execution time",
                                        )
                                    )
                            except ValueError:
                                pass

        except Exception as e:
            logger.error(f"Performance benchmark failed: {e}")

        return issues

    def run_code_quality_analysis(self) -> list[CodeReviewIssue]:
        """Run code quality analysis."""
        logger.info("📊 Running code quality analysis...")

        issues = []

        # Run linting checks
        linting_issues = self._run_linting_checks()
        issues.extend(linting_issues)

        # Run complexity analysis
        complexity_issues = self._analyze_code_complexity()
        issues.extend(complexity_issues)

        # Run documentation checks
        doc_issues = self._check_documentation_quality()
        issues.extend(doc_issues)

        self.issues.extend(issues)
        self.current_review.issues_found += len(issues)

        return issues

    def _run_linting_checks(self) -> list[CodeReviewIssue]:
        """Run code linting checks."""
        issues = []

        try:
            # Run ruff linting
            result = subprocess.run(
                [sys.executable, "-m", "ruff", "check", "scripts/", "--output-format", "json"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode in [0, 1]:  # Ruff returns 1 for issues found
                try:
                    ruff_data = json.loads(result.stdout)
                    for issue in ruff_data:
                        review_issue = CodeReviewIssue(
                            issue_id=f"ruff_{issue.get('code', 'unknown')}",
                            severity="low",
                            category="style",
                            file_path=issue.get("filename", "unknown"),
                            line_number=issue.get("location", {}).get("row", 0),
                            description=f"Linting issue: {issue.get('message', 'Code style issue')}",
                            suggestion="Fix code style according to project standards",
                        )
                        issues.append(review_issue)
                except json.JSONDecodeError:
                    logger.warning("Could not parse ruff output")

        except Exception as e:
            logger.error(f"Linting checks failed: {e}")

        return issues

    def _analyze_code_complexity(self) -> list[CodeReviewIssue]:
        """Analyze code complexity."""
        issues = []

        try:
            # Run radon complexity analysis
            result = subprocess.run(
                [sys.executable, "-m", "radon", "cc", "scripts/", "-j"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode == 0:
                try:
                    radon_data = json.loads(result.stdout)
                    for file_path, functions in radon_data.items():
                        for func_name, complexity in functions.items():
                            if complexity > 10:  # High complexity threshold
                                issues.append(
                                    CodeReviewIssue(
                                        issue_id=f"complexity_{file_path}_{func_name}",
                                        severity="medium",
                                        category="maintainability",
                                        file_path=file_path,
                                        line_number=0,
                                        description=f"High complexity function: {func_name} (complexity: {complexity})",
                                        suggestion="Refactor function to reduce complexity",
                                    )
                                )
                except json.JSONDecodeError:
                    logger.warning("Could not parse radon output")

        except Exception as e:
            logger.error(f"Complexity analysis failed: {e}")

        return issues

    def _check_documentation_quality(self) -> list[CodeReviewIssue]:
        """Check documentation quality."""
        issues = []

        try:
            # Check for missing docstrings in critical files
            critical_files = [
                "scripts/single_doorway.py",
                "scripts/process_tasks.py",
                "scripts/task_generation_automation.py",
            ]

            for file_path in critical_files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    content = full_path.read_text()

                    # Check for module docstring
                    if not content.strip().startswith('"""') and not content.strip().startswith("'''"):
                        issues.append(
                            CodeReviewIssue(
                                issue_id=f"doc_missing_{file_path}",
                                severity="low",
                                category="documentation",
                                file_path=str(file_path),
                                line_number=1,
                                description="Missing module docstring",
                                suggestion="Add comprehensive module documentation",
                            )
                        )

                    # Check for function docstrings
                    import re

                    function_pattern = r"def\s+(\w+)\s*\("
                    functions = re.findall(function_pattern, content)

                    for func_name in functions:
                        # Simple check for docstring after function definition
                        func_pattern = rf"def\s+{func_name}\s*\([^)]*\):"
                        if re.search(func_pattern, content):
                            # Check if there's a docstring in the next few lines
                            lines = content.split("\n")
                            for i, line in enumerate(lines):
                                if f"def {func_name}(" in line:
                                    # Look for docstring in next 3 lines
                                    has_docstring = False
                                    for j in range(i + 1, min(i + 4, len(lines))):
                                        if '"""' in lines[j] or "'''" in lines[j]:
                                            has_docstring = True
                                            break

                                    if not has_docstring:
                                        issues.append(
                                            CodeReviewIssue(
                                                issue_id=f"doc_func_{file_path}_{func_name}",
                                                severity="low",
                                                category="documentation",
                                                file_path=str(file_path),
                                                line_number=i + 1,
                                                description=f"Missing docstring for function: {func_name}",
                                                suggestion="Add function documentation",
                                            )
                                        )
                                    break

        except Exception as e:
            logger.error(f"Documentation quality check failed: {e}")

        return issues

    def complete_review(self) -> dict[str, Any]:
        """Complete the code review and generate report."""
        if not self.current_review:
            raise ValueError("No active review to complete")

        logger.info(f"✅ Completing code review: {self.current_review.review_id}")

        # Calculate final metrics
        self.current_review.end_time = datetime.now()
        self.current_review.review_duration_seconds = (
            self.current_review.end_time - self.current_review.start_time
        ).total_seconds()

        # Calculate scores
        self.current_review.performance_score = self._calculate_performance_score()
        self.current_review.quality_score = self._calculate_quality_score()

        # Generate report
        report = self._generate_review_report()

        # Save review data
        self._save_review_data()

        return report

    def _calculate_performance_score(self) -> float:
        """Calculate performance score (0-100)."""
        if not self.current_review:
            return 0.0

        # Base score
        score = 100.0

        # Penalize for long review duration
        if self.current_review.review_duration_seconds > 300:  # 5 minutes
            score -= 20

        # Penalize for critical issues
        score -= self.current_review.critical_issues * 10

        # Penalize for high severity issues
        high_issues = len([i for i in self.issues if i.severity == "high"])
        score -= high_issues * 5

        return max(0.0, score)

    def _calculate_quality_score(self) -> float:
        """Calculate quality score (0-100)."""
        if not self.current_review or self.current_review.files_reviewed == 0:
            return 0.0

        # Base score
        score = 100.0

        # Penalize for issues per file
        issues_per_file = self.current_review.issues_found / self.current_review.files_reviewed
        score -= issues_per_file * 10

        # Bonus for good documentation
        doc_issues = len([i for i in self.issues if i.category == "documentation"])
        if doc_issues == 0:
            score += 10

        return max(0.0, min(100.0, score))

    def _generate_review_report(self) -> dict[str, Any]:
        """Generate comprehensive review report."""
        if not self.current_review:
            return {}

        # Group issues by category and severity
        issues_by_category = {}
        issues_by_severity = {}

        for issue in self.issues:
            # By category
            if issue.category not in issues_by_category:
                issues_by_category[issue.category] = []
            issues_by_category[issue.category].append(issue)

            # By severity
            if issue.severity not in issues_by_severity:
                issues_by_severity[issue.severity] = []
            issues_by_severity[issue.severity].append(issue)

        report = {
            "review_id": self.current_review.review_id,
            "timestamp": self.current_review.end_time.isoformat(),
            "duration_seconds": self.current_review.review_duration_seconds,
            "metrics": asdict(self.current_review),
            "summary": {
                "total_issues": self.current_review.issues_found,
                "critical_issues": self.current_review.critical_issues,
                "performance_score": self.current_review.performance_score,
                "quality_score": self.current_review.quality_score,
                "overall_score": (self.current_review.performance_score + self.current_review.quality_score) / 2,
            },
            "issues_by_category": {
                category: [asdict(issue) for issue in issues] for category, issues in issues_by_category.items()
            },
            "issues_by_severity": {
                severity: [asdict(issue) for issue in issues] for severity, issues in issues_by_severity.items()
            },
            "recommendations": self._generate_recommendations(),
        }

        return report

    def _generate_recommendations(self) -> list[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Performance recommendations
        if self.current_review.performance_score < 80:
            recommendations.append("Optimize code performance - focus on critical path execution")

        # Quality recommendations
        if self.current_review.quality_score < 80:
            recommendations.append("Improve code quality - address documentation and style issues")

        # Security recommendations
        critical_security = len([i for i in self.issues if i.category == "security" and i.severity == "critical"])
        if critical_security > 0:
            recommendations.append(f"Address {critical_security} critical security issues immediately")

        # Documentation recommendations
        doc_issues = len([i for i in self.issues if i.category == "documentation"])
        if doc_issues > 5:
            recommendations.append("Improve code documentation - add missing docstrings and comments")

        return recommendations

    def _save_review_data(self):
        """Save review data to persistent storage."""
        if not self.current_review:
            return

        try:
            # Save review metrics
            metrics_file = self.reviews_dir / f"{self.current_review.review_id}_metrics.json"
            with open(metrics_file, "w") as f:
                json.dump(asdict(self.current_review), f, indent=2)

            # Save issues
            issues_file = self.reviews_dir / f"{self.current_review.review_id}_issues.json"
            with open(issues_file, "w") as f:
                json.dump([asdict(issue) for issue in self.issues], f, indent=2)

            logger.info(f"📁 Review data saved to {self.reviews_dir}")

        except Exception as e:
            logger.error(f"Failed to save review data: {e}")

    def print_review_summary(self, report: dict[str, Any]):
        """Print a formatted review summary."""
        if not report:
            return

        summary = report.get("summary", {})
        metrics = report.get("metrics", {})

        print(f"\n🔍 **Code Review Summary: {report.get('review_id', 'Unknown')}**")
        print(f"📅 Completed: {report.get('timestamp', 'Unknown')}")
        print(f"⏱️ Duration: {metrics.get('review_duration_seconds', 0):.1f}s")
        print(f"📁 Files: {metrics.get('files_reviewed', 0)}")
        print(f"📝 Lines: {metrics.get('lines_reviewed', 0)}")

        print("\n📊 **Issues Found:**")
        print(f"   Total: {summary.get('total_issues', 0)}")
        print(f"   Critical: {summary.get('critical_issues', 0)}")

        print("\n🎯 **Scores:**")
        print(f"   Performance: {summary.get('performance_score', 0):.1f}/100")
        print(f"   Quality: {summary.get('quality_score', 0):.1f}/100")
        print(f"   Overall: {summary.get('overall_score', 0):.1f}/100")

        # Show recommendations
        recommendations = report.get("recommendations", [])
        if recommendations:
            print("\n💡 **Recommendations:**")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")


def main():
    """Main function for code review core."""
    import argparse

    parser = argparse.ArgumentParser(description="Code Review Core Implementation")
    parser.add_argument("--review-id", required=True, help="Review ID")
    parser.add_argument("--targets", nargs="+", default=["scripts/"], help="Target paths to review")
    parser.add_argument("--output", help="Output file for report")

    args = parser.parse_args()

    # Initialize code review core
    core = CodeReviewCore()

    try:
        # Start review
        core.start_review(args.review_id, args.targets)

        # Run analyses
        core.run_security_analysis()
        core.run_performance_analysis()
        core.run_code_quality_analysis()

        # Complete review
        report = core.complete_review()

        # Print summary
        core.print_review_summary(report)

        # Save report if requested
        if args.output:
            with open(args.output, "w") as f:
                json.dump(report, f, indent=2)
            print(f"\n📄 Report saved to: {args.output}")

        # Return appropriate exit code
        if report.get("summary", {}).get("critical_issues", 0) > 0:
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        logger.error(f"Code review failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
