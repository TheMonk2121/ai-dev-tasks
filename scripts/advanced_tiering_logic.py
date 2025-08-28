#!/usr/bin/env python3
"""
Advanced Tiering Logic System for Documentation t-t3 Authority Structure

This module implements sophisticated content analysis and tier assignment
based on multiple factors including authority indicators, usage patterns,
complexity, and business impact.

Author: AI Assistant
Date: 2025-01-27
"""

import hashlib
import json
import logging
import re
import sqlite3
import statistics
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TierLevel(Enum):
    """Tier levels for documentation"""

    TIER_1 = "T1"  # Critical - Core authority documents
    TIER_2 = "T2"  # High - Important supporting documents
    TIER_3 = "T3"  # Supporting - Reference and utility documents


class AuthorityType(Enum):
    """Types of authority indicators"""

    CORE_WORKFLOW = "core_workflow"
    BEST_PRACTICE = "best_practice"
    REFERENCE = "reference"
    UTILITY = "utility"
    ARCHIVE = "archive"


@dataclass
class ContentMetrics:
    """Metrics for content analysis"""

    word_count: int
    line_count: int
    heading_count: int
    code_block_count: int
    link_count: int
    cross_reference_count: int
    last_modified_days: int
    complexity_score: float
    readability_score: float
    authority_indicators: List[str]
    usage_frequency: int
    dependency_count: int
    business_impact_score: float


@dataclass
class TieringFactors:
    """Factors used for tier determination"""

    authority_weight: float = 0.3
    usage_weight: float = 0.25
    complexity_weight: float = 0.2
    business_impact_weight: float = 0.15
    freshness_weight: float = 0.1


@dataclass
class TieringResult:
    """Result of tiering analysis"""

    file_path: str
    assigned_tier: TierLevel
    confidence_score: float
    reasoning: List[str]
    factors: Dict[str, float]
    recommendations: List[str]
    timestamp: datetime


@dataclass
class AdvancedTieringAnalysis:
    """Complete tiering analysis result"""

    tiering_results: List[TieringResult]
    tier_distribution: Dict[TierLevel, int]
    confidence_stats: Dict[str, float]
    recommendations: List[str]
    timestamp: datetime


