#!/usr/bin/env python3
# cspell:ignore lastrowid
"""
Documentation Usage Analysis System for B-1032

Tracks guide access patterns, identifies valuable content, and finds consolidation opportunities.
Part of the t-t3 Authority Structure Implementation.
"""

import argparse
import importlib.util
import json
import re
import sqlite3
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


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


# Optional imports for advanced analysis
try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# Detect optional DSPy package availability without importing unresolved modules
DSPY_AVAILABLE = importlib.util.find_spec("dspy_rag_system") is not None


@dataclass
class GuideMetrics:
    """Metrics for a single guide file."""

    file_path: str
    file_name: str
    size_bytes: int
    line_count: int
    word_count: int
    last_modified: datetime
    days_since_modified: int
    has_tldr: bool
    has_anchor_key: bool
    has_role_pins: bool
    cross_references: List[str]
    internal_links: List[str]
    external_links: List[str]
    code_blocks: int
    headings: List[str]
    complexity_score: float
    readability_score: float
    authority_indicators: List[str]
    consolidation_opportunities: List[str]
    usage_patterns: Dict[str, Any]


@dataclass
class AnalysisResult:
    """Complete analysis result for all guides."""

    total_guides: int
    total_lines: int
    total_words: int
    total_size_mb: float
    average_complexity: float
    average_readability: float
    guides_by_size: Dict[str, List[str]]
    guides_by_complexity: Dict[str, List[str]]
    duplicate_content: List[Tuple[str, str, float]]
    consolidation_suggestions: List[Dict[str, Any]]
    authority_conflicts: List[Dict[str, Any]]
    usage_patterns: Dict[str, Any]
    recommendations: List[str]
    analysis_timestamp: datetime
    analysis_duration_seconds: float


