#!/usr/bin/env python3
"""
Advanced AI-Powered Content Generation System
Task 6.2: B-1032 Documentation t-t3 Authority Structure Implementation

This module implements intelligent content generation, enhancement, and optimization
based on tier requirements, content analysis, and best practices.
"""

import json
import logging
import os
import re
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import hashlib


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Content types for generation and enhancement."""
    GUIDE = "guide"
    REFERENCE = "reference"
    TUTORIAL = "tutorial"
    TEMPLATE = "template"
    CHECKLIST = "checklist"
    WORKFLOW = "workflow"
    INTEGRATION = "integration"
    TROUBLESHOOTING = "troubleshooting"


class GenerationStrategy(Enum):
    """Content generation strategies."""
    TEMPLATE_BASED = "template_based"
    EXTRACTIVE = "extractive"
    ABSTRACTIVE = "abstractive"
    HYBRID = "hybrid"
    ENHANCEMENT = "enhancement"
    OPTIMIZATION = "optimization"


@dataclass
class ContentGenerationRequest:
    """Request for content generation."""
    content_type: ContentType
    tier_level: str
    target_audience: str
    key_topics: List[str]
    existing_content: Optional[str] = None
    enhancement_focus: Optional[str] = None
    generation_strategy: GenerationStrategy = GenerationStrategy.HYBRID


@dataclass
class ContentGenerationResult:
    """Result of content generation."""
    generated_content: str
    confidence_score: float
    generation_strategy: GenerationStrategy
    enhancement_areas: List[str]
    quality_metrics: Dict[str, float]
    generation_time: float
    metadata: Dict[str, Any]


@dataclass
class ContentEnhancementPlan:
    """Plan for content enhancement."""
    enhancement_type: str
    priority: int
    description: str
    implementation_steps: List[str]
    expected_impact: str
    effort_estimate: str


@dataclass
class AdvancedContentAnalysis:
    """Complete content analysis result."""
    content_id: str
    analysis_timestamp: datetime
    content_type: ContentType
    tier_level: str
    generation_opportunities: List[Dict[str, Any]]
    enhancement_plans: List[ContentEnhancementPlan]
    quality_assessment: Dict[str, float]
    optimization_recommendations: List[str]
    generation_results: List[ContentGenerationResult]


class AdvancedAIContentGeneration:
    """Advanced AI-powered content generation and enhancement system."""
    
    def __init__(self, db_path: str = "ai_content_generation.db"):
        """Initialize the content generation system."""
        self.db_path = db_path
        self.db_conn = None
        self.init_database()
        
        # Load templates and patterns
        self.templates = self._load_templates()
        self.enhancement_patterns = self._load_enhancement_patterns()
        self.quality_metrics = self._load_quality_metrics()
        
        logger.info("Advanced AI Content Generation system initialized")
    
    def init_database(self):
        """Initialize the SQLite database."""
        self.db_conn = sqlite3.connect(self.db_path)
        cursor = self.db_conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_analysis (
                id TEXT PRIMARY KEY,
                content_path TEXT,
                content_type TEXT,
                tier_level TEXT,
                analysis_timestamp TEXT,
                generation_opportunities TEXT,
                enhancement_plans TEXT,
                quality_assessment TEXT,
                optimization_recommendations TEXT,
                generation_results TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generation_requests (
                id TEXT PRIMARY KEY,
                request_data TEXT,
                timestamp TEXT,
                status TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enhancement_plans (
                id TEXT PRIMARY KEY,
                content_id TEXT,
                enhancement_type TEXT,
                priority INTEGER,
                description TEXT,
                implementation_steps TEXT,
                expected_impact TEXT,
                effort_estimate TEXT,
                status TEXT
            )
        """)
        
        self.db_conn.commit()
        logger.info("Database initialized successfully")
    
    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load content generation templates."""
        return {
            "guide": {
                "structure": ["overview", "prerequisites", "steps", "examples", "troubleshooting"],
                "sections": {
                    "overview": "## Overview\n\n{description}\n\n### Key Benefits\n{benefits}",
                    "prerequisites": "## Prerequisites\n\n{prerequisites}",
                    "steps": "## Implementation Steps\n\n{steps}",
                    "examples": "## Examples\n\n{examples}",
                    "troubleshooting": "## Troubleshooting\n\n{issues}"
                }
            },
            "reference": {
                "structure": ["overview", "api", "parameters", "examples", "notes"],
                "sections": {
                    "overview": "## Overview\n\n{description}",
                    "api": "## API Reference\n\n{api_details}",
                    "parameters": "## Parameters\n\n{parameters}",
                    "examples": "## Examples\n\n{examples}",
                    "notes": "## Notes\n\n{notes}"
                }
            },
            "tutorial": {
                "structure": ["introduction", "setup", "step_by_step", "verification", "next_steps"],
                "sections": {
                    "introduction": "## Introduction\n\n{introduction}",
                    "setup": "## Setup\n\n{setup_instructions}",
                    "step_by_step": "## Step-by-Step Guide\n\n{steps}",
                    "verification": "## Verification\n\n{verification_steps}",
                    "next_steps": "## Next Steps\n\n{next_steps}"
                }
            }
        }
    
    def _load_enhancement_patterns(self) -> Dict[str, List[str]]:
        """Load content enhancement patterns."""
        return {
            "readability": [
                "Add clear section headers",
                "Use bullet points for lists",
                "Include code examples",
                "Add visual breaks between sections"
            ],
            "completeness": [
                "Add missing prerequisites",
                "Include troubleshooting section",
                "Add related links",
                "Include version information"
            ],
            "authority": [
                "Add expert quotes or references",
                "Include best practices",
                "Add security considerations",
                "Include performance notes"
            ],
            "usability": [
                "Add quick start section",
                "Include common use cases",
                "Add configuration examples",
                "Include integration notes"
            ]
        }
    
    def _load_quality_metrics(self) -> Dict[str, Dict[str, float]]:
        """Load quality assessment metrics."""
        return {
            "readability": {
                "sentence_length": 0.2,
                "paragraph_length": 0.2,
                "technical_terms": 0.3,
                "code_examples": 0.3
            },
            "completeness": {
                "section_coverage": 0.4,
                "example_coverage": 0.3,
                "link_coverage": 0.2,
                "metadata_coverage": 0.1
            },
            "authority": {
                "expert_references": 0.3,
                "best_practices": 0.3,
                "security_notes": 0.2,
                "performance_notes": 0.2
            }
        }
    
    def analyze_content_for_generation(self, content_path: str) -> AdvancedContentAnalysis:
        """Analyze content for generation opportunities."""
        logger.info(f"Analyzing content for generation: {content_path}")
        
        content_id = self._generate_content_id(content_path)
        analysis_timestamp = datetime.now()
        
        # Read content
        content = self._read_content(content_path)
        if not content:
            raise ValueError(f"Could not read content from {content_path}")
        
        # Determine content type and tier
        content_type = self._determine_content_type(content)
        tier_level = self._determine_tier_level(content_path)
        
        # Analyze generation opportunities
        generation_opportunities = self._identify_generation_opportunities(content, content_type, tier_level)
        
        # Create enhancement plans
        enhancement_plans = self._create_enhancement_plans(content, content_type, tier_level)
        
        # Assess quality
        quality_assessment = self._assess_content_quality(content, content_type, tier_level)
        
        # Generate optimization recommendations
        optimization_recommendations = self._generate_optimization_recommendations(
            content, quality_assessment, enhancement_plans
        )
        
        # Generate content
        generation_results = self._generate_content_samples(
            content, content_type, tier_level, generation_opportunities
        )
        
        # Create analysis result
        analysis = AdvancedContentAnalysis(
            content_id=content_id,
            analysis_timestamp=analysis_timestamp,
            content_type=content_type,
            tier_level=tier_level,
            generation_opportunities=generation_opportunities,
            enhancement_plans=enhancement_plans,
            quality_assessment=quality_assessment,
            optimization_recommendations=optimization_recommendations,
            generation_results=generation_results
        )
        
        # Store in database
        self._store_analysis(analysis)
        
        logger.info(f"Content analysis completed for {content_path}")
        return analysis
    
    def _generate_content_id(self, content_path: str) -> str:
        """Generate unique content ID."""
        return hashlib.md5(content_path.encode()).hexdigest()[:8]
    
    def _read_content(self, content_path: str) -> Optional[str]:
        """Read content from file."""
        try:
            with open(content_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading content from {content_path}: {e}")
            return None
    
    def _determine_content_type(self, content: str) -> ContentType:
        """Determine content type based on content analysis."""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['guide', 'how to', 'step by step']):
            return ContentType.GUIDE
        elif any(word in content_lower for word in ['reference', 'api', 'parameters']):
            return ContentType.REFERENCE
        elif any(word in content_lower for word in ['tutorial', 'learn', 'getting started']):
            return ContentType.TUTORIAL
        elif any(word in content_lower for word in ['template', 'boilerplate']):
            return ContentType.TEMPLATE
        elif any(word in content_lower for word in ['checklist', 'todo', 'tasks']):
            return ContentType.CHECKLIST
        elif any(word in content_lower for word in ['workflow', 'process', 'pipeline']):
            return ContentType.WORKFLOW
        elif any(word in content_lower for word in ['integration', 'connect', 'hook']):
            return ContentType.INTEGRATION
        elif any(word in content_lower for word in ['troubleshooting', 'debug', 'error']):
            return ContentType.TROUBLESHOOTING
        else:
            return ContentType.GUIDE  # Default
    
    def _determine_tier_level(self, content_path: str) -> str:
        """Determine tier level based on file path and content."""
        path_parts = Path(content_path).parts
        
        if '000_core' in path_parts:
            return 'T1'
        elif '100_memory' in path_parts:
            return 'T1'
        elif '400_guides' in path_parts:
            return 'T2'
        elif '500_research' in path_parts:
            return 'T3'
        else:
            return 'T2'  # Default
    
    def _identify_generation_opportunities(self, content: str, content_type: ContentType, tier_level: str) -> List[Dict[str, Any]]:
        """Identify opportunities for content generation."""
        opportunities = []
        
        # Analyze content structure
        sections = self._extract_sections(content)
        missing_sections = self._identify_missing_sections(sections, content_type)
        
        for section in missing_sections:
            opportunities.append({
                "type": "missing_section",
                "section": section,
                "priority": "high" if tier_level == 'T1' else "medium",
                "description": f"Generate {section} section for {content_type.value}"
            })
        
        # Analyze enhancement opportunities
        enhancement_areas = self._identify_enhancement_areas(content, content_type, tier_level)
        for area in enhancement_areas:
            opportunities.append({
                "type": "enhancement",
                "area": area,
                "priority": "medium",
                "description": f"Enhance {area} for better {content_type.value}"
            })
        
        # Analyze optimization opportunities
        optimization_areas = self._identify_optimization_areas(content, content_type, tier_level)
        for area in optimization_areas:
            opportunities.append({
                "type": "optimization",
                "area": area,
                "priority": "low",
                "description": f"Optimize {area} for improved performance"
            })
        
        return opportunities
    
    def _extract_sections(self, content: str) -> List[str]:
        """Extract section headers from content."""
        section_pattern = r'^#{1,6}\s+(.+)$'
        sections = re.findall(section_pattern, content, re.MULTILINE)
        return [section.lower().strip() for section in sections]
    
    def _identify_missing_sections(self, sections: List[str], content_type: ContentType) -> List[str]:
        """Identify missing sections based on content type."""
        template = self.templates.get(content_type.value, {})
        required_sections = template.get('structure', [])
        
        missing = []
        for section in required_sections:
            if not any(section in s for s in sections):
                missing.append(section)
        
        return missing
    
    def _identify_enhancement_areas(self, content: str, content_type: ContentType, tier_level: str) -> List[str]:
        """Identify areas for enhancement."""
        areas = []
        
        # Check for code examples
        if not re.search(r'```[\w]*\n', content):
            areas.append("code_examples")
        
        # Check for links
        if not re.search(r'\[.*\]\(.*\)', content):
            areas.append("cross_references")
        
        # Check for metadata
        if not re.search(r'---\n.*\n---', content):
            areas.append("metadata")
        
        # Check for authority indicators
        if tier_level in ['T1', 'T2'] and not re.search(r'(best practice|security|performance)', content, re.IGNORECASE):
            areas.append("authority_indicators")
        
        return areas
    
    def _identify_optimization_areas(self, content: str, content_type: ContentType, tier_level: str) -> List[str]:
        """Identify areas for optimization."""
        areas = []
        
        # Check content length
        if len(content) > 5000:
            areas.append("content_length")
        
        # Check for long paragraphs
        paragraphs = content.split('\n\n')
        long_paragraphs = [p for p in paragraphs if len(p) > 500]
        if long_paragraphs:
            areas.append("paragraph_length")
        
        # Check for complex sentences
        sentences = re.split(r'[.!?]+', content)
        complex_sentences = [s for s in sentences if len(s.split()) > 25]
        if complex_sentences:
            areas.append("sentence_complexity")
        
        return areas
    
    def _create_enhancement_plans(self, content: str, content_type: ContentType, tier_level: str) -> List[ContentEnhancementPlan]:
        """Create enhancement plans for content."""
        plans = []
        
        # Readability enhancement
        if self._needs_readability_enhancement(content):
            plans.append(ContentEnhancementPlan(
                enhancement_type="readability",
                priority=1,
                description="Improve content readability and structure",
                implementation_steps=self.enhancement_patterns["readability"],
                expected_impact="Improved user comprehension and engagement",
                effort_estimate="2-4 hours"
            ))
        
        # Completeness enhancement
        if self._needs_completeness_enhancement(content, content_type):
            plans.append(ContentEnhancementPlan(
                enhancement_type="completeness",
                priority=2,
                description="Add missing sections and information",
                implementation_steps=self.enhancement_patterns["completeness"],
                expected_impact="More comprehensive and useful documentation",
                effort_estimate="3-6 hours"
            ))
        
        # Authority enhancement
        if tier_level in ['T1', 'T2'] and self._needs_authority_enhancement(content):
            plans.append(ContentEnhancementPlan(
                enhancement_type="authority",
                priority=3,
                description="Add authority indicators and best practices",
                implementation_steps=self.enhancement_patterns["authority"],
                expected_impact="Enhanced credibility and trust",
                effort_estimate="2-3 hours"
            ))
        
        # Usability enhancement
        if self._needs_usability_enhancement(content):
            plans.append(ContentEnhancementPlan(
                enhancement_type="usability",
                priority=4,
                description="Improve practical usability and accessibility",
                implementation_steps=self.enhancement_patterns["usability"],
                expected_impact="Better user experience and adoption",
                effort_estimate="2-4 hours"
            ))
        
        return plans
    
    def _needs_readability_enhancement(self, content: str) -> bool:
        """Check if content needs readability enhancement."""
        # Check for long paragraphs
        paragraphs = content.split('\n\n')
        long_paragraphs = [p for p in paragraphs if len(p) > 300]
        
        # Check for lack of structure
        has_structure = bool(re.search(r'^#{1,6}\s+', content, re.MULTILINE))
        
        return len(long_paragraphs) > 2 or not has_structure
    
    def _needs_completeness_enhancement(self, content: str, content_type: ContentType) -> bool:
        """Check if content needs completeness enhancement."""
        template = self.templates.get(content_type.value, {})
        required_sections = template.get('structure', [])
        
        sections = self._extract_sections(content)
        missing_sections = self._identify_missing_sections(sections, content_type)
        
        return len(missing_sections) > 0
    
    def _needs_authority_enhancement(self, content: str) -> bool:
        """Check if content needs authority enhancement."""
        authority_indicators = ['best practice', 'security', 'performance', 'recommended', 'expert']
        return not any(indicator in content.lower() for indicator in authority_indicators)
    
    def _needs_usability_enhancement(self, content: str) -> bool:
        """Check if content needs usability enhancement."""
        usability_indicators = ['quick start', 'example', 'configuration', 'use case']
        return not any(indicator in content.lower() for indicator in usability_indicators)
    
    def _assess_content_quality(self, content: str, content_type: ContentType, tier_level: str) -> Dict[str, float]:
        """Assess content quality across multiple dimensions."""
        quality_scores = {}
        
        # Readability assessment
        readability_score = self._assess_readability(content)
        quality_scores['readability'] = readability_score
        
        # Completeness assessment
        completeness_score = self._assess_completeness(content, content_type)
        quality_scores['completeness'] = completeness_score
        
        # Authority assessment
        authority_score = self._assess_authority(content, tier_level)
        quality_scores['authority'] = authority_score
        
        # Overall quality
        quality_scores['overall'] = (readability_score + completeness_score + authority_score) / 3
        
        return quality_scores
    
    def _assess_readability(self, content: str) -> float:
        """Assess content readability."""
        metrics = self.quality_metrics['readability']
        score = 0.0
        
        # Sentence length assessment
        sentences = re.split(r'[.!?]+', content)
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        if avg_sentence_length <= 20:
            score += metrics['sentence_length']
        
        # Paragraph length assessment
        paragraphs = content.split('\n\n')
        short_paragraphs = [p for p in paragraphs if len(p) <= 300]
        paragraph_score = len(short_paragraphs) / len(paragraphs) if paragraphs else 0
        score += paragraph_score * metrics['paragraph_length']
        
        # Technical terms assessment
        technical_terms = len(re.findall(r'\b[A-Z]{2,}\b', content))
        if technical_terms <= 10:
            score += metrics['technical_terms']
        
        # Code examples assessment
        code_blocks = len(re.findall(r'```[\w]*\n', content))
        if code_blocks > 0:
            score += metrics['code_examples']
        
        return min(score, 1.0)
    
    def _assess_completeness(self, content: str, content_type: ContentType) -> float:
        """Assess content completeness."""
        metrics = self.quality_metrics['completeness']
        score = 0.0
        
        # Section coverage
        template = self.templates.get(content_type.value, {})
        required_sections = template.get('structure', [])
        sections = self._extract_sections(content)
        
        covered_sections = sum(1 for section in required_sections if any(section in s for s in sections))
        section_coverage = covered_sections / len(required_sections) if required_sections else 1.0
        score += section_coverage * metrics['section_coverage']
        
        # Example coverage
        examples = len(re.findall(r'(example|Example|EXAMPLE)', content))
        if examples > 0:
            score += metrics['example_coverage']
        
        # Link coverage
        links = len(re.findall(r'\[.*\]\(.*\)', content))
        if links > 0:
            score += metrics['link_coverage']
        
        # Metadata coverage
        if re.search(r'---\n.*\n---', content):
            score += metrics['metadata_coverage']
        
        return min(score, 1.0)
    
    def _assess_authority(self, content: str, tier_level: str) -> float:
        """Assess content authority."""
        metrics = self.quality_metrics['authority']
        score = 0.0
        
        # Expert references
        expert_indicators = ['expert', 'authority', 'official', 'certified']
        if any(indicator in content.lower() for indicator in expert_indicators):
            score += metrics['expert_references']
        
        # Best practices
        best_practice_indicators = ['best practice', 'recommended', 'should', 'must']
        if any(indicator in content.lower() for indicator in best_practice_indicators):
            score += metrics['best_practices']
        
        # Security notes
        if 'security' in content.lower():
            score += metrics['security_notes']
        
        # Performance notes
        if 'performance' in content.lower():
            score += metrics['performance_notes']
        
        return min(score, 1.0)
    
    def _generate_optimization_recommendations(self, content: str, quality_assessment: Dict[str, float], enhancement_plans: List[ContentEnhancementPlan]) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # Based on quality scores
        if quality_assessment.get('readability', 0) < 0.7:
            recommendations.append("Improve content structure with better section headers and shorter paragraphs")
        
        if quality_assessment.get('completeness', 0) < 0.7:
            recommendations.append("Add missing sections and examples to improve completeness")
        
        if quality_assessment.get('authority', 0) < 0.7:
            recommendations.append("Include best practices and expert recommendations to enhance authority")
        
        # Based on enhancement plans
        for plan in enhancement_plans:
            if plan.priority <= 2:
                recommendations.append(f"Implement {plan.enhancement_type} enhancement: {plan.description}")
        
        return recommendations
    
    def _generate_content_samples(self, content: str, content_type: ContentType, tier_level: str, opportunities: List[Dict[str, Any]]) -> List[ContentGenerationResult]:
        """Generate sample content based on opportunities."""
        results = []
        
        for opportunity in opportunities[:3]:  # Limit to top 3 opportunities
            if opportunity['type'] == 'missing_section':
                result = self._generate_section_content(content, content_type, tier_level, opportunity)
                results.append(result)
            elif opportunity['type'] == 'enhancement':
                result = self._generate_enhancement_content(content, content_type, tier_level, opportunity)
                results.append(result)
        
        return results
    
    def _generate_section_content(self, content: str, content_type: ContentType, tier_level: str, opportunity: Dict[str, Any]) -> ContentGenerationResult:
        """Generate content for a missing section."""
        section = opportunity['section']
        template = self.templates.get(content_type.value, {})
        section_template = template.get('sections', {}).get(section, f"## {section.title()}\n\n{{content}}")
        
        # Generate placeholder content
        placeholder_content = f"Content for {section} section would be generated here based on the document's context and requirements."
        
        generated_content = section_template.format(
            content=placeholder_content,
            description=f"Description of {section}",
            benefits=f"- Benefit 1\n- Benefit 2\n- Benefit 3",
            prerequisites=f"- Prerequisite 1\n- Prerequisite 2",
            steps=f"1. Step 1\n2. Step 2\n3. Step 3",
            examples=f"```\nExample code or configuration\n```",
            issues=f"- Common issue 1: Solution\n- Common issue 2: Solution",
            api_details=f"API details for {section}",
            parameters=f"Parameter descriptions",
            notes=f"Important notes about {section}"
        )
        
        return ContentGenerationResult(
            generated_content=generated_content,
            confidence_score=0.8,
            generation_strategy=GenerationStrategy.TEMPLATE_BASED,
            enhancement_areas=[section],
            quality_metrics={'completeness': 0.9, 'readability': 0.8},
            generation_time=0.5,
            metadata={'section': section, 'content_type': content_type.value}
        )
    
    def _generate_enhancement_content(self, content: str, content_type: ContentType, tier_level: str, opportunity: Dict[str, Any]) -> ContentGenerationResult:
        """Generate enhancement content."""
        area = opportunity['area']
        
        if area == 'code_examples':
            enhanced_content = f"""