class AdvancedTieringLogic:
    """
    Advanced tiering logic system for documentation classification
    """

    def __init__(self, db_path: str = "advanced_tiering.db"):
        """Initialize the advanced tiering system"""
        self.db_path = db_path
        self.tiering_factors = TieringFactors()
        self.authority_patterns = self._load_authority_patterns()
        self.business_impact_keywords = self._load_business_impact_keywords()
        self.init_database()

    def _load_authority_patterns(self) -> Dict[str, List[str]]:
        """Load authority indicator patterns"""
        return {
            "core_workflow": [
                r"workflow",
                r"process",
                r"template",
                r"guide",
                r"procedure",
                r"standard",
                r"protocol",
                r"methodology",
                r"framework",
            ],
            "best_practice": [
                r"best practice",
                r"guideline",
                r"recommendation",
                r"standard",
                r"convention",
                r"pattern",
                r"principle",
                r"rule",
            ],
            "reference": [
                r"reference",
                r"documentation",
                r"specification",
                r"schema",
                r"api",
                r"interface",
                r"configuration",
                r"setup",
            ],
            "utility": [r"utility", r"tool", r"script", r"helper", r"function", r"component", r"module", r"library"],
            "archive": [
                r"legacy",
                r"deprecated",
                r"archive",
                r"old",
                r"outdated",
                r"migration",
                r"upgrade",
                r"replacement",
            ],
        }

    def _load_business_impact_keywords(self) -> Dict[str, float]:
        """Load business impact keywords with weights"""
        return {
            "critical": 1.0,
            "essential": 0.9,
            "core": 0.8,
            "primary": 0.7,
            "important": 0.6,
            "standard": 0.5,
            "optional": 0.3,
            "experimental": 0.2,
            "deprecated": 0.1,
        }

    def init_database(self):
        """Initialize the database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tiering_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    assigned_tier TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    reasoning TEXT,
                    factors TEXT,
                    recommendations TEXT,
                    timestamp TEXT NOT NULL,
                    content_hash TEXT NOT NULL
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tiering_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    content_metrics TEXT,
                    tiering_factors TEXT,
                    analysis_timestamp TEXT NOT NULL
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tiering_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """
            )

            conn.execute("CREATE INDEX IF NOT EXISTS idx_file_path ON tiering_history(file_path)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON tiering_history(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tier ON tiering_history(assigned_tier)")

    def analyze_content_metrics(self, file_path: str) -> ContentMetrics:
        """Analyze content metrics for a file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Basic metrics
            lines = content.split("\n")
            words = content.split()
            headings = len(re.findall(r"^#{1,6}\s+", content, re.MULTILINE))
            code_blocks = len(re.findall(r"```[\s\S]*?```", content))
            links = len(re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content))
            cross_refs = len(re.findall(r"@\w+", content))

            # Last modified
            file_stat = Path(file_path).stat()
            last_modified = datetime.fromtimestamp(file_stat.st_mtime)
            days_since_modified = (datetime.now() - last_modified).days

            # Complexity score (based on content structure)
            complexity_score = self._calculate_complexity_score(content, headings, code_blocks)

            # Readability score
            readability_score = self._calculate_readability_score(content, words)

            # Authority indicators
            authority_indicators = self._extract_authority_indicators(content)

            # Usage frequency (placeholder - would integrate with actual usage tracking)
            usage_frequency = self._estimate_usage_frequency(file_path)

            # Dependency count
            dependency_count = self._count_dependencies(content)

            # Business impact score
            business_impact_score = self._calculate_business_impact_score(content)

            return ContentMetrics(
                word_count=len(words),
                line_count=len(lines),
                heading_count=headings,
                code_block_count=code_blocks,
                link_count=links,
                cross_reference_count=cross_refs,
                last_modified_days=days_since_modified,
                complexity_score=complexity_score,
                readability_score=readability_score,
                authority_indicators=authority_indicators,
                usage_frequency=usage_frequency,
                dependency_count=dependency_count,
                business_impact_score=business_impact_score,
            )

        except Exception as e:
            logger.error(f"Error analyzing content metrics for {file_path}: {e}")
            return ContentMetrics(
                word_count=0,
                line_count=0,
                heading_count=0,
                code_block_count=0,
                link_count=0,
                cross_reference_count=0,
                last_modified_days=999,
                complexity_score=0.0,
                readability_score=0.0,
                authority_indicators=[],
                usage_frequency=0,
                dependency_count=0,
                business_impact_score=0.0,
            )

    def _calculate_complexity_score(self, content: str, headings: int, code_blocks: int) -> float:
        """Calculate complexity score based on content structure"""
        # Base complexity from structure
        structure_complexity = min(1.0, (headings * 0.1) + (code_blocks * 0.15))

        # Content complexity
        sentences = len(re.findall(r"[.!?]+", content))
        avg_sentence_length = len(content.split()) / max(sentences, 1)
        sentence_complexity = min(1.0, avg_sentence_length / 50.0)

        # Technical complexity
        technical_terms = len(
            re.findall(
                r"\b(api|database|schema|config|workflow|integration|deployment|monitoring)\b", content, re.IGNORECASE
            )
        )
        technical_complexity = min(1.0, technical_terms / 20.0)

        return (structure_complexity + sentence_complexity + technical_complexity) / 3.0

    def _calculate_readability_score(self, content: str, words: List[str]) -> float:
        """Calculate readability score (Flesch Reading Ease approximation)"""
        if not words:
            return 0.0

        sentences = len(re.findall(r"[.!?]+", content))
        syllables = sum(self._count_syllables(word) for word in words)

        if sentences == 0 or syllables == 0:
            return 0.0

        # Simplified Flesch Reading Ease
        avg_sentence_length = len(words) / sentences
        avg_syllables_per_word = syllables / len(words)

        readability = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        return max(0.0, min(100.0, readability)) / 100.0

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)"""
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        on_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not on_vowel:
                count += 1
            on_vowel = is_vowel

        return max(1, count)

    def _extract_authority_indicators(self, content: str) -> List[str]:
        """Extract authority indicators from content"""
        indicators = []
        content_lower = content.lower()

        for auth_type, patterns in self.authority_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    indicators.append(auth_type)
                    break

        return list(set(indicators))

    def _estimate_usage_frequency(self, file_path: str) -> int:
        """Estimate usage frequency (placeholder implementation)"""
        # In a real implementation, this would integrate with actual usage tracking
        # For now, use file age and cross-references as proxies
        try:
            file_stat = Path(file_path).stat()
            days_old = (datetime.now() - datetime.fromtimestamp(file_stat.st_mtime)).days

            # Older files might be more established
            if days_old < 30:
                return 1
            elif days_old < 90:
                return 2
            elif days_old < 365:
                return 3
            else:
                return 4
        except:
            return 1

    def _count_dependencies(self, content: str) -> int:
        """Count dependencies and references"""
        # Count various types of dependencies
        imports = len(re.findall(r"^import\s+\w+", content, re.MULTILINE))
        requires = len(re.findall(r"requires?", content, re.IGNORECASE))
        depends = len(re.findall(r"depends?", content, re.IGNORECASE))
        references = len(re.findall(r"@\w+", content))

        return imports + requires + depends + references

    def _calculate_business_impact_score(self, content: str) -> float:
        """Calculate business impact score"""
        content_lower = content.lower()
        total_score = 0.0
        keyword_count = 0

        for keyword, weight in self.business_impact_keywords.items():
            count = len(re.findall(rf"\b{keyword}\b", content_lower))
            if count > 0:
                total_score += weight * count
                keyword_count += count

        if keyword_count == 0:
            return 0.5  # Default neutral score

        return total_score / keyword_count

    def determine_tier(self, metrics: ContentMetrics) -> Tuple[TierLevel, float, List[str]]:
        """Determine tier based on content metrics"""
        reasoning = []

        # Calculate factor scores
        authority_score = self._calculate_authority_score(metrics)
        usage_score = self._calculate_usage_score(metrics)
        complexity_score = metrics.complexity_score
        business_impact_score = metrics.business_impact_score
        freshness_score = self._calculate_freshness_score(metrics)

        # Weighted composite score
        composite_score = (
            authority_score * self.tiering_factors.authority_weight
            + usage_score * self.tiering_factors.usage_weight
            + complexity_score * self.tiering_factors.complexity_weight
            + business_impact_score * self.tiering_factors.business_impact_weight
            + freshness_score * self.tiering_factors.freshness_weight
        )

        # Determine tier based on composite score
        if composite_score >= 0.8:
            tier = TierLevel.TIER_1
            reasoning.append(f"High composite score ({composite_score:.2f}) indicates critical importance")
        elif composite_score >= 0.6:
            tier = TierLevel.TIER_2
            reasoning.append(f"Moderate composite score ({composite_score:.2f}) indicates high importance")
        else:
            tier = TierLevel.TIER_3
            reasoning.append(f"Lower composite score ({composite_score:.2f}) indicates supporting role")

        # Add specific reasoning
        if authority_score > 0.8:
            reasoning.append("High authority indicators detected")
        if usage_score > 0.7:
            reasoning.append("High usage frequency indicates importance")
        if business_impact_score > 0.8:
            reasoning.append("High business impact keywords detected")
        if metrics.last_modified_days > 365:
            reasoning.append("Document is over 1 year old - consider review")

        confidence_score = min(1.0, composite_score + 0.2)  # Boost confidence for higher scores

        return tier, confidence_score, reasoning

    def _calculate_authority_score(self, metrics: ContentMetrics) -> float:
        """Calculate authority score based on indicators"""
        if not metrics.authority_indicators:
            return 0.3

        # Weight different authority types
        authority_weights = {
            "core_workflow": 1.0,
            "best_practice": 0.9,
            "reference": 0.7,
            "utility": 0.5,
            "archive": 0.2,
        }

        total_weight = 0.0
        for indicator in metrics.authority_indicators:
            total_weight += authority_weights.get(indicator, 0.5)

        return min(1.0, total_weight / len(metrics.authority_indicators))

    def _calculate_usage_score(self, metrics: ContentMetrics) -> float:
        """Calculate usage score based on frequency and dependencies"""
        # Normalize usage frequency (1-4 scale to 0-1)
        usage_score = min(1.0, metrics.usage_frequency / 4.0)

        # Factor in dependencies
        dependency_score = min(1.0, metrics.dependency_count / 10.0)

        return (usage_score + dependency_score) / 2.0

    def _calculate_freshness_score(self, metrics: ContentMetrics) -> float:
        """Calculate freshness score based on last modified date"""
        if metrics.last_modified_days <= 30:
            return 1.0
        elif metrics.last_modified_days <= 90:
            return 0.8
        elif metrics.last_modified_days <= 365:
            return 0.6
        else:
            return 0.3

    def analyze_file(self, file_path: str) -> TieringResult:
        """Analyze a single file and determine its tier"""
        logger.info(f"Analyzing file: {file_path}")

        # Analyze content metrics
        metrics = self.analyze_content_metrics(file_path)

        # Determine tier
        tier, confidence, reasoning = self.determine_tier(metrics)

        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, tier)

        # Create result
        result = TieringResult(
            file_path=file_path,
            assigned_tier=tier,
            confidence_score=confidence,
            reasoning=reasoning,
            factors={
                "authority": self._calculate_authority_score(metrics),
                "usage": self._calculate_usage_score(metrics),
                "complexity": metrics.complexity_score,
                "business_impact": metrics.business_impact_score,
                "freshness": self._calculate_freshness_score(metrics),
            },
            recommendations=recommendations,
            timestamp=datetime.now(),
        )

        # Store in database
        self._store_tiering_result(result, metrics)

        return result

    def _generate_recommendations(self, metrics: ContentMetrics, tier: TierLevel) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        # Content quality recommendations
        if metrics.readability_score < 0.5:
            recommendations.append("Consider improving readability - content may be too complex")

        if metrics.last_modified_days > 365:
            recommendations.append("Document is over 1 year old - consider review and update")

        if metrics.complexity_score > 0.8:
            recommendations.append("High complexity detected - consider breaking into smaller documents")

        # Authority recommendations
        if not metrics.authority_indicators:
            recommendations.append("No clear authority indicators - consider adding purpose and scope")

        # Tier-specific recommendations
        if tier == TierLevel.TIER_1:
            recommendations.append("Tier 1 document - ensure comprehensive coverage and regular review")
        elif tier == TierLevel.TIER_2:
            recommendations.append("Tier 2 document - maintain quality and cross-references")
        else:
            recommendations.append("Tier 3 document - consider consolidation if similar content exists")

        return recommendations

    def _store_tiering_result(self, result: TieringResult, metrics: ContentMetrics):
        """Store tiering result in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Store tiering result
                conn.execute(
                    """
                    INSERT INTO tiering_history
                    (file_path, assigned_tier, confidence_score, reasoning, factors, recommendations, timestamp, content_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        result.file_path,
                        result.assigned_tier.value,
                        result.confidence_score,
                        json.dumps(result.reasoning),
                        json.dumps(result.factors),
                        json.dumps(result.recommendations),
                        result.timestamp.isoformat(),
                        self._calculate_content_hash(result.file_path),
                    ),
                )

                # Store metrics
                conn.execute(
                    """
                    INSERT INTO tiering_metrics
                    (file_path, content_metrics, tiering_factors, analysis_timestamp)
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        result.file_path,
                        json.dumps(asdict(metrics)),
                        json.dumps(asdict(self.tiering_factors)),
                        result.timestamp.isoformat(),
                    ),
                )

        except Exception as e:
            logger.error(f"Error storing tiering result: {e}")

    def _calculate_content_hash(self, file_path: str) -> str:
        """Calculate content hash for change detection"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return hashlib.md5(content.encode()).hexdigest()
        except:
            return ""

    def analyze_directory(self, directory_path: str, file_pattern: str = "*.md") -> AdvancedTieringAnalysis:
        """Analyze all files in a directory"""
        logger.info(f"Analyzing directory: {directory_path}")

        directory = Path(directory_path)
        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory_path}")

        # Find all matching files
        files = list(directory.rglob(file_pattern))
        logger.info(f"Found {len(files)} files to analyze")

        # Analyze each file
        tiering_results = []
        for file_path in files:
            try:
                result = self.analyze_file(str(file_path))
                tiering_results.append(result)
            except Exception as e:
                logger.error(f"Error analyzing {file_path}: {e}")

        # Calculate statistics
        tier_distribution = Counter(result.assigned_tier for result in tiering_results)
        confidence_scores = [result.confidence_score for result in tiering_results]

        confidence_stats = {
            "mean": statistics.mean(confidence_scores) if confidence_scores else 0.0,
            "median": statistics.median(confidence_scores) if confidence_scores else 0.0,
            "min": min(confidence_scores) if confidence_scores else 0.0,
            "max": max(confidence_scores) if confidence_scores else 0.0,
        }

        # Generate overall recommendations
        recommendations = self._generate_overall_recommendations(tiering_results)

        return AdvancedTieringAnalysis(
            tiering_results=tiering_results,
            tier_distribution=dict(tier_distribution),
            confidence_stats=confidence_stats,
            recommendations=recommendations,
            timestamp=datetime.now(),
        )

    def _generate_overall_recommendations(self, results: List[TieringResult]) -> List[str]:
        """Generate overall recommendations based on analysis results"""
        recommendations = []

        # Tier distribution analysis
        tier_counts = Counter(result.assigned_tier for result in results)
        total_files = len(results)

        if tier_counts.get(TierLevel.TIER_1, 0) > total_files * 0.3:
            recommendations.append("High proportion of Tier 1 documents - consider if all are truly critical")

        if tier_counts.get(TierLevel.TIER_3, 0) > total_files * 0.6:
            recommendations.append("High proportion of Tier 3 documents - consider consolidation opportunities")

        # Confidence analysis
        low_confidence = [r for r in results if r.confidence_score < 0.6]
        if low_confidence:
            recommendations.append(f"{len(low_confidence)} documents have low confidence scores - review manually")

        # Freshness analysis
        old_documents = [r for r in results if any("over 1 year old" in rec for rec in r.recommendations)]
        if old_documents:
            recommendations.append(f"{len(old_documents)} documents are over 1 year old - schedule review")

        return recommendations

    def get_tiering_history(self, file_path: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get tiering history from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                if file_path:
                    cursor = conn.execute(
                        """
                        SELECT * FROM tiering_history
                        WHERE file_path = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    """,
                        (file_path, limit),
                    )
                else:
                    cursor = conn.execute(
                        """
                        SELECT * FROM tiering_history
                        ORDER BY timestamp DESC
                        LIMIT ?
                    """,
                        (limit,),
                    )

                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Error retrieving tiering history: {e}")
            return []

    def export_analysis(
        self, analysis: AdvancedTieringAnalysis, output_dir: str = "artifacts/analysis"
    ) -> Dict[str, str]:
        """Export analysis results to files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = analysis.timestamp.strftime("%Y%m%d_%H%M%S")

        # Export detailed results
        results_file = output_path / f"advanced_tiering_results_{timestamp}.json"
        with open(results_file, "w") as f:
            json.dump(
                {
                    "timestamp": analysis.timestamp.isoformat(),
                    "tier_distribution": {k.value: v for k, v in analysis.tier_distribution.items()},
                    "confidence_stats": analysis.confidence_stats,
                    "recommendations": analysis.recommendations,
                    "results": [
                        {
                            "file_path": r.file_path,
                            "assigned_tier": r.assigned_tier.value,
                            "confidence_score": r.confidence_score,
                            "reasoning": r.reasoning,
                            "factors": r.factors,
                            "recommendations": r.recommendations,
                            "timestamp": r.timestamp.isoformat(),
                        }
                        for r in analysis.tiering_results
                    ],
                },
                f,
                indent=2,
            )

        # Export summary report
        summary_file = output_path / f"advanced_tiering_summary_{timestamp}.md"
        with open(summary_file, "w") as f:
            f.write("# Advanced Tiering Analysis Summary\n\n")
            f.write(f"**Analysis Date:** {analysis.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Tier Distribution\n\n")
            for tier, count in analysis.tier_distribution.items():
                percentage = (count / len(analysis.tiering_results)) * 100
                f.write(f"- **{tier.value}:** {count} documents ({percentage:.1f}%)\n")

            f.write("\n## Confidence Statistics\n\n")
            for stat, value in analysis.confidence_stats.items():
                f.write(f"- **{stat.title()}:** {value:.3f}\n")

            f.write("\n## Recommendations\n\n")
            for i, rec in enumerate(analysis.recommendations, 1):
                f.write(f"{i}. {rec}\n")

            f.write("\n## Detailed Results\n\n")
            for result in analysis.tiering_results:
                f.write(f"### {Path(result.file_path).name}\n\n")
                f.write(f"- **Tier:** {result.assigned_tier.value}\n")
                f.write(f"- **Confidence:** {result.confidence_score:.3f}\n")
                f.write(f"- **Reasoning:** {'; '.join(result.reasoning)}\n")
                f.write(f"- **Recommendations:** {'; '.join(result.recommendations)}\n\n")

        return {"results": str(results_file), "summary": str(summary_file)}


def main():
    """Main function for command-line usage"""
    import argparse

    parser = argparse.ArgumentParser(description="Advanced Tiering Logic System")
    parser.add_argument("path", help="File or directory path to analyze")
    parser.add_argument("--output", "-o", default="artifacts/analysis", help="Output directory for results")
    parser.add_argument("--pattern", "-p", default="*.md", help="File pattern to match (for directories)")
    parser.add_argument("--history", action="store_true", help="Show tiering history")

    args = parser.parse_args()

    # Initialize system
    tiering_system = AdvancedTieringLogic()

    path = Path(args.path)

    if args.history:
        # Show history
        history = tiering_system.get_tiering_history(str(path) if path.is_file() else None)
        print(f"Tiering History ({len(history)} entries):")
        for entry in history[:10]:  # Show last 10
            print(f"- {entry['file_path']}: {entry['assigned_tier']} " f"(confidence: {entry['confidence_score']:.3f})")
        return

    if path.is_file():
        # Analyze single file
        result = tiering_system.analyze_file(str(path))
        print(f"Analysis Result for {path.name}:")
        print(f"- Tier: {result.assigned_tier.value}")
        print(f"- Confidence: {result.confidence_score:.3f}")
        print(f"- Reasoning: {'; '.join(result.reasoning)}")
        print(f"- Recommendations: {'; '.join(result.recommendations)}")

    elif path.is_dir():
        # Analyze directory
        analysis = tiering_system.analyze_directory(str(path), args.pattern)

        print("Analysis Complete:")
        print(f"- Files analyzed: {len(analysis.tiering_results)}")
        print(f"- Tier distribution: {analysis.tier_distribution}")
        print(f"- Average confidence: {analysis.confidence_stats['mean']:.3f}")
        print(f"- Recommendations: {len(analysis.recommendations)}")

        # Export results
        output_files = tiering_system.export_analysis(analysis, args.output)
        print("\nResults exported to:")
        for file_type, file_path in output_files.items():
            print(f"- {file_type}: {file_path}")

    else:
        print(f"Error: Path does not exist: {path}")


if __name__ == "__main__":
    main()
