#!/usr/bin/env python3
"""
AI-Powered Consolidation System for B-1032

Uses NLP techniques, content similarity analysis, and confidence scoring to identify
consolidation opportunities in documentation. Part of the t-t3 Authority Structure Implementation.
"""

import argparse
import json
import re
import sqlite3
import time
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional


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
class ConsolidationOpportunity:
    """Represents a potential consolidation opportunity."""

    source_guides: List[str]
    target_guide: Optional[str]
    similarity_score: float
    confidence_score: float
    consolidation_type: str
    overlap_content: List[str]
    merge_strategy: str
    estimated_effort: str
    risk_level: str
    benefits: List[str]
    challenges: List[str]
    created_at: datetime


@dataclass
class ConsolidationAnalysis:
    """Complete consolidation analysis result."""

    total_opportunities: int
    high_confidence_opportunities: int
    medium_confidence_opportunities: int
    low_confidence_opportunities: int
    opportunities_by_type: Dict[str, List[ConsolidationOpportunity]]
    similarity_matrix: Dict[str, Dict[str, float]]
    consolidation_recommendations: List[Dict[str, Any]]
    analysis_timestamp: datetime
    analysis_duration_seconds: float


class AIConsolidationSystem:
    """Main AI-powered consolidation system."""

    def __init__(self, guides_dir: str = "400_guides", output_dir: str = "artifacts/consolidation"):
        self.guides_dir = Path(guides_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize database for consolidation history
        self.db_path = self.output_dir / "consolidation_history.db"
        self._init_database()

        # Consolidation thresholds
        self.similarity_threshold = 0.3
        self.confidence_threshold = 0.7
        self.min_content_overlap = 0.1

        # Content type patterns for consolidation
        self.consolidation_patterns = {
            "duplicate_content": ["duplicate", "same", "identical", "copy"],
            "related_topics": ["related", "similar", "connected", "associated"],
            "workflow_consolidation": ["workflow", "process", "procedure", "step"],
            "reference_consolidation": ["reference", "guide", "manual", "documentation"],
            "best_practice_consolidation": ["best practice", "guideline", "recommendation"],
        }

    def _init_database(self):
        """Initialize SQLite database for consolidation history."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS consolidation_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total_opportunities INTEGER,
                    high_confidence_count INTEGER,
                    medium_confidence_count INTEGER,
                    low_confidence_count INTEGER,
                    analysis_duration REAL,
                    results_json TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS consolidation_opportunities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER,
                    source_guides TEXT,
                    target_guide TEXT,
                    similarity_score REAL,
                    confidence_score REAL,
                    consolidation_type TEXT,
                    overlap_content TEXT,
                    merge_strategy TEXT,
                    estimated_effort TEXT,
                    risk_level TEXT,
                    benefits TEXT,
                    challenges TEXT,
                    opportunity_json TEXT,
                    FOREIGN KEY (run_id) REFERENCES consolidation_runs (id)
                )
            """
            )

    def analyze_consolidation_opportunities(self) -> ConsolidationAnalysis:
        """Analyze all guides for consolidation opportunities."""
        start_time = time.time()

        print("🤖 Starting AI-powered consolidation analysis...")
        print(f"📁 Analyzing guides in: {self.guides_dir}")

        # Get all markdown files
        guide_files = list(self.guides_dir.glob("*.md"))
        print(f"📄 Found {len(guide_files)} guide files")

        # Load guide contents
        guide_contents = {}
        for file_path in guide_files:
            try:
                content = file_path.read_text(encoding="utf-8")
                guide_contents[file_path.name] = content
                print(f"✅ Loaded: {file_path.name}")
            except Exception as e:
                print(f"❌ Error loading {file_path.name}: {e}")

        # Generate similarity matrix
        similarity_matrix = self._generate_similarity_matrix(guide_contents)

        # Find consolidation opportunities
        opportunities = self._find_consolidation_opportunities(guide_contents, similarity_matrix)

        # Generate analysis result
        analysis_result = self._generate_analysis_result(opportunities, similarity_matrix, start_time)

        # Store results in database
        self._store_consolidation_results(analysis_result, opportunities)

        # Save to JSON
        self._save_consolidation_results(analysis_result, opportunities)

        print(f"🎯 Consolidation analysis complete in {analysis_result.analysis_duration_seconds:.2f} seconds")
        print(f"📊 Results saved to: {self.output_dir}")

        return analysis_result

    def _generate_similarity_matrix(self, guide_contents: Dict[str, str]) -> Dict[str, Dict[str, float]]:
        """Generate similarity matrix between all guides."""
        print("🔍 Generating similarity matrix...")

        similarity_matrix = {}
        guide_names = list(guide_contents.keys())

        for i, guide1 in enumerate(guide_names):
            similarity_matrix[guide1] = {}
            for j, guide2 in enumerate(guide_names):
                if i == j:
                    similarity_matrix[guide1][guide2] = 1.0
                else:
                    similarity = self._calculate_content_similarity(guide_contents[guide1], guide_contents[guide2])
                    similarity_matrix[guide1][guide2] = similarity

        return similarity_matrix

    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two content pieces using multiple methods."""
        # Method 1: Jaccard similarity on words
        words1 = set(re.findall(r"\b\w+\b", content1.lower()))
        words2 = set(re.findall(r"\b\w+\b", content2.lower()))

        if len(words1.union(words2)) == 0:
            jaccard_similarity = 0.0
        else:
            jaccard_similarity = len(words1.intersection(words2)) / len(words1.union(words2))

        # Method 2: Sequence similarity
        sequence_similarity = SequenceMatcher(None, content1, content2).ratio()

        # Method 3: Heading similarity
        headings1 = set(re.findall(r"^#{1,6}\s+(.+)$", content1, re.MULTILINE))
        headings2 = set(re.findall(r"^#{1,6}\s+(.+)$", content2, re.MULTILINE))

        if len(headings1.union(headings2)) == 0:
            heading_similarity = 0.0
        else:
            heading_similarity = len(headings1.intersection(headings2)) / len(headings1.union(headings2))

        # Method 4: Code block similarity
        code_blocks1 = re.findall(r"```[\s\S]*?```", content1)
        code_blocks2 = re.findall(r"```[\s\S]*?```", content2)

        if len(code_blocks1) + len(code_blocks2) == 0:
            code_similarity = 0.0
        else:
            code_similarity = len(set(code_blocks1).intersection(set(code_blocks2))) / len(
                set(code_blocks1).union(set(code_blocks2))
            )

        # Weighted combination
        weighted_similarity = (
            jaccard_similarity * 0.4 + sequence_similarity * 0.3 + heading_similarity * 0.2 + code_similarity * 0.1
        )

        return weighted_similarity

    def _find_consolidation_opportunities(
        self, guide_contents: Dict[str, str], similarity_matrix: Dict[str, Dict[str, float]]
    ) -> List[ConsolidationOpportunity]:
        """Find consolidation opportunities based on similarity analysis."""
        print("🔍 Finding consolidation opportunities...")

        opportunities = []
        guide_names = list(guide_contents.keys())

        # Find high similarity pairs
        for i, guide1 in enumerate(guide_names):
            for j, guide2 in enumerate(guide_names[i + 1 :], i + 1):
                similarity = similarity_matrix[guide1][guide2]

                if similarity >= self.similarity_threshold:
                    opportunity = self._create_consolidation_opportunity(guide1, guide2, similarity, guide_contents)
                    if opportunity:
                        opportunities.append(opportunity)

        # Find content type consolidation opportunities
        type_opportunities = self._find_content_type_opportunities(guide_contents)
        opportunities.extend(type_opportunities)

        # Find small guide consolidation opportunities
        small_guide_opportunities = self._find_small_guide_opportunities(guide_contents)
        opportunities.extend(small_guide_opportunities)

        # Sort by confidence score
        opportunities.sort(key=lambda x: x.confidence_score, reverse=True)

        return opportunities

    def _create_consolidation_opportunity(
        self, guide1: str, guide2: str, similarity: float, guide_contents: Dict[str, str]
    ) -> Optional[ConsolidationOpportunity]:
        """Create a consolidation opportunity for two similar guides."""
        content1 = guide_contents[guide1]
        content2 = guide_contents[guide2]

        # Determine consolidation type
        consolidation_type = self._determine_consolidation_type(content1, content2)

        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(similarity, content1, content2, consolidation_type)

        # Find overlap content
        overlap_content = self._find_overlap_content(content1, content2)

        # Determine merge strategy
        merge_strategy = self._determine_merge_strategy(consolidation_type, similarity)

        # Estimate effort
        estimated_effort = self._estimate_effort(content1, content2, consolidation_type)

        # Assess risk level
        risk_level = self._assess_risk_level(similarity, consolidation_type, len(overlap_content))

        # Identify benefits and challenges
        benefits = self._identify_benefits(guide1, guide2, consolidation_type)
        challenges = self._identify_challenges(guide1, guide2, consolidation_type)

        # Determine target guide (larger or more comprehensive one)
        target_guide = guide1 if len(content1) >= len(content2) else guide2

        return ConsolidationOpportunity(
            source_guides=[guide1, guide2],
            target_guide=target_guide,
            similarity_score=similarity,
            confidence_score=confidence_score,
            consolidation_type=consolidation_type,
            overlap_content=overlap_content,
            merge_strategy=merge_strategy,
            estimated_effort=estimated_effort,
            risk_level=risk_level,
            benefits=benefits,
            challenges=challenges,
            created_at=datetime.now(),
        )

    def _determine_consolidation_type(self, content1: str, content2: str) -> str:
        """Determine the type of consolidation needed."""
        # Check for duplicate content
        if self._is_duplicate_content(content1, content2):
            return "duplicate_content"

        # Check for related topics
        if self._is_related_content(content1, content2):
            return "related_topics"

        # Check for workflow consolidation
        if self._is_workflow_content(content1, content2):
            return "workflow_consolidation"

        # Check for reference consolidation
        if self._is_reference_content(content1, content2):
            return "reference_consolidation"

        # Check for best practice consolidation
        if self._is_best_practice_content(content1, content2):
            return "best_practice_consolidation"

        return "general_consolidation"

    def _is_duplicate_content(self, content1: str, content2: str) -> bool:
        """Check if content is duplicate or nearly duplicate."""
        similarity = SequenceMatcher(None, content1, content2).ratio()
        return similarity > 0.8

    def _is_related_content(self, content1: str, content2: str) -> bool:
        """Check if content is related."""
        words1 = set(re.findall(r"\b\w+\b", content1.lower()))
        words2 = set(re.findall(r"\b\w+\b", content2.lower()))

        common_words = words1.intersection(words2)
        return len(common_words) > 10

    def _is_workflow_content(self, content1: str, content2: str) -> bool:
        """Check if content is workflow-related."""
        workflow_indicators = ["workflow", "process", "procedure", "step", "sequence"]
        content_lower1 = content1.lower()
        content_lower2 = content2.lower()

        return any(indicator in content_lower1 and indicator in content_lower2 for indicator in workflow_indicators)

    def _is_reference_content(self, content1: str, content2: str) -> bool:
        """Check if content is reference material."""
        reference_indicators = ["reference", "guide", "manual", "documentation", "api"]
        content_lower1 = content1.lower()
        content_lower2 = content2.lower()

        return any(indicator in content_lower1 and indicator in content_lower2 for indicator in reference_indicators)

    def _is_best_practice_content(self, content1: str, content2: str) -> bool:
        """Check if content is best practice material."""
        practice_indicators = ["best practice", "guideline", "recommendation", "standard"]
        content_lower1 = content1.lower()
        content_lower2 = content2.lower()

        return any(indicator in content_lower1 and indicator in content_lower2 for indicator in practice_indicators)

    def _calculate_confidence_score(
        self, similarity: float, content1: str, content2: str, consolidation_type: str
    ) -> float:
        """Calculate confidence score for consolidation opportunity."""
        base_score = similarity

        # Adjust based on content type
        type_multipliers = {
            "duplicate_content": 1.2,
            "related_topics": 1.0,
            "workflow_consolidation": 0.9,
            "reference_consolidation": 0.8,
            "best_practice_consolidation": 0.9,
            "general_consolidation": 0.7,
        }

        base_score *= type_multipliers.get(consolidation_type, 1.0)

        # Adjust based on content size
        size1, size2 = len(content1), len(content2)
        size_ratio = min(size1, size2) / max(size1, size2)
        base_score *= 0.8 + 0.2 * size_ratio

        # Adjust based on structure similarity
        headings1 = re.findall(r"^#{1,6}\s+(.+)$", content1, re.MULTILINE)
        headings2 = re.findall(r"^#{1,6}\s+(.+)$", content2, re.MULTILINE)

        if len(headings1) + len(headings2) > 0:
            heading_similarity = len(set(headings1).intersection(set(headings2))) / len(
                set(headings1).union(set(headings2))
            )
            base_score *= 0.9 + 0.1 * heading_similarity

        return min(base_score, 1.0)

    def _find_overlap_content(self, content1: str, content2: str) -> List[str]:
        """Find overlapping content between two guides."""
        overlap = []

        # Find overlapping headings
        headings1 = re.findall(r"^#{1,6}\s+(.+)$", content1, re.MULTILINE)
        headings2 = re.findall(r"^#{1,6}\s+(.+)$", content2, re.MULTILINE)

        common_headings = set(headings1).intersection(set(headings2))
        overlap.extend([f"Heading: {h}" for h in common_headings])

        # Find overlapping code blocks
        code_blocks1 = re.findall(r"```[\s\S]*?```", content1)
        code_blocks2 = re.findall(r"```[\s\S]*?```", content2)

        common_code = set(code_blocks1).intersection(set(code_blocks2))
        overlap.extend([f"Code block: {len(c)} chars" for c in common_code])

        # Find overlapping links
        links1 = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content1)
        links2 = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content2)

        common_links = set(links1).intersection(set(links2))
        overlap.extend([f"Link: {link[0]}" for link in common_links])

        return overlap

    def _determine_merge_strategy(self, consolidation_type: str, similarity: float) -> str:
        """Determine the best merge strategy."""
        if similarity > 0.8:
            return "content_replacement"
        elif similarity > 0.6:
            return "content_merging"
        elif similarity > 0.4:
            return "section_consolidation"
        else:
            return "reference_consolidation"

    def _estimate_effort(self, content1: str, content2: str, consolidation_type: str) -> str:
        """Estimate the effort required for consolidation."""
        total_size = len(content1) + len(content2)

        if total_size < 5000:
            return "Low (1-2 hours)"
        elif total_size < 15000:
            return "Medium (3-5 hours)"
        elif total_size < 30000:
            return "High (6-10 hours)"
        else:
            return "Very High (10+ hours)"

    def _assess_risk_level(self, similarity: float, consolidation_type: str, overlap_count: int) -> str:
        """Assess the risk level of consolidation."""
        if similarity > 0.8 and consolidation_type == "duplicate_content":
            return "Low"
        elif similarity > 0.6 and overlap_count > 3:
            return "Medium"
        elif similarity > 0.4:
            return "Medium-High"
        else:
            return "High"

    def _identify_benefits(self, guide1: str, guide2: str, consolidation_type: str) -> List[str]:
        """Identify benefits of consolidation."""
        benefits = []

        if consolidation_type == "duplicate_content":
            benefits.extend(
                ["Eliminate duplicate information", "Reduce maintenance overhead", "Improve content consistency"]
            )
        elif consolidation_type == "related_topics":
            benefits.extend(["Create comprehensive guide", "Improve discoverability", "Reduce navigation complexity"])
        elif consolidation_type == "workflow_consolidation":
            benefits.extend(
                ["Streamline workflow documentation", "Create end-to-end process guide", "Reduce process fragmentation"]
            )
        else:
            benefits.extend(["Improve content organization", "Reduce documentation sprawl", "Enhance user experience"])

        return benefits

    def _identify_challenges(self, guide1: str, guide2: str, consolidation_type: str) -> List[str]:
        """Identify challenges of consolidation."""
        challenges = []

        challenges.extend(
            ["Potential loss of specific details", "Need for careful content review", "Update of cross-references"]
        )

        if consolidation_type == "workflow_consolidation":
            challenges.append("Maintain workflow sequence integrity")

        if consolidation_type == "reference_consolidation":
            challenges.append("Preserve reference accuracy")

        return challenges

    def _find_content_type_opportunities(self, guide_contents: Dict[str, str]) -> List[ConsolidationOpportunity]:
        """Find consolidation opportunities based on content type."""
        opportunities = []

        # Group guides by content type
        content_types = defaultdict(list)
        for guide_name, content in guide_contents.items():
            content_type = self._classify_content_type(content)
            content_types[content_type].append(guide_name)

        # Create opportunities for groups with multiple guides
        for content_type, guides in content_types.items():
            if len(guides) > 2:
                # Find the most comprehensive guide as target
                target_guide = max(guides, key=lambda g: len(guide_contents[g]))

                opportunity = ConsolidationOpportunity(
                    source_guides=guides,
                    target_guide=target_guide,
                    similarity_score=0.5,  # Medium similarity for type-based consolidation
                    confidence_score=0.6,
                    consolidation_type=f"{content_type}_consolidation",
                    overlap_content=[f"Content type: {content_type}"],
                    merge_strategy="type_based_consolidation",
                    estimated_effort="Medium (4-6 hours)",
                    risk_level="Medium",
                    benefits=[
                        f"Consolidate {content_type} documentation",
                        "Improve content organization",
                        "Reduce fragmentation",
                    ],
                    challenges=[
                        "Maintain content specificity",
                        "Preserve unique information",
                        "Update cross-references",
                    ],
                    created_at=datetime.now(),
                )
                opportunities.append(opportunity)

        return opportunities

    def _classify_content_type(self, content: str) -> str:
        """Classify content by type."""
        content_lower = content.lower()

        if any(word in content_lower for word in ["workflow", "process", "procedure"]):
            return "workflow"
        elif any(word in content_lower for word in ["reference", "api", "schema"]):
            return "reference"
        elif any(word in content_lower for word in ["best practice", "guideline", "recommendation"]):
            return "best_practice"
        elif any(word in content_lower for word in ["guide", "how-to", "tutorial"]):
            return "guide"
        else:
            return "general"

    def _find_small_guide_opportunities(self, guide_contents: Dict[str, str]) -> List[ConsolidationOpportunity]:
        """Find consolidation opportunities for small guides."""
        opportunities = []

        # Find small guides (less than 200 lines)
        small_guides = [name for name, content in guide_contents.items() if len(content.split("\n")) < 200]

        if len(small_guides) > 3:
            # Group small guides by content similarity
            groups = self._group_similar_guides(small_guides, guide_contents)

            for group in groups:
                if len(group) > 1:
                    target_guide = max(group, key=lambda g: len(guide_contents[g]))

                    opportunity = ConsolidationOpportunity(
                        source_guides=group,
                        target_guide=target_guide,
                        similarity_score=0.4,
                        confidence_score=0.7,
                        consolidation_type="small_guide_consolidation",
                        overlap_content=["Small guide consolidation"],
                        merge_strategy="content_merging",
                        estimated_effort="Low (2-3 hours)",
                        risk_level="Low",
                        benefits=[
                            "Reduce documentation fragmentation",
                            "Improve content discoverability",
                            "Create more comprehensive guides",
                        ],
                        challenges=["Maintain logical organization", "Preserve unique information"],
                        created_at=datetime.now(),
                    )
                    opportunities.append(opportunity)

        return opportunities

    def _group_similar_guides(self, guides: List[str], guide_contents: Dict[str, str]) -> List[List[str]]:
        """Group guides by similarity."""
        groups = []
        used_guides = set()

        for guide1 in guides:
            if guide1 in used_guides:
                continue

            group = [guide1]
            used_guides.add(guide1)

            for guide2 in guides:
                if guide2 in used_guides:
                    continue

                similarity = self._calculate_content_similarity(guide_contents[guide1], guide_contents[guide2])

                if similarity > 0.3:  # Lower threshold for small guides
                    group.append(guide2)
                    used_guides.add(guide2)

            if len(group) > 1:
                groups.append(group)

        return groups

    def _generate_analysis_result(
        self,
        opportunities: List[ConsolidationOpportunity],
        similarity_matrix: Dict[str, Dict[str, float]],
        start_time: float,
    ) -> ConsolidationAnalysis:
        """Generate consolidation analysis result."""
        total_opportunities = len(opportunities)

        # Count by confidence level
        high_confidence = sum(1 for o in opportunities if o.confidence_score >= 0.8)
        medium_confidence = sum(1 for o in opportunities if 0.6 <= o.confidence_score < 0.8)
        low_confidence = sum(1 for o in opportunities if o.confidence_score < 0.6)

        # Group opportunities by type
        opportunities_by_type = defaultdict(list)
        for opportunity in opportunities:
            opportunities_by_type[opportunity.consolidation_type].append(opportunity)

        # Generate recommendations
        recommendations = self._generate_recommendations(opportunities)

        analysis_duration = time.time() - start_time

        return ConsolidationAnalysis(
            total_opportunities=total_opportunities,
            high_confidence_opportunities=high_confidence,
            medium_confidence_opportunities=medium_confidence,
            low_confidence_opportunities=low_confidence,
            opportunities_by_type=dict(opportunities_by_type),
            similarity_matrix=similarity_matrix,
            consolidation_recommendations=recommendations,
            analysis_timestamp=datetime.now(),
            analysis_duration_seconds=analysis_duration,
        )

    def _generate_recommendations(self, opportunities: List[ConsolidationOpportunity]) -> List[Dict[str, Any]]:
        """Generate consolidation recommendations."""
        recommendations = []

        # High confidence recommendations
        high_confidence = [o for o in opportunities if o.confidence_score >= 0.8]
        if high_confidence:
            recommendations.append(
                {
                    "type": "high_confidence_consolidation",
                    "count": len(high_confidence),
                    "description": f"Found {len(high_confidence)} high-confidence consolidation opportunities",
                    "priority": "high",
                    "opportunities": [o.source_guides for o in high_confidence[:5]],
                }
            )

        # Duplicate content recommendations
        duplicates = [o for o in opportunities if o.consolidation_type == "duplicate_content"]
        if duplicates:
            recommendations.append(
                {
                    "type": "duplicate_content_removal",
                    "count": len(duplicates),
                    "description": f"Found {len(duplicates)} duplicate content opportunities",
                    "priority": "high",
                    "opportunities": [o.source_guides for o in duplicates[:5]],
                }
            )

        # Small guide consolidation
        small_guides = [o for o in opportunities if o.consolidation_type == "small_guide_consolidation"]
        if small_guides:
            recommendations.append(
                {
                    "type": "small_guide_consolidation",
                    "count": len(small_guides),
                    "description": f"Found {len(small_guides)} small guide consolidation opportunities",
                    "priority": "medium",
                    "opportunities": [o.source_guides for o in small_guides[:5]],
                }
            )

        return recommendations

    def _store_consolidation_results(
        self, analysis_result: ConsolidationAnalysis, opportunities: List[ConsolidationOpportunity]
    ):
        """Store consolidation results in SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            # Store main consolidation run
            cursor = conn.execute(
                """
                INSERT INTO consolidation_runs
                (timestamp, total_opportunities, high_confidence_count, medium_confidence_count,
                 low_confidence_count, analysis_duration, results_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    analysis_result.analysis_timestamp.isoformat(),
                    analysis_result.total_opportunities,
                    analysis_result.high_confidence_opportunities,
                    analysis_result.medium_confidence_opportunities,
                    analysis_result.low_confidence_opportunities,
                    analysis_result.analysis_duration_seconds,
                    json.dumps(asdict(analysis_result), cls=CustomJSONEncoder),
                ),
            )
            run_id = cursor.lastrowid

            # Store individual opportunities
            for opportunity in opportunities:
                conn.execute(
                    """
                    INSERT INTO consolidation_opportunities
                    (run_id, source_guides, target_guide, similarity_score, confidence_score,
                     consolidation_type, overlap_content, merge_strategy, estimated_effort,
                     risk_level, benefits, challenges, opportunity_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        run_id,
                        json.dumps(opportunity.source_guides),
                        opportunity.target_guide,
                        opportunity.similarity_score,
                        opportunity.confidence_score,
                        opportunity.consolidation_type,
                        json.dumps(opportunity.overlap_content),
                        opportunity.merge_strategy,
                        opportunity.estimated_effort,
                        opportunity.risk_level,
                        json.dumps(opportunity.benefits),
                        json.dumps(opportunity.challenges),
                        json.dumps(asdict(opportunity), cls=CustomJSONEncoder),
                    ),
                )

    def _save_consolidation_results(
        self, analysis_result: ConsolidationAnalysis, opportunities: List[ConsolidationOpportunity]
    ):
        """Save consolidation results to JSON files."""
        # Save main analysis result
        analysis_file = self.output_dir / "consolidation_analysis.json"
        with open(analysis_file, "w") as f:
            json.dump(asdict(analysis_result), f, indent=2, cls=CustomJSONEncoder)

        # Save individual opportunities
        opportunities_file = self.output_dir / "consolidation_opportunities.json"
        with open(opportunities_file, "w") as f:
            json.dump([asdict(opp) for opp in opportunities], f, indent=2, cls=CustomJSONEncoder)

        # Generate summary report
        self._generate_summary_report(analysis_result, opportunities)

    def _generate_summary_report(
        self, analysis_result: ConsolidationAnalysis, opportunities: List[ConsolidationOpportunity]
    ):
        """Generate a human-readable summary report."""
        report_file = self.output_dir / "consolidation_summary.md"

        with open(report_file, "w") as f:
            f.write("# AI-Powered Consolidation Analysis Summary\n\n")
            f.write(f"**Analysis Date:** {analysis_result.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Analysis Duration:** {analysis_result.analysis_duration_seconds:.2f} seconds\n\n")

            f.write("## Overview\n\n")
            f.write(f"- **Total Opportunities:** {analysis_result.total_opportunities}\n")
            f.write(f"- **High Confidence:** {analysis_result.high_confidence_opportunities}\n")
            f.write(f"- **Medium Confidence:** {analysis_result.medium_confidence_opportunities}\n")
            f.write(f"- **Low Confidence:** {analysis_result.low_confidence_opportunities}\n\n")

            f.write("## Opportunities by Type\n\n")
            for opp_type, opps in analysis_result.opportunities_by_type.items():
                f.write(f"- **{opp_type}:** {len(opps)} opportunities\n")
            f.write("\n")

            f.write("## Top Recommendations\n\n")
            for i, rec in enumerate(analysis_result.consolidation_recommendations[:5], 1):
                f.write(f"{i}. **{rec['type']}:** {rec['description']} (Priority: {rec['priority']})\n")
            f.write("\n")

            f.write("## High-Confidence Opportunities\n\n")
            high_conf_opps = [o for o in opportunities if o.confidence_score >= 0.8]
            for i, opp in enumerate(high_conf_opps[:10], 1):
                f.write(f"{i}. **{opp.consolidation_type}:** {opp.source_guides[0]} + {opp.source_guides[1]} ")
                f.write(f"(Confidence: {opp.confidence_score:.2f}, Risk: {opp.risk_level})\n")
                f.write(f"   - Strategy: {opp.merge_strategy}\n")
                f.write(f"   - Effort: {opp.estimated_effort}\n")
                f.write(f"   - Benefits: {', '.join(opp.benefits[:2])}\n\n")


def main():
    """Main entry point for the AI consolidation system."""
    parser = argparse.ArgumentParser(description="AI-powered documentation consolidation analysis")
    parser.add_argument("--guides-dir", default="400_guides", help="Directory containing guides")
    parser.add_argument("--output-dir", default="artifacts/consolidation", help="Output directory for results")
    parser.add_argument("--analyze-consolidation", action="store_true", help="Run full consolidation analysis")
    parser.add_argument("--nlp-techniques", action="store_true", help="Use advanced NLP techniques")
    parser.add_argument("--content-similarity", action="store_true", help="Enable content similarity analysis")
    parser.add_argument("--confidence-scoring", action="store_true", help="Enable confidence scoring")

    args = parser.parse_args()

    # Initialize consolidation system
    consolidation_system = AIConsolidationSystem(args.guides_dir, args.output_dir)

    if args.analyze_consolidation:
        print("🤖 Starting AI-powered consolidation analysis...")
        result = consolidation_system.analyze_consolidation_opportunities()
        print(f"📊 Consolidation results saved to: {consolidation_system.output_dir}")
        return result

    else:
        print("🤖 Running consolidation analysis...")
        result = consolidation_system.analyze_consolidation_opportunities()
        return result


if __name__ == "__main__":
    main()