class DocumentationUsageAnalyzer:
    """Main analyzer class for documentation usage patterns."""

    def __init__(self, guides_dir: str = "400_guides", output_dir: str = "artifacts/analysis"):
        self.guides_dir = Path(guides_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize database for historical tracking
        self.db_path = self.output_dir / "usage_analysis.db"
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

        self.complexity_indicators = [
            "advanced",
            "complex",
            "detailed",
            "comprehensive",
            "thorough",
            "extensive",
            "in-depth",
            "technical",
            "sophisticated",
        ]

        self.consolidation_indicators = [
            "similar",
            "related",
            "overlap",
            "duplicate",
            "redundant",
            "merge",
            "combine",
            "consolidate",
            "unify",
        ]

    def _init_database(self):
        """Initialize SQLite database for historical tracking."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS analysis_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total_guides INTEGER,
                    total_lines INTEGER,
                    total_words INTEGER,
                    analysis_duration REAL,
                    results_json TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS guide_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER,
                    file_path TEXT,
                    file_name TEXT,
                    size_bytes INTEGER,
                    line_count INTEGER,
                    word_count INTEGER,
                    complexity_score REAL,
                    readability_score REAL,
                    last_modified TEXT,
                    metrics_json TEXT,
                    FOREIGN KEY (run_id) REFERENCES analysis_runs (id)
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS consolidation_opportunities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER,
                    guide1 TEXT,
                    guide2 TEXT,
                    similarity_score REAL,
                    overlap_content TEXT,
                    suggestion_type TEXT,
                    FOREIGN KEY (run_id) REFERENCES analysis_runs (id)
                )
            """
            )

    def analyze_all_guides(self) -> AnalysisResult:
        """Analyze all guides in the 400_guides directory."""
        start_time = time.time()

        print("🔍 Starting documentation usage analysis...")
        print(f"📁 Analyzing guides in: {self.guides_dir}")

        # Get all markdown files
        guide_files = list(self.guides_dir.glob("*.md"))
        print(f"📄 Found {len(guide_files)} guide files")

        # Analyze each guide
        guide_metrics = []
        for file_path in guide_files:
            try:
                metrics = self._analyze_single_guide(file_path)
                guide_metrics.append(metrics)
                print(f"✅ Analyzed: {file_path.name}")
            except Exception as e:
                print(f"❌ Error analyzing {file_path.name}: {e}")

        # Generate comprehensive analysis
        analysis_result = self._generate_analysis_result(guide_metrics, start_time)

        # Store results in database
        self._store_analysis_results(analysis_result, guide_metrics)

        # Save to JSON
        self._save_analysis_results(analysis_result, guide_metrics)

        print(f"🎯 Analysis complete in {analysis_result.analysis_duration_seconds:.2f} seconds")
        print(f"📊 Results saved to: {self.output_dir}")

        return analysis_result

    def _analyze_single_guide(self, file_path: Path) -> GuideMetrics:
        """Analyze a single guide file."""
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Basic metrics
        size_bytes = file_path.stat().st_size
        line_count = len(lines)
        word_count = len(content.split())

        # File metadata
        stat = file_path.stat()
        last_modified = datetime.fromtimestamp(stat.st_mtime)
        days_since_modified = (datetime.now() - last_modified).days

        # Content analysis
        has_tldr = any("TL;DR" in line for line in lines)
        has_anchor_key = any("ANCHOR_KEY:" in line for line in lines)
        has_role_pins = any("ROLE_PINS:" in line for line in lines)

        # Extract cross-references and links
        cross_references = self._extract_cross_references(content)
        internal_links = self._extract_internal_links(content)
        external_links = self._extract_external_links(content)

        # Count code blocks and headings
        code_blocks = content.count("```")
        headings = self._extract_headings(content)

        # Calculate scores
        complexity_score = self._calculate_complexity_score(content, line_count, word_count)
        readability_score = self._calculate_readability_score(content, line_count, word_count)

        # Authority indicators
        authority_indicators = self._identify_authority_indicators(content)

        # Consolidation opportunities
        consolidation_opportunities = self._identify_consolidation_opportunities(content)

        # Usage patterns
        usage_patterns = self._analyze_usage_patterns(content, file_path.name)

        return GuideMetrics(
            file_path=str(file_path),
            file_name=file_path.name,
            size_bytes=size_bytes,
            line_count=line_count,
            word_count=word_count,
            last_modified=last_modified,
            days_since_modified=days_since_modified,
            has_tldr=has_tldr,
            has_anchor_key=has_anchor_key,
            has_role_pins=has_role_pins,
            cross_references=cross_references,
            internal_links=internal_links,
            external_links=external_links,
            code_blocks=code_blocks,
            headings=headings,
            complexity_score=complexity_score,
            readability_score=readability_score,
            authority_indicators=authority_indicators,
            consolidation_opportunities=consolidation_opportunities,
            usage_patterns=usage_patterns,
        )

    def _extract_cross_references(self, content: str) -> List[str]:
        """Extract cross-references to other guides."""
        # Look for references to other 400_guides files
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

    def _calculate_complexity_score(self, content: str, line_count: int, word_count: int) -> float:
        """Calculate complexity score based on various factors."""
        score = 0.0

        # Base complexity from size
        if line_count > 1000:
            score += 0.3
        elif line_count > 500:
            score += 0.2
        elif line_count > 200:
            score += 0.1

        # Complexity indicators
        complexity_matches = sum(1 for indicator in self.complexity_indicators if indicator.lower() in content.lower())
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

    def _identify_consolidation_opportunities(self, content: str) -> List[str]:
        """Identify potential consolidation opportunities."""
        opportunities = []
        content_lower = content.lower()

        for indicator in self.consolidation_indicators:
            if indicator in content_lower:
                opportunities.append(indicator)

        return opportunities

    def _analyze_usage_patterns(self, content: str, filename: str) -> Dict[str, Any]:
        """Analyze usage patterns in the content."""
        patterns = {
            "has_workflow_references": bool(re.search(r"workflow|process|procedure", content, re.I)),
            "has_code_examples": bool(re.search(r"```\w+", content)),
            "has_configuration": bool(re.search(r"config|setting|parameter", content, re.I)),
            "has_troubleshooting": bool(re.search(r"troubleshoot|debug|error|fix", content, re.I)),
            "has_best_practices": bool(re.search(r"best practice|guideline|recommendation", content, re.I)),
            "has_references": bool(re.search(r"reference|see also|related", content, re.I)),
            "content_type": self._determine_content_type(content, filename),
        }

        return patterns

    def _determine_content_type(self, content: str, filename: str) -> str:
        """Determine the type of content in the guide."""
        content_lower = content.lower()

        if "workflow" in content_lower or "process" in content_lower:
            return "workflow"
        elif "guide" in content_lower or "how-to" in content_lower:
            return "guide"
        elif "reference" in content_lower or "api" in content_lower:
            return "reference"
        elif "best practice" in content_lower or "guideline" in content_lower:
            return "best_practice"
        elif "troubleshoot" in content_lower or "debug" in content_lower:
            return "troubleshooting"
        else:
            return "general"

    def _generate_analysis_result(self, guide_metrics: List[GuideMetrics], start_time: float) -> AnalysisResult:
        """Generate comprehensive analysis result."""
        total_guides = len(guide_metrics)
        total_lines = sum(m.line_count for m in guide_metrics)
        total_words = sum(m.word_count for m in guide_metrics)
        total_size_mb = sum(m.size_bytes for m in guide_metrics) / (1024 * 1024)

        # Calculate averages
        avg_complexity = sum(m.complexity_score for m in guide_metrics) / total_guides if total_guides > 0 else 0
        avg_readability = sum(m.readability_score for m in guide_metrics) / total_guides if total_guides > 0 else 0

        # Group guides by size
        guides_by_size = {
            "small": [m.file_name for m in guide_metrics if m.line_count < 200],
            "medium": [m.file_name for m in guide_metrics if 200 <= m.line_count < 500],
            "large": [m.file_name for m in guide_metrics if 500 <= m.line_count < 1000],
            "very_large": [m.file_name for m in guide_metrics if m.line_count >= 1000],
        }

        # Group guides by complexity
        guides_by_complexity = {
            "low": [m.file_name for m in guide_metrics if m.complexity_score < 0.3],
            "medium": [m.file_name for m in guide_metrics if 0.3 <= m.complexity_score < 0.6],
            "high": [m.file_name for m in guide_metrics if m.complexity_score >= 0.6],
        }

        # Find duplicate content
        duplicate_content = self._find_duplicate_content(guide_metrics)

        # Generate consolidation suggestions
        consolidation_suggestions = self._generate_consolidation_suggestions(guide_metrics)

        # Find authority conflicts
        authority_conflicts = self._find_authority_conflicts(guide_metrics)

        # Analyze usage patterns
        usage_patterns = self._analyze_overall_usage_patterns(guide_metrics)

        # Generate recommendations
        recommendations = self._generate_recommendations(guide_metrics, duplicate_content, consolidation_suggestions)

        analysis_duration = time.time() - start_time

        return AnalysisResult(
            total_guides=total_guides,
            total_lines=total_lines,
            total_words=total_words,
            total_size_mb=total_size_mb,
            average_complexity=avg_complexity,
            average_readability=avg_readability,
            guides_by_size=guides_by_size,
            guides_by_complexity=guides_by_complexity,
            duplicate_content=duplicate_content,
            consolidation_suggestions=consolidation_suggestions,
            authority_conflicts=authority_conflicts,
            usage_patterns=usage_patterns,
            recommendations=recommendations,
            analysis_timestamp=datetime.now(),
            analysis_duration_seconds=analysis_duration,
        )

    def _find_duplicate_content(self, guide_metrics: List[GuideMetrics]) -> List[Tuple[str, str, float]]:
        """Find potential duplicate content between guides."""
        duplicates = []

        for i, guide1 in enumerate(guide_metrics):
            for j, guide2 in enumerate(guide_metrics[i + 1 :], i + 1):
                similarity = self._calculate_content_similarity(guide1, guide2)
                if similarity > 0.3:  # Threshold for potential duplication
                    duplicates.append((guide1.file_name, guide2.file_name, similarity))

        # Sort by similarity score
        duplicates.sort(key=lambda x: x[2], reverse=True)
        return duplicates[:10]  # Return top 10 duplicates

    def _calculate_content_similarity(self, guide1: GuideMetrics, guide2: GuideMetrics) -> float:
        """Calculate similarity between two guides."""
        # Simple similarity based on common words and structure
        content1 = Path(guide1.file_path).read_text(encoding="utf-8").lower()
        content2 = Path(guide2.file_path).read_text(encoding="utf-8").lower()

        # Extract words
        words1 = set(re.findall(r"\b\w+\b", content1))
        words2 = set(re.findall(r"\b\w+\b", content2))

        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        if union == 0:
            return 0.0

        return intersection / union

    def _generate_consolidation_suggestions(self, guide_metrics: List[GuideMetrics]) -> List[Dict[str, Any]]:
        """Generate consolidation suggestions based on analysis."""
        suggestions = []

        # Group by content type
        content_types = defaultdict(list)
        for guide in guide_metrics:
            content_type = guide.usage_patterns.get("content_type", "general")
            content_types[content_type].append(guide)

        # Suggest consolidations for similar content types
        for content_type, guides in content_types.items():
            if len(guides) > 2:
                suggestions.append(
                    {
                        "type": "content_type_consolidation",
                        "content_type": content_type,
                        "guides": [g.file_name for g in guides],
                        "reason": f'Multiple guides of type "{content_type}" could be consolidated',
                        "priority": "medium",
                    }
                )

        # Suggest consolidations for small guides
        small_guides = [g for g in guide_metrics if g.line_count < 100]
        if len(small_guides) > 3:
            suggestions.append(
                {
                    "type": "small_guides_consolidation",
                    "guides": [g.file_name for g in small_guides],
                    "reason": f"{len(small_guides)} small guides could be consolidated into larger, more comprehensive guides",
                    "priority": "high",
                }
            )

        return suggestions

    def _find_authority_conflicts(self, guide_metrics: List[GuideMetrics]) -> List[Dict[str, Any]]:
        """Find potential authority conflicts between guides."""
        conflicts = []

        # Find guides with authority indicators
        authoritative_guides = [g for g in guide_metrics if g.authority_indicators]

        # Check for conflicts in similar content areas
        for i, guide1 in enumerate(authoritative_guides):
            for guide2 in authoritative_guides[i + 1 :]:
                if self._calculate_content_similarity(guide1, guide2) > 0.2:
                    conflicts.append(
                        {
                            "guide1": guide1.file_name,
                            "guide2": guide2.file_name,
                            "similarity": self._calculate_content_similarity(guide1, guide2),
                            "authority_indicators1": guide1.authority_indicators,
                            "authority_indicators2": guide2.authority_indicators,
                            "conflict_type": "overlapping_authority",
                        }
                    )

        return conflicts

    def _analyze_overall_usage_patterns(self, guide_metrics: List[GuideMetrics]) -> Dict[str, Any]:
        """Analyze overall usage patterns across all guides."""
        patterns = {
            "content_type_distribution": Counter(),
            "has_tldr_count": 0,
            "has_anchor_key_count": 0,
            "has_role_pins_count": 0,
            "average_cross_references": 0,
            "average_internal_links": 0,
            "average_external_links": 0,
            "code_blocks_total": 0,
            "recent_updates": 0,  # Updated in last 30 days
            "stale_content": 0,  # Not updated in last 90 days
        }

        for guide in guide_metrics:
            patterns["content_type_distribution"][guide.usage_patterns.get("content_type", "general")] += 1
            patterns["has_tldr_count"] += 1 if guide.has_tldr else 0
            patterns["has_anchor_key_count"] += 1 if guide.has_anchor_key else 0
            patterns["has_role_pins_count"] += 1 if guide.has_role_pins else 0
            patterns["average_cross_references"] += len(guide.cross_references)
            patterns["average_internal_links"] += len(guide.internal_links)
            patterns["average_external_links"] += len(guide.external_links)
            patterns["code_blocks_total"] += guide.code_blocks

            if guide.days_since_modified <= 30:
                patterns["recent_updates"] += 1
            elif guide.days_since_modified > 90:
                patterns["stale_content"] += 1

        # Calculate averages
        total_guides = len(guide_metrics)
        if total_guides > 0:
            patterns["average_cross_references"] /= total_guides
            patterns["average_internal_links"] /= total_guides
            patterns["average_external_links"] /= total_guides

        return patterns

    def _generate_recommendations(
        self,
        guide_metrics: List[GuideMetrics],
        duplicate_content: List[Tuple[str, str, float]],
        consolidation_suggestions: List[Dict[str, Any]],
    ) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []

        # Size-based recommendations
        large_guides = [g for g in guide_metrics if g.line_count > 1000]
        if large_guides:
            recommendations.append(
                f"Consider breaking down {len(large_guides)} large guides into smaller, focused guides"
            )

        small_guides = [g for g in guide_metrics if g.line_count < 100]
        if len(small_guides) > 5:
            recommendations.append(
                f"Consolidate {len(small_guides)} small guides into larger, more comprehensive guides"
            )

        # Quality recommendations
        guides_without_tldr = [g for g in guide_metrics if not g.has_tldr]
        if guides_without_tldr:
            recommendations.append(f"Add TL;DR sections to {len(guides_without_tldr)} guides for better accessibility")

        # Duplicate content recommendations
        if duplicate_content:
            recommendations.append(f"Address {len(duplicate_content)} potential duplicate content issues")

        # Authority recommendations
        guides_with_authority = [g for g in guide_metrics if g.authority_indicators]
        if len(guides_with_authority) > 5:
            recommendations.append("Review authority designations to ensure clear hierarchy")

        # Freshness recommendations
        stale_guides = [g for g in guide_metrics if g.days_since_modified > 90]
        if stale_guides:
            recommendations.append(f"Review and update {len(stale_guides)} stale guides")

        return recommendations

    def _store_analysis_results(self, analysis_result: AnalysisResult, guide_metrics: List[GuideMetrics]):
        """Store analysis results in SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            # Convert analysis result to dict, handling tuples
            analysis_dict = asdict(analysis_result)
            # Convert tuples to lists for JSON serialization
            analysis_dict["duplicate_content"] = [list(item) for item in analysis_dict["duplicate_content"]]

            # Convert any remaining tuple keys to strings
            def convert_tuples_to_strings(obj):
                if isinstance(obj, dict):
                    return {str(k) if isinstance(k, tuple) else k: convert_tuples_to_strings(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_tuples_to_strings(item) for item in obj]
                elif isinstance(obj, tuple):
                    return list(obj)
                else:
                    return obj

            analysis_dict = convert_tuples_to_strings(analysis_dict)

            # Store main analysis run
            cursor = conn.execute(
                """
                INSERT INTO analysis_runs
                (timestamp, total_guides, total_lines, total_words, analysis_duration, results_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    analysis_result.analysis_timestamp.isoformat(),
                    analysis_result.total_guides,
                    analysis_result.total_lines,
                    analysis_result.total_words,
                    analysis_result.analysis_duration_seconds,
                    json.dumps(analysis_dict, cls=CustomJSONEncoder),
                ),
            )
            run_id = cursor.lastrowid

            # Store individual guide metrics
            for guide in guide_metrics:
                conn.execute(
                    """
                    INSERT INTO guide_metrics
                    (run_id, file_path, file_name, size_bytes, line_count, word_count,
                     complexity_score, readability_score, last_modified, metrics_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        run_id,
                        guide.file_path,
                        guide.file_name,
                        guide.size_bytes,
                        guide.line_count,
                        guide.word_count,
                        guide.complexity_score,
                        guide.readability_score,
                        guide.last_modified.isoformat(),
                        json.dumps(asdict(guide), cls=CustomJSONEncoder),
                    ),
                )

            # Store consolidation opportunities
            for suggestion in analysis_result.consolidation_suggestions:
                conn.execute(
                    """
                    INSERT INTO consolidation_opportunities
                    (run_id, guide1, guide2, similarity_score, overlap_content, suggestion_type)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        run_id,
                        suggestion.get("guides", [])[0] if suggestion.get("guides") else "",
                        suggestion.get("guides", [])[1] if len(suggestion.get("guides", [])) > 1 else "",
                        suggestion.get("similarity", 0.0),
                        json.dumps(suggestion),
                        suggestion.get("type", "general"),
                    ),
                )

    def _save_analysis_results(self, analysis_result: AnalysisResult, guide_metrics: List[GuideMetrics]):
        """Save analysis results to JSON files."""
        # Save main analysis result
        analysis_file = self.output_dir / "analysis_result.json"
        analysis_dict = asdict(analysis_result)
        # Convert tuples to lists for JSON serialization
        analysis_dict["duplicate_content"] = [list(item) for item in analysis_dict["duplicate_content"]]

        # Convert any remaining tuple keys to strings
        def convert_tuples_to_strings(obj):
            if isinstance(obj, dict):
                return {str(k) if isinstance(k, tuple) else k: convert_tuples_to_strings(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_tuples_to_strings(item) for item in obj]
            elif isinstance(obj, tuple):
                return list(obj)
            else:
                return obj

        analysis_dict = convert_tuples_to_strings(analysis_dict)

        with open(analysis_file, "w") as f:
            json.dump(analysis_dict, f, indent=2, cls=CustomJSONEncoder)

        # Save individual guide metrics
        metrics_file = self.output_dir / "guide_metrics.json"
        with open(metrics_file, "w") as f:
            json.dump([asdict(guide) for guide in guide_metrics], f, indent=2, cls=CustomJSONEncoder)

        # Generate summary report
        self._generate_summary_report(analysis_result, guide_metrics)

    def _generate_summary_report(self, analysis_result: AnalysisResult, guide_metrics: List[GuideMetrics]):
        """Generate a human-readable summary report."""
        report_file = self.output_dir / "analysis_summary.md"

        with open(report_file, "w") as f:
            f.write("# Documentation Usage Analysis Summary\n\n")
            f.write(f"**Analysis Date:** {analysis_result.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Analysis Duration:** {analysis_result.analysis_duration_seconds:.2f} seconds\n\n")

            f.write("## Overview\n\n")
            f.write(f"- **Total Guides:** {analysis_result.total_guides}\n")
            f.write(f"- **Total Lines:** {analysis_result.total_lines:,}\n")
            f.write(f"- **Total Words:** {analysis_result.total_words:,}\n")
            f.write(f"- **Total Size:** {analysis_result.total_size_mb:.2f} MB\n")
            f.write(f"- **Average Complexity:** {analysis_result.average_complexity:.2f}\n")
            f.write(f"- **Average Readability:** {analysis_result.average_readability:.2f}\n\n")

            f.write("## Size Distribution\n\n")
            for size, guides in analysis_result.guides_by_size.items():
                f.write(f"- **{size.title()}:** {len(guides)} guides\n")
            f.write("\n")

            f.write("## Complexity Distribution\n\n")
            for complexity, guides in analysis_result.guides_by_complexity.items():
                f.write(f"- **{complexity.title()}:** {len(guides)} guides\n")
            f.write("\n")

            f.write("## Top Consolidation Opportunities\n\n")
            for i, suggestion in enumerate(analysis_result.consolidation_suggestions[:5], 1):
                f.write(f"{i}. **{suggestion['type']}:** {suggestion['reason']}\n")
            f.write("\n")

            f.write("## Recommendations\n\n")
            for i, recommendation in enumerate(analysis_result.recommendations, 1):
                f.write(f"{i}. {recommendation}\n")
            f.write("\n")

            f.write("## Usage Patterns\n\n")
            patterns = analysis_result.usage_patterns
            f.write(f"- **Guides with TL;DR:** {patterns['has_tldr_count']}/{analysis_result.total_guides}\n")
            f.write(
                f"- **Guides with Anchor Keys:** {patterns['has_anchor_key_count']}/{analysis_result.total_guides}\n"
            )
            f.write(f"- **Guides with Role Pins:** {patterns['has_role_pins_count']}/{analysis_result.total_guides}\n")
            f.write(f"- **Recent Updates (30 days):** {patterns['recent_updates']}\n")
            f.write(f"- **Stale Content (90+ days):** {patterns['stale_content']}\n")
            f.write(f"- **Total Code Blocks:** {patterns['code_blocks_total']}\n")

    def generate_usage_report(self, output_format: str = "json") -> str:
        """Generate a usage report in the specified format."""
        if output_format == "json":
            return self._generate_json_report()
        elif output_format == "csv" and PANDAS_AVAILABLE:
            return self._generate_csv_report()
        else:
            return self._generate_text_report()

    def _generate_json_report(self) -> str:
        """Generate JSON format usage report."""

        # Query latest analysis results
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT results_json FROM analysis_runs
                ORDER BY timestamp DESC LIMIT 1
            """
            )
            result = cursor.fetchone()

            if result:
                return result[0]
            else:
                return json.dumps({"error": "No analysis results found"})

    def _generate_csv_report(self) -> str:
        """Generate CSV format usage report."""
        if not PANDAS_AVAILABLE:
            return "Pandas not available for CSV generation"

        report_file = self.output_dir / "usage_report.csv"

        # Query guide metrics
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(
                """
                SELECT file_name, line_count, word_count, complexity_score,
                       readability_score, last_modified
                FROM guide_metrics
                WHERE run_id = (SELECT MAX(id) FROM analysis_runs)
            """,
                conn,
            )

            df.to_csv(report_file, index=False)
            return str(report_file)

    def _generate_text_report(self) -> str:
        """Generate text format usage report."""
        report_file = self.output_dir / "usage_report.txt"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT file_name, line_count, complexity_score, readability_score
                FROM guide_metrics
                WHERE run_id = (SELECT MAX(id) FROM analysis_runs)
                ORDER BY complexity_score DESC
            """
            )

            with open(report_file, "w") as f:
                f.write("Documentation Usage Report\n")
                f.write("=" * 50 + "\n\n")

                for row in cursor.fetchall():
                    f.write(f"{row[0]}: {row[1]} lines, complexity: {row[2]:.2f}, readability: {row[3]:.2f}\n")

            return str(report_file)