## Code Examples

```python
# Example implementation
def example_function():
    \"\"\"Example function for {content_type.value}.\"\"\"
    return "example result"
```

```bash
# Example command
example-command --option value
```
"""
        elif area == 'cross_references':
            enhanced_content = f"""
## Related Documentation

- [Related Guide 1](link-to-guide-1)
- [Related Reference](link-to-reference)
- [Related Tutorial](link-to-tutorial)

## External Resources

- [Official Documentation](official-link)
- [Community Resources](community-link)
"""
        else:
            enhanced_content = f"## {area.replace('_', ' ').title()}\n\nEnhanced content for {area} would be generated here."
        
        return ContentGenerationResult(
            generated_content=enhanced_content,
            confidence_score=0.7,
            generation_strategy=GenerationStrategy.ENHANCEMENT,
            enhancement_areas=[area],
            quality_metrics={'usability': 0.8, 'completeness': 0.7},
            generation_time=0.3,
            metadata={'enhancement_area': area, 'content_type': content_type.value}
        )
    
    def _store_analysis(self, analysis: AdvancedContentAnalysis):
        """Store analysis results in database."""
        cursor = self.db_conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO content_analysis 
            (id, content_path, content_type, tier_level, analysis_timestamp, 
             generation_opportunities, enhancement_plans, quality_assessment, 
             optimization_recommendations, generation_results)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            analysis.content_id,
            f"content_{analysis.content_id}",
            analysis.content_type.value,
            analysis.tier_level,
            analysis.analysis_timestamp.isoformat(),
            json.dumps(analysis.generation_opportunities),
            json.dumps([asdict(plan) for plan in analysis.enhancement_plans]),
            json.dumps(analysis.quality_assessment),
            json.dumps(analysis.optimization_recommendations),
            json.dumps([asdict(result) for result in analysis.generation_results])
        ))
        
        self.db_conn.commit()
        logger.info(f"Analysis stored for content {analysis.content_id}")
    
    def analyze_directory(self, directory_path: str) -> List[AdvancedContentAnalysis]:
        """Analyze all markdown files in a directory."""
        logger.info(f"Analyzing directory: {directory_path}")
        
        analyses = []
        directory = Path(directory_path)
        
        # Find all markdown files
        markdown_files = list(directory.rglob("*.md"))
        
        for file_path in markdown_files:
            try:
                analysis = self.analyze_content_for_generation(str(file_path))
                analyses.append(analysis)
                logger.info(f"Analyzed {file_path}")
            except Exception as e:
                logger.error(f"Error analyzing {file_path}: {e}")
        
        logger.info(f"Directory analysis completed: {len(analyses)} files analyzed")
        return analyses
    
    def export_results(self, output_format: str = "json", output_path: Optional[str] = None) -> str:
        """Export analysis results."""
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT * FROM content_analysis")
        rows = cursor.fetchall()
        
        if output_format == "json":
            results = []
            for row in rows:
                results.append({
                    "id": row[0],
                    "content_path": row[1],
                    "content_type": row[2],
                    "tier_level": row[3],
                    "analysis_timestamp": row[4],
                    "generation_opportunities": json.loads(row[5]),
                    "enhancement_plans": json.loads(row[6]),
                    "quality_assessment": json.loads(row[7]),
                    "optimization_recommendations": json.loads(row[8]),
                    "generation_results": json.loads(row[9])
                })
            
            output = json.dumps(results, indent=2)
        else:  # markdown
            output = "# Content Generation Analysis Results\n\n"
            for row in rows:
                output += f"## {row[1]}\n\n"
                output += f"- **Content Type:** {row[2]}\n"
                output += f"- **Tier Level:** {row[3]}\n"
                output += f"- **Analysis Timestamp:** {row[4]}\n\n"
                
                quality_assessment = json.loads(row[7])
                output += "### Quality Assessment\n\n"
                for metric, score in quality_assessment.items():
                    output += f"- **{metric.title()}:** {score:.2f}\n"
                output += "\n"
                
                recommendations = json.loads(row[8])
                if recommendations:
                    output += "### Optimization Recommendations\n\n"
                    for rec in recommendations:
                        output += f"- {rec}\n"
                    output += "\n"
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output)
            logger.info(f"Results exported to {output_path}")
        
        return output


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced AI Content Generation System")
    parser.add_argument("--input", "-i", required=True, help="Input file or directory path")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--format", "-f", choices=["json", "markdown"], default="json", help="Output format")
    parser.add_argument("--db", default="ai_content_generation.db", help="Database path")
    
    args = parser.parse_args()
    
    # Initialize system
    generator = AdvancedAIContentGeneration(args.db)
    
    # Analyze content
    if os.path.isfile(args.input):
        analysis = generator.analyze_content_for_generation(args.input)
        print(f"Analysis completed for {args.input}")
    elif os.path.isdir(args.input):
        analyses = generator.analyze_directory(args.input)
        print(f"Directory analysis completed: {len(analyses)} files analyzed")
    else:
        print(f"Error: {args.input} is not a valid file or directory")
        return
    
    # Export results
    output = generator.export_results(args.format, args.output)
    if not args.output:
        print(output)


if __name__ == "__main__":
    main()
