#!/usr/bin/env python3
"""
Baseline Metrics Establishment for B-1032

Establishes baseline metrics for all guides, including size analysis, cross-reference mapping,
and quality scoring. Part of the t-t3 Authority Structure Implementation.
"""

import argparse
import hashlib
import json
import re
import sqlite3
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects and other non-serializable types."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, tuple):
            return list(obj)
        elif hasattr(obj, "__dict__"):
            return obj.__dict__
        return super().default(obj)


@dataclass
class BaselineMetrics:
    """Baseline metrics for a single guide."""

    file_path: str
    file_name: str
    size_bytes: int
    line_count: int
    word_count: int
    character_count: int
    last_modified: datetime
    days_since_modified: int
    content_hash: str
    cross_references: List[str]
    internal_links: List[str]
    external_links: List[str]
    headings: List[str]
    code_blocks: int
    images: int
    tables: int
    lists: int
    quality_score: float
    complexity_score: float
    readability_score: float
    authority_indicators: List[str]
    content_type: str
    estimated_reading_time: int  # minutes


@dataclass
class BaselineSummary:
    """Summary of baseline metrics for all guides."""

    total_guides: int
    total_lines: int
    total_words: int
    total_size_mb: float
    average_quality_score: float
    average_complexity_score: float
    average_readability_score: float
    size_distribution: Dict[str, List[str]]
    quality_distribution: Dict[str, List[str]]
    content_type_distribution: Dict[str, int]
    cross_reference_network: Dict[str, List[str]]
    authority_hierarchy: Dict[str, List[str]]
    baseline_timestamp: datetime
    baseline_duration_seconds: float