def main():
    """Main entry point for the documentation usage analyzer."""
    parser = argparse.ArgumentParser(description="Analyze documentation usage patterns")
    parser.add_argument("--guides-dir", default="400_guides", help="Directory containing guides")
    parser.add_argument("--output-dir", default="artifacts/analysis", help="Output directory for results")
    parser.add_argument("--analyze-all", action="store_true", help="Run full analysis")
    parser.add_argument("--output-json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--generate-report", action="store_true", help="Generate usage report")
    parser.add_argument("--report-format", choices=["json", "csv", "text"], default="json", help="Report format")

    args = parser.parse_args()

    # Initialize analyzer
    analyzer = DocumentationUsageAnalyzer(args.guides_dir, args.output_dir)

    if args.analyze_all:
        print("🚀 Starting comprehensive documentation analysis...")
        result = analyzer.analyze_all_guides()

        if args.output_json:
            print(f"📊 Analysis results saved to: {analyzer.output_dir}")
            print(f"📄 JSON output: {analyzer.output_dir}/analysis_result.json")

        return result

    elif args.generate_report:
        print("📋 Generating usage report...")
        report_path = analyzer.generate_usage_report(args.report_format)
        print(f"📄 Report generated: {report_path}")
        return report_path

    else:
        print("🔍 Running quick analysis...")
        result = analyzer.analyze_all_guides()
        return result


if __name__ == "__main__":
    main()