class BaselineMetricsEstablisher:
    """Main class for establishing baseline metrics."""

    def __init__(self, guides_dir: str = "400_guides", output_dir: str = "artifacts/baseline"):
        self.guides_dir = Path(guides_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize database for baseline history
        self.db_path = self.output_dir / "baseline_history.db"
        self._init_database()

        # Analysis patterns
        self.authority_indicators = [
            "authoritative",
            "primary",
            "main",
            "core",
            "essential",
            "critical",
            "definitive",
            "comprehensive",
            "complete",
            "master",
            "reference",
        ]

        self.content_type_patterns = {
            "workflow": ["workflow", "process", "procedure", "step-by-step"],
            "guide": ["guide", "how-to", "tutorial", "walkthrough"],
            "reference": ["reference", "api", "schema", "specification"],
            "best_practice": ["best practice", "guideline", "recommendation", "standard"],
            "troubleshooting": ["troubleshoot", "debug", "error", "fix", "issue"],
            "overview": ["overview", "introduction", "summary", "overview"],
        }

    def _init_database(self):
        """Initialize SQLite database for baseline history."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS baseline_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total_guides INTEGER,
                    total_lines INTEGER,
                    total_words INTEGER,
                    average_quality_score REAL,
                    baseline_duration REAL,
                    results_json TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS guide_baselines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER,
                    file_path TEXT,
                    file_name TEXT,
                    size_bytes INTEGER,
                    line_count INTEGER,
                    word_count INTEGER,
                    quality_score REAL,
                    complexity_score REAL,
                    readability_score REAL,
                    content_type TEXT,
                    cross_references TEXT,
                    baseline_json TEXT,
                    FOREIGN KEY (run_id) REFERENCES baseline_runs (id)
                )
            """
            )

    def establish_baseline(self) -> BaselineSummary:
        """Establish baseline metrics for all guides."""
        start_time = time.time()

        print("📊 Starting baseline metrics establishment...")
        print(f"📁 Analyzing guides in: {self.guides_dir}")

        # Get all markdown files
        guide_files = list(self.guides_dir.glob("*.md"))
        print(f"📄 Found {len(guide_files)} guide files")

        # Analyze each guide
        baseline_metrics = []
        for file_path in guide_files:
            try:
                metrics = self._analyze_single_guide(file_path)
                baseline_metrics.append(metrics)
                print(f"✅ Analyzed: {file_path.name} (Quality: {metrics.quality_score:.2f})")
            except Exception as e:
                print(f"❌ Error analyzing {file_path.name}: {e}")

        # Generate baseline summary
        baseline_summary = self._generate_baseline_summary(baseline_metrics, start_time)

        # Store results in database
        self._store_baseline_results(baseline_summary, baseline_metrics)

        # Save to JSON
        self._save_baseline_results(baseline_summary, baseline_metrics)

        print(f"🎯 Baseline establishment complete in {baseline_summary.baseline_duration_seconds:.2f} seconds")
        print(f"📊 Results saved to: {self.output_dir}")

        return baseline_summary

    def _analyze_single_guide(self, file_path: Path) -> BaselineMetrics:
        """Analyze a single guide file for baseline metrics."""
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Basic metrics
        size_bytes = file_path.stat().st_size
        line_count = len(lines)
        word_count = len(content.split())
        character_count = len(content)

        # File metadata
        stat = file_path.stat()
        last_modified = datetime.fromtimestamp(stat.st_mtime)
        days_since_modified = (datetime.now() - last_modified).days

        # Content hash for change detection
        content_hash = hashlib.md5(content.encode()).hexdigest()

        # Extract cross-references and links
        cross_references = self._extract_cross_references(content)
        internal_links = self._extract_internal_links(content)
        external_links = self._extract_external_links(content)

        # Extract structural elements
        headings = self._extract_headings(content)
        code_blocks = content.count("```")
        images = content.count("![")
        tables = content.count("|")
        lists = content.count("- ") + content.count("1. ")

        # Calculate scores
        quality_score = self._calculate_quality_score(content, line_count, word_count, headings)
        complexity_score = self._calculate_complexity_score(content, line_count, word_count)
        readability_score = self._calculate_readability_score(content, line_count, word_count)

        # Authority indicators
        authority_indicators = self._identify_authority_indicators(content)

        # Content type
        content_type = self._determine_content_type(content, file_path.name)

        # Estimated reading time (average 200 words per minute)
        estimated_reading_time = max(1, word_count // 200)

        return BaselineMetrics(
            file_path=str(file_path),
            file_name=file_path.name,
            size_bytes=size_bytes,
            line_count=line_count,
            word_count=word_count,
            character_count=character_count,
            last_modified=last_modified,
            days_since_modified=days_since_modified,
            content_hash=content_hash,
            cross_references=cross_references,
            internal_links=internal_links,
            external_links=external_links,
            headings=headings,
            code_blocks=code_blocks,
            images=images,
            tables=tables,
            lists=lists,
            quality_score=quality_score,
            complexity_score=complexity_score,
            readability_score=readability_score,
            authority_indicators=authority_indicators,
            content_type=content_type,
            estimated_reading_time=estimated_reading_time,
        )

    def _extract_cross_references(self, content: str) -> List[str]:
        """Extract cross-references to other guides."""
        pattern = r"400_guides/[^)\s]+\.md"
        return re.findall(pattern, content)

    def _extract_internal_links(self, content: str) -> List[str]:
        """Extract internal links within the project."""
        pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        matches = re.findall(pattern, content)
        return [link for _, link in matches if not link.startswith("http")]

    def _extract_external_links(self, content: str) -> List[str]:
        """Extract external links."""
        pattern = r"\[([^\]]+)\]\((https?://[^)]+)\)"
        matches = re.findall(pattern, content)
        return [link for _, link in matches]

    def _extract_headings(self, content: str) -> List[str]:
        """Extract all headings from the content."""
        pattern = r"^#{1,6}\s+(.+)$"
        return re.findall(pattern, content, re.MULTILINE)

    def _calculate_quality_score(self, content: str, line_count: int, word_count: int, headings: List[str]) -> float:
        """Calculate quality score based on various factors."""
        score = 0.0

        # Structure quality (30%)
        if len(headings) >= 3:
            score += 0.3
        elif len(headings) >= 2:
            score += 0.2
        elif len(headings) >= 1:
            score += 0.1

        # Content quality (25%)
        if "TL;DR" in content:
            score += 0.25

        # Link quality (20%)
        internal_links = self._extract_internal_links(content)
        external_links = self._extract_external_links(content)
        if len(internal_links) > 0 or len(external_links) > 0:
            score += 0.2

        # Code quality (15%)
        code_blocks = content.count("```")
        if code_blocks > 0:
            score += 0.15

        # Metadata quality (10%)
        if "ANCHOR_KEY:" in content and "ROLE_PINS:" in content:
            score += 0.1

        return min(score, 1.0)

    def _calculate_complexity_score(self, content: str, line_count: int, word_count: int) -> float:
        """Calculate complexity score."""
        score = 0.0

        # Size complexity
        if line_count > 1000:
            score += 0.3
        elif line_count > 500:
            score += 0.2
        elif line_count > 200:
            score += 0.1

        # Content complexity
        complexity_indicators = ["advanced", "complex", "detailed", "comprehensive", "thorough"]
        complexity_matches = sum(1 for indicator in complexity_indicators if indicator.lower() in content.lower())
        score += min(complexity_matches * 0.1, 0.3)

        # Code complexity
        code_blocks = content.count("```")
        score += min(code_blocks * 0.05, 0.2)

        # Cross-reference complexity
        cross_refs = len(self._extract_cross_references(content))
        score += min(cross_refs * 0.02, 0.2)

        return min(score, 1.0)

    def _calculate_readability_score(self, content: str, line_count: int, word_count: int) -> float:
        """Calculate readability score."""
        score = 1.0

        # Penalize very long files
        if line_count > 2000:
            score -= 0.3
        elif line_count > 1000:
            score -= 0.2
        elif line_count > 500:
            score -= 0.1

        # Reward TL;DR sections
        if "TL;DR" in content:
            score += 0.1

        # Reward clear structure
        headings = self._extract_headings(content)
        if len(headings) >= 3:
            score += 0.1

        # Penalize very dense content
        if word_count > 0 and line_count > 0:
            words_per_line = word_count / line_count
            if words_per_line > 20:
                score -= 0.2
            elif words_per_line > 15:
                score -= 0.1

        return max(score, 0.0)

    def _identify_authority_indicators(self, content: str) -> List[str]:
        """Identify authority indicators in the content."""
        found_indicators = []
        content_lower = content.lower()

        for indicator in self.authority_indicators:
            if indicator in content_lower:
                found_indicators.append(indicator)

        return found_indicators

    def _determine_content_type(self, content: str, filename: str) -> str:
        """Determine the type of content in the guide."""
        content_lower = content.lower()

        for content_type, patterns in self.content_type_patterns.items():
            for pattern in patterns:
                if pattern in content_lower:
                    return content_type

        return "general"

    def _generate_baseline_summary(self, baseline_metrics: List[BaselineMetrics], start_time: float) -> BaselineSummary:
        """Generate baseline summary for all guides."""
        total_guides = len(baseline_metrics)
        total_lines = sum(m.line_count for m in baseline_metrics)
        total_words = sum(m.word_count for m in baseline_metrics)
        total_size_mb = sum(m.size_bytes for m in baseline_metrics) / (1024 * 1024)

        # Calculate averages
        avg_quality = sum(m.quality_score for m in baseline_metrics) / total_guides if total_guides > 0 else 0
        avg_complexity = sum(m.complexity_score for m in baseline_metrics) / total_guides if total_guides > 0 else 0
        avg_readability = sum(m.readability_score for m in baseline_metrics) / total_guides if total_guides > 0 else 0

        # Size distribution
        size_distribution = {
            "small": [m.file_name for m in baseline_metrics if m.line_count < 200],
            "medium": [m.file_name for m in baseline_metrics if 200 <= m.line_count < 500],
            "large": [m.file_name for m in baseline_metrics if 500 <= m.line_count < 1000],
            "very_large": [m.file_name for m in baseline_metrics if m.line_count >= 1000],
        }

        # Quality distribution
        quality_distribution = {
            "low": [m.file_name for m in baseline_metrics if m.quality_score < 0.5],
            "medium": [m.file_name for m in baseline_metrics if 0.5 <= m.quality_score < 0.8],
            "high": [m.file_name for m in baseline_metrics if m.quality_score >= 0.8],
        }

        # Content type distribution
        content_type_distribution = Counter()
        for metrics in baseline_metrics:
            content_type_distribution[metrics.content_type] += 1

        # Cross-reference network
        cross_reference_network = defaultdict(list)
        for metrics in baseline_metrics:
            for ref in metrics.cross_references:
                ref_name = Path(ref).name
                cross_reference_network[metrics.file_name].append(ref_name)

        # Authority hierarchy
        authority_hierarchy = defaultdict(list)
        for metrics in baseline_metrics:
            if metrics.authority_indicators:
                for indicator in metrics.authority_indicators:
                    authority_hierarchy[indicator].append(metrics.file_name)

        baseline_duration = time.time() - start_time

        return BaselineSummary(
            total_guides=total_guides,
            total_lines=total_lines,
            total_words=total_words,
            total_size_mb=total_size_mb,
            average_quality_score=avg_quality,
            average_complexity_score=avg_complexity,
            average_readability_score=avg_readability,
            size_distribution=size_distribution,
            quality_distribution=quality_distribution,
            content_type_distribution=dict(content_type_distribution),
            cross_reference_network=dict(cross_reference_network),
            authority_hierarchy=dict(authority_hierarchy),
            baseline_timestamp=datetime.now(),
            baseline_duration_seconds=baseline_duration,
        )

    def _store_baseline_results(self, baseline_summary: BaselineSummary, baseline_metrics: List[BaselineMetrics]):
        """Store baseline results in SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            # Store main baseline run
            cursor = conn.execute(
                """
                INSERT INTO baseline_runs
                (timestamp, total_guides, total_lines, total_words, average_quality_score, baseline_duration, results_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    baseline_summary.baseline_timestamp.isoformat(),
                    baseline_summary.total_guides,
                    baseline_summary.total_lines,
                    baseline_summary.total_words,
                    baseline_summary.average_quality_score,
                    baseline_summary.baseline_duration_seconds,
                    json.dumps(asdict(baseline_summary), cls=CustomJSONEncoder),
                ),
            )
            run_id = cursor.lastrowid

            # Store individual guide baselines
            for metrics in baseline_metrics:
                conn.execute(
                    """
                    INSERT INTO guide_baselines
                    (run_id, file_path, file_name, size_bytes, line_count, word_count,
                     quality_score, complexity_score, readability_score, content_type,
                     cross_references, baseline_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        run_id,
                        metrics.file_path,
                        metrics.file_name,
                        metrics.size_bytes,
                        metrics.line_count,
                        metrics.word_count,
                        metrics.quality_score,
                        metrics.complexity_score,
                        metrics.readability_score,
                        metrics.content_type,
                        json.dumps(metrics.cross_references),
                        json.dumps(asdict(metrics), cls=CustomJSONEncoder),
                    ),
                )

    def _save_baseline_results(self, baseline_summary: BaselineSummary, baseline_metrics: List[BaselineMetrics]):
        """Save baseline results to JSON files."""
        # Save main baseline summary
        summary_file = self.output_dir / "baseline_summary.json"
        with open(summary_file, "w") as f:
            json.dump(asdict(baseline_summary), f, indent=2, cls=CustomJSONEncoder)

        # Save individual baseline metrics
        metrics_file = self.output_dir / "baseline_metrics.json"
        with open(metrics_file, "w") as f:
            json.dump([asdict(metrics) for metrics in baseline_metrics], f, indent=2, cls=CustomJSONEncoder)

        # Generate summary report
        self._generate_summary_report(baseline_summary, baseline_metrics)

    def _generate_summary_report(self, baseline_summary: BaselineSummary, baseline_metrics: List[BaselineMetrics]):
        """Generate a human-readable summary report."""
        report_file = self.output_dir / "baseline_summary.md"

        with open(report_file, "w") as f:
            f.write("# Documentation Baseline Metrics Summary\n\n")
            f.write(f"**Baseline Date:** {baseline_summary.baseline_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Baseline Duration:** {baseline_summary.baseline_duration_seconds:.2f} seconds\n\n")

            f.write("## Overview\n\n")
            f.write(f"- **Total Guides:** {baseline_summary.total_guides}\n")
            f.write(f"- **Total Lines:** {baseline_summary.total_lines:,}\n")
            f.write(f"- **Total Words:** {baseline_summary.total_words:,}\n")
            f.write(f"- **Total Size:** {baseline_summary.total_size_mb:.2f} MB\n")
            f.write(f"- **Average Quality Score:** {baseline_summary.average_quality_score:.2f}\n")
            f.write(f"- **Average Complexity Score:** {baseline_summary.average_complexity_score:.2f}\n")
            f.write(f"- **Average Readability Score:** {baseline_summary.average_readability_score:.2f}\n\n")

            f.write("## Size Distribution\n\n")
            for size, guides in baseline_summary.size_distribution.items():
                f.write(f"- **{size.title()}:** {len(guides)} guides\n")
            f.write("\n")

            f.write("## Quality Distribution\n\n")
            for quality, guides in baseline_summary.quality_distribution.items():
                f.write(f"- **{quality.title()}:** {len(guides)} guides\n")
            f.write("\n")

            f.write("## Content Type Distribution\n\n")
            for content_type, count in baseline_summary.content_type_distribution.items():
                f.write(f"- **{content_type.title()}:** {count} guides\n")
            f.write("\n")

            f.write("## Authority Hierarchy\n\n")
            for indicator, guides in baseline_summary.authority_hierarchy.items():
                f.write(f"- **{indicator.title()}:** {len(guides)} guides\n")
                for guide in guides[:3]:  # Show first 3 guides
                    f.write(f"  - {guide}\n")
                if len(guides) > 3:
                    f.write(f"  - ... and {len(guides) - 3} more\n")
                f.write("\n")

            f.write("## Top Quality Guides\n\n")
            # Show guides with highest quality scores
            sorted_metrics = sorted(baseline_metrics, key=lambda x: x.quality_score, reverse=True)
            f.write("**Guides with highest quality scores:**\n")
            for metrics in sorted_metrics[:10]:
                f.write(f"- {metrics.file_name}: {metrics.quality_score:.2f} (Type: {metrics.content_type})\n")

            f.write("\n## Cross-Reference Network\n\n")
            f.write("**Most referenced guides:**\n")
            reference_counts = Counter()
            for metrics in baseline_metrics:
                for ref in metrics.cross_references:
                    ref_name = Path(ref).name
                    reference_counts[ref_name] += 1

            for ref, count in reference_counts.most_common(10):
                f.write(f"- {ref}: {count} references\n")


def main():
    """Main entry point for the baseline metrics establisher."""
    parser = argparse.ArgumentParser(description="Establish baseline metrics for documentation")
    parser.add_argument("--guides-dir", default="400_guides", help="Directory containing guides")
    parser.add_argument("--output-dir", default="artifacts/baseline", help="Output directory for results")
    parser.add_argument("--establish-baseline", action="store_true", help="Run full baseline establishment")
    parser.add_argument("--all-guides", action="store_true", help="Analyze all guides")
    parser.add_argument("--size-analysis", action="store_true", help="Include detailed size analysis")
    parser.add_argument("--cross-ref-mapping", action="store_true", help="Include cross-reference mapping")

    args = parser.parse_args()

    # Initialize establisher
    establisher = BaselineMetricsEstablisher(args.guides_dir, args.output_dir)

    if args.establish_baseline or args.all_guides:
        print("🚀 Starting baseline metrics establishment...")
        result = establisher.establish_baseline()
        print(f"📊 Baseline results saved to: {establisher.output_dir}")
        return result

    else:
        print("📊 Running baseline establishment...")
        result = establisher.establish_baseline()
        return result


if __name__ == "__main__":
    main()
