#!/usr/bin/env python3
# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportAny=false
"""
Documentation Knowledge Graph System

This module provides DiGraph-based modeling for documentation cross-references
and knowledge mapping in the AI Dev Tasks ecosystem. It can model and analyze:

1. Documentation Hierarchy - Core guides, specialized guides, and their relationships
2. Cross-Reference Networks - How documents reference and link to each other
3. Knowledge Dependencies - Prerequisites and dependencies between documentation
4. Content Categories - Different types of content and their organization
5. Navigation Patterns - How users navigate through the documentation system
6. Documentation Health - Link validation, coverage analysis, and quality metrics

Usage:
    python documentation_knowledge_graph.py --doc-type hierarchy --analyze
    python documentation_knowledge_graph.py --doc-type cross-references --visualize
    python documentation_knowledge_graph.py --doc-type knowledge-dependencies --export
"""

import json
import re
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import networkx as nx
from networkx import DiGraph

if TYPE_CHECKING:
    from networkx import DiGraph as DiGraphType
else:
    DiGraphType = DiGraph


class DocumentationType(Enum):
    """Types of documentation relationships that can be modeled"""

    HIERARCHY = "hierarchy"
    CROSS_REFERENCES = "cross-references"
    KNOWLEDGE_DEPENDENCIES = "knowledge-dependencies"
    CONTENT_CATEGORIES = "content-categories"
    NAVIGATION_PATTERNS = "navigation-patterns"
    DOCUMENTATION_HEALTH = "documentation-health"


class DocumentNodeType(Enum):
    """Types of nodes in the documentation graph"""

    CORE_GUIDE = "core_guide"
    SPECIALIZED_GUIDE = "specialized_guide"
    WORKFLOW_DOCUMENT = "workflow_document"
    REFERENCE_DOCUMENT = "reference_document"
    TEMPLATE_DOCUMENT = "template_document"
    RESEARCH_DOCUMENT = "research_document"
    SETUP_DOCUMENT = "setup_document"
    MEMORY_DOCUMENT = "memory_document"
    CONFIGURATION_DOCUMENT = "configuration_document"
    ARCHIVE_DOCUMENT = "archive_document"


class DocumentEdgeType(Enum):
    """Types of edges in the documentation graph"""

    REFERENCES = "references"
    DEPENDS_ON = "depends_on"
    PREREQUISITE_FOR = "prerequisite_for"
    EXTENDS = "extends"
    IMPLEMENTS = "implements"
    VALIDATES = "validates"
    SUPPLEMENTS = "supplements"
    REPLACES = "replaces"
    VERSION_OF = "version_of"
    PART_OF = "part_of"
    CONTAINS = "contains"
    LINKS_TO = "links_to"
    CROSS_REFERENCES = "cross_references"
    NAVIGATES_TO = "navigates_to"
    FOLLOWS_FROM = "follows_from"
    PRECEDES = "precedes"
    FOUNDATION_FOR = "foundation_for"
    INFLUENCES = "influences"
    SUPPORTS = "supports"
    NEEDS_IMPROVEMENT = "needs_improvement"
    NEEDS_ATTENTION = "needs_attention"


@dataclass
class DocumentNode:
    """Represents a node in the documentation knowledge graph"""

    id: str
    name: str
    node_type: DocumentNodeType
    file_path: str
    description: str = ""
    tier: int = 1
    priority: int = 10
    content_type: str = ""
    last_updated: datetime = None
    word_count: int = 0
    cross_reference_count: int = 0
    metadata: dict[str, Any] = None
    tags: list[str] = None

    def __post_init__(self) -> None:
        if self.last_updated is None:
            self.last_updated: Any = datetime.now()
        if self.metadata is None:
            self.metadata: Any = {}
        if self.tags is None:
            self.tags: Any = []


@dataclass
class DocumentEdge:
    """Represents an edge in the documentation knowledge graph"""

    source: str
    target: str
    edge_type: DocumentEdgeType
    weight: float = 1.0
    strength: float = 1.0
    description: str = ""
    link_type: str = "internal"
    context: str = ""
    metadata: dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata: Any = {}


class DocumentationKnowledgeGraph:
    """DiGraph-based documentation knowledge modeling and analysis system"""

    def __init__(self, doc_type: DocumentationType) -> None:
        self.doc_type: Any = doc_type
        self.graph: DiGraphType = DiGraph()  # pyright: ignore[reportUnknownVariableType,reportMissingTypeArgument]
        self.nodes: dict[str, DocumentNode] = {}
        self.edges: list[DocumentEdge] = []
        self._build_documentation_graph()

    def _build_documentation_graph(self) -> None:
        """Build the documentation knowledge graph based on the documentation type"""
        if self.doc_type == DocumentationType.HIERARCHY:
            self._build_documentation_hierarchy()
        elif self.doc_type == DocumentationType.CROSS_REFERENCES:
            self._build_cross_reference_network()
        elif self.doc_type == DocumentationType.KNOWLEDGE_DEPENDENCIES:
            self._build_knowledge_dependencies()
        elif self.doc_type == DocumentationType.CONTENT_CATEGORIES:
            self._build_content_categories()
        elif self.doc_type == DocumentationType.NAVIGATION_PATTERNS:
            self._build_navigation_patterns()
        elif self.doc_type == DocumentationType.DOCUMENTATION_HEALTH:
            self._build_documentation_health()

    def _build_documentation_hierarchy(self) -> None:
        """Build documentation hierarchy based on tiers and importance"""
        # Core documentation (Tier 1 - Critical)
        core_docs = [
            DocumentNode(
                "memory_context",
                "Memory Context",
                DocumentNodeType.MEMORY_DOCUMENT,
                "100_memory/100_cursor-memory-context.md",
                "Memory scaffold and current state",
                tier=1,
                priority=5,
                content_type="context",
                cross_reference_count=15,
            ),
            DocumentNode(
                "backlog",
                "Backlog",
                DocumentNodeType.CORE_GUIDE,
                "000_core/000_backlog.md",
                "Priorities and dependencies",
                tier=1,
                priority=8,
                content_type="planning",
                cross_reference_count=12,
            ),
            DocumentNode(
                "system_overview",
                "System Overview",
                DocumentNodeType.CORE_GUIDE,
                "400_guides/400_03_system-overview-and-architecture.md",
                "System architecture and overview",
                tier=1,
                priority=6,
                content_type="architecture",
                cross_reference_count=20,
            ),
            DocumentNode(
                "memory_overview",
                "Memory System Overview",
                DocumentNodeType.CORE_GUIDE,
                "400_guides/400_00_memory-system-overview.md",
                "Entry point and navigation",
                tier=1,
                priority=7,
                content_type="navigation",
                cross_reference_count=18,
            ),
        ]

        # High priority guides (Tier 2)
        high_priority_docs = [
            DocumentNode(
                "development_workflow",
                "Development Workflow",
                DocumentNodeType.CORE_GUIDE,
                "400_guides/400_04_development-workflow-and-standards.md",
                "Development workflows and standards",
                tier=2,
                priority=15,
                content_type="workflow",
                cross_reference_count=16,
            ),
            DocumentNode(
                "ai_constitution",
                "AI Constitution",
                DocumentNodeType.CORE_GUIDE,
                "400_guides/400_02_governance-and-ai-constitution.md",
                "AI safety and governance",
                tier=2,
                priority=12,
                content_type="governance",
                cross_reference_count=14,
            ),
            DocumentNode(
                "documentation_playbook",
                "Documentation Playbook",
                DocumentNodeType.CORE_GUIDE,
                "400_guides/400_01_documentation-playbook.md",
                "File management rules",
                tier=2,
                priority=18,
                content_type="process",
                cross_reference_count=8,
            ),
        ]

        # Specialized guides (Tier 3)
        specialized_docs = [
            DocumentNode(
                "codebase_organization",
                "Codebase Organization",
                DocumentNodeType.SPECIALIZED_GUIDE,
                "400_guides/400_05_codebase-organization-patterns.md",
                "Code organization and patterns",
                tier=3,
                priority=25,
                content_type="patterns",
                cross_reference_count=10,
            ),
            DocumentNode(
                "dspy_frameworks",
                "DSPy Frameworks",
                DocumentNodeType.SPECIALIZED_GUIDE,
                "400_guides/400_09_ai-frameworks-dspy.md",
                "AI framework integration",
                tier=3,
                priority=22,
                content_type="integration",
                cross_reference_count=12,
            ),
            DocumentNode(
                "performance_optimization",
                "Performance Optimization",
                DocumentNodeType.SPECIALIZED_GUIDE,
                "400_guides/400_11_performance-optimization.md",
                "System optimization",
                tier=3,
                priority=28,
                content_type="optimization",
                cross_reference_count=6,
            ),
        ]

        # Workflow documents
        workflow_docs = [
            DocumentNode(
                "prd_template",
                "PRD Template",
                DocumentNodeType.TEMPLATE_DOCUMENT,
                "000_core/001_PRD_TEMPLATE.md",
                "PRD creation workflow",
                tier=4,
                priority=35,
                content_type="template",
                cross_reference_count=4,
            ),
            DocumentNode(
                "task_template",
                "Task Template",
                DocumentNodeType.TEMPLATE_DOCUMENT,
                "000_core/002_TASK-LIST_TEMPLATE.md",
                "Task generation workflow",
                tier=4,
                priority=38,
                content_type="template",
                cross_reference_count=3,
            ),
            DocumentNode(
                "execution_template",
                "Execution Template",
                DocumentNodeType.TEMPLATE_DOCUMENT,
                "000_core/003_EXECUTION_TEMPLATE.md",
                "AI execution workflow",
                tier=4,
                priority=40,
                content_type="template",
                cross_reference_count=2,
            ),
        ]

        # Add all nodes
        all_docs = core_docs + high_priority_docs + specialized_docs + workflow_docs
        for doc in all_docs:
            self._add_node(doc)

        # Define hierarchy relationships
        hierarchy_relationships = [
            # Core docs are foundational
            (
                "memory_context",
                "system_overview",
                DocumentEdgeType.FOUNDATION_FOR,
                "Memory context provides foundation for system overview",
            ),
            ("backlog", "system_overview", DocumentEdgeType.INFLUENCES, "Backlog influences system overview"),
            (
                "memory_overview",
                "system_overview",
                DocumentEdgeType.NAVIGATES_TO,
                "Memory overview navigates to system overview",
            ),
            # High priority guides extend core docs
            (
                "system_overview",
                "development_workflow",
                DocumentEdgeType.EXTENDS,
                "System overview extends to development workflow",
            ),
            (
                "system_overview",
                "ai_constitution",
                DocumentEdgeType.EXTENDS,
                "System overview extends to AI constitution",
            ),
            (
                "memory_context",
                "documentation_playbook",
                DocumentEdgeType.INFLUENCES,
                "Memory context influences documentation playbook",
            ),
            # Specialized guides depend on core and high priority
            (
                "development_workflow",
                "codebase_organization",
                DocumentEdgeType.PREREQUISITE_FOR,
                "Development workflow is prerequisite for codebase organization",
            ),
            (
                "system_overview",
                "dspy_frameworks",
                DocumentEdgeType.PREREQUISITE_FOR,
                "System overview is prerequisite for DSPy frameworks",
            ),
            (
                "development_workflow",
                "performance_optimization",
                DocumentEdgeType.PREREQUISITE_FOR,
                "Development workflow is prerequisite for performance optimization",
            ),
            # Workflow documents implement the guides
            (
                "development_workflow",
                "prd_template",
                DocumentEdgeType.IMPLEMENTS,
                "Development workflow implements PRD template",
            ),
            (
                "development_workflow",
                "task_template",
                DocumentEdgeType.IMPLEMENTS,
                "Development workflow implements task template",
            ),
            (
                "development_workflow",
                "execution_template",
                DocumentEdgeType.IMPLEMENTS,
                "Development workflow implements execution template",
            ),
        ]

        # Add edges
        for source, target, edge_type, description in hierarchy_relationships:
            self._add_edge(source, target, edge_type, description, weight=0.8)

    def _build_cross_reference_network(self) -> None:
        """Build cross-reference network based on actual document links"""
        # Documents with high cross-reference coverage
        high_coverage_docs = [
            DocumentNode(
                "context_priority_guide",
                "Context Priority Guide",
                DocumentNodeType.CORE_GUIDE,
                "400_guides/400_context-priority-guide.md",
                "Context prioritization guide",
                cross_reference_count=25,
                content_type="priority",
            ),
            DocumentNode(
                "ai_constitution",
                "AI Constitution",
                DocumentNodeType.CORE_GUIDE,
                "400_guides/400_02_governance-and-ai-constitution.md",
                "AI safety and governance",
                cross_reference_count=18,
                content_type="governance",
            ),
            DocumentNode(
                "development_workflow",
                "Development Workflow",
                DocumentNodeType.CORE_GUIDE,
                "400_guides/400_04_development-workflow-and-standards.md",
                "Development workflows",
                cross_reference_count=16,
                content_type="workflow",
            ),
        ]

        # Documents with medium cross-reference coverage
        medium_coverage_docs = [
            DocumentNode(
                "system_overview",
                "System Overview",
                DocumentNodeType.CORE_GUIDE,
                "400_guides/400_03_system-overview-and-architecture.md",
                "System architecture",
                cross_reference_count=12,
                content_type="architecture",
            ),
            DocumentNode(
                "memory_system",
                "Memory System",
                DocumentNodeType.MEMORY_DOCUMENT,
                "400_guides/400_01_memory-system-architecture.md",
                "Memory system architecture",
                cross_reference_count=10,
                content_type="memory",
            ),
            DocumentNode(
                "codebase_organization",
                "Codebase Organization",
                DocumentNodeType.SPECIALIZED_GUIDE,
                "400_guides/400_05_codebase-organization-patterns.md",
                "Code organization patterns",
                cross_reference_count=8,
                content_type="patterns",
            ),
        ]

        # Documents with low cross-reference coverage
        low_coverage_docs = [
            DocumentNode(
                "deployment_ops",
                "Deployment Operations",
                DocumentNodeType.SPECIALIZED_GUIDE,
                "400_guides/400_11_deployments-ops-and-observability.md",
                "Deployment and operations",
                cross_reference_count=3,
                content_type="operations",
            ),
            DocumentNode(
                "performance_optimization",
                "Performance Optimization",
                DocumentNodeType.SPECIALIZED_GUIDE,
                "400_guides/400_11_performance-optimization.md",
                "System optimization",
                cross_reference_count=2,
                content_type="optimization",
            ),
        ]

        # Add all nodes
        all_docs = high_coverage_docs + medium_coverage_docs + low_coverage_docs
        for doc in all_docs:
            self._add_node(doc)

        # Define cross-reference relationships
        cross_reference_links = [
            # High coverage docs reference each other
            (
                "context_priority_guide",
                "ai_constitution",
                DocumentEdgeType.CROSS_REFERENCES,
                "Context priority references AI constitution",
            ),
            (
                "context_priority_guide",
                "development_workflow",
                DocumentEdgeType.CROSS_REFERENCES,
                "Context priority references development workflow",
            ),
            (
                "ai_constitution",
                "development_workflow",
                DocumentEdgeType.CROSS_REFERENCES,
                "AI constitution references development workflow",
            ),
            # High coverage docs reference medium coverage
            (
                "context_priority_guide",
                "system_overview",
                DocumentEdgeType.CROSS_REFERENCES,
                "Context priority references system overview",
            ),
            (
                "development_workflow",
                "system_overview",
                DocumentEdgeType.CROSS_REFERENCES,
                "Development workflow references system overview",
            ),
            (
                "ai_constitution",
                "memory_system",
                DocumentEdgeType.CROSS_REFERENCES,
                "AI constitution references memory system",
            ),
            # Medium coverage docs reference each other
            (
                "system_overview",
                "memory_system",
                DocumentEdgeType.CROSS_REFERENCES,
                "System overview references memory system",
            ),
            (
                "system_overview",
                "codebase_organization",
                DocumentEdgeType.CROSS_REFERENCES,
                "System overview references codebase organization",
            ),
            (
                "memory_system",
                "codebase_organization",
                DocumentEdgeType.CROSS_REFERENCES,
                "Memory system references codebase organization",
            ),
            # Some references to low coverage docs
            (
                "development_workflow",
                "deployment_ops",
                DocumentEdgeType.CROSS_REFERENCES,
                "Development workflow references deployment ops",
            ),
            (
                "system_overview",
                "performance_optimization",
                DocumentEdgeType.CROSS_REFERENCES,
                "System overview references performance optimization",
            ),
        ]

        # Add edges
        for source, target, edge_type, description in cross_reference_links:
            self._add_edge(source, target, edge_type, description, weight=0.7)

    def _build_knowledge_dependencies(self) -> None:
        """Build knowledge dependencies showing prerequisites and learning paths"""
        # Prerequisite documents
        prerequisites = [
            DocumentNode(
                "memory_context",
                "Memory Context",
                DocumentNodeType.MEMORY_DOCUMENT,
                "100_memory/100_cursor-memory-context.md",
                "Foundation memory context",
                content_type="foundation",
            ),
            DocumentNode(
                "backlog",
                "Backlog",
                DocumentNodeType.CORE_GUIDE,
                "000_core/000_backlog.md",
                "Project priorities and dependencies",
                content_type="planning",
            ),
            DocumentNode(
                "system_overview",
                "System Overview",
                DocumentNodeType.CORE_GUIDE,
                "400_guides/400_03_system-overview-and-architecture.md",
                "System architecture foundation",
                content_type="architecture",
            ),
        ]

        # Intermediate documents
        intermediate_docs = [
            DocumentNode(
                "development_workflow",
                "Development Workflow",
                DocumentNodeType.CORE_GUIDE,
                "400_guides/400_04_development-workflow-and-standards.md",
                "Development processes",
                content_type="workflow",
            ),
            DocumentNode(
                "ai_constitution",
                "AI Constitution",
                DocumentNodeType.CORE_GUIDE,
                "400_guides/400_02_governance-and-ai-constitution.md",
                "AI safety and governance",
                content_type="governance",
            ),
            DocumentNode(
                "memory_system",
                "Memory System",
                DocumentNodeType.MEMORY_DOCUMENT,
                "400_guides/400_01_memory-system-architecture.md",
                "Memory system details",
                content_type="memory",
            ),
        ]

        # Advanced documents
        advanced_docs = [
            DocumentNode(
                "dspy_frameworks",
                "DSPy Frameworks",
                DocumentNodeType.SPECIALIZED_GUIDE,
                "400_guides/400_09_ai-frameworks-dspy.md",
                "AI framework integration",
                content_type="integration",
            ),
            DocumentNode(
                "performance_optimization",
                "Performance Optimization",
                DocumentNodeType.SPECIALIZED_GUIDE,
                "400_guides/400_11_performance-optimization.md",
                "System optimization",
                content_type="optimization",
            ),
            DocumentNode(
                "advanced_configurations",
                "Advanced Configurations",
                DocumentNodeType.SPECIALIZED_GUIDE,
                "400_guides/400_12_advanced-configurations.md",
                "Advanced setup and configuration",
                content_type="configuration",
            ),
        ]

        # Add all nodes
        all_docs = prerequisites + intermediate_docs + advanced_docs
        for doc in all_docs:
            self._add_node(doc)

        # Define knowledge dependencies
        knowledge_dependencies = [
            # Prerequisites for intermediate docs
            (
                "memory_context",
                "development_workflow",
                DocumentEdgeType.PREREQUISITE_FOR,
                "Memory context is prerequisite for development workflow",
            ),
            (
                "backlog",
                "development_workflow",
                DocumentEdgeType.PREREQUISITE_FOR,
                "Backlog is prerequisite for development workflow",
            ),
            (
                "system_overview",
                "development_workflow",
                DocumentEdgeType.PREREQUISITE_FOR,
                "System overview is prerequisite for development workflow",
            ),
            (
                "memory_context",
                "ai_constitution",
                DocumentEdgeType.PREREQUISITE_FOR,
                "Memory context is prerequisite for AI constitution",
            ),
            (
                "system_overview",
                "memory_system",
                DocumentEdgeType.PREREQUISITE_FOR,
                "System overview is prerequisite for memory system",
            ),
            # Intermediate docs for advanced docs
            (
                "development_workflow",
                "dspy_frameworks",
                DocumentEdgeType.PREREQUISITE_FOR,
                "Development workflow is prerequisite for DSPy frameworks",
            ),
            (
                "memory_system",
                "dspy_frameworks",
                DocumentEdgeType.PREREQUISITE_FOR,
                "Memory system is prerequisite for DSPy frameworks",
            ),
            (
                "development_workflow",
                "performance_optimization",
                DocumentEdgeType.PREREQUISITE_FOR,
                "Development workflow is prerequisite for performance optimization",
            ),
            (
                "system_overview",
                "advanced_configurations",
                DocumentEdgeType.PREREQUISITE_FOR,
                "System overview is prerequisite for advanced configurations",
            ),
        ]

        # Add edges
        for source, target, edge_type, description in knowledge_dependencies:
            self._add_edge(source, target, edge_type, description, weight=0.9)

    def _build_content_categories(self) -> None:
        """Build content categories showing different types of documentation"""
        # Content categories
        categories = [
            DocumentNode(
                "architecture_docs",
                "Architecture Documentation",
                DocumentNodeType.CORE_GUIDE,
                "Architecture",
                "System architecture and design documents",
                content_type="architecture",
                cross_reference_count=15,
            ),
            DocumentNode(
                "workflow_docs",
                "Workflow Documentation",
                DocumentNodeType.CORE_GUIDE,
                "Workflow",
                "Process and workflow documentation",
                content_type="workflow",
                cross_reference_count=12,
            ),
            DocumentNode(
                "memory_docs",
                "Memory Documentation",
                DocumentNodeType.MEMORY_DOCUMENT,
                "Memory",
                "Memory system and context documentation",
                content_type="memory",
                cross_reference_count=10,
            ),
            DocumentNode(
                "integration_docs",
                "Integration Documentation",
                DocumentNodeType.SPECIALIZED_GUIDE,
                "Integration",
                "External integrations and APIs",
                content_type="integration",
                cross_reference_count=8,
            ),
            DocumentNode(
                "optimization_docs",
                "Optimization Documentation",
                DocumentNodeType.SPECIALIZED_GUIDE,
                "Optimization",
                "Performance and system optimization",
                content_type="optimization",
                cross_reference_count=6,
            ),
            DocumentNode(
                "governance_docs",
                "Governance Documentation",
                DocumentNodeType.CORE_GUIDE,
                "Governance",
                "AI safety and governance policies",
                content_type="governance",
                cross_reference_count=14,
            ),
        ]

        # Add nodes
        for category in categories:
            self._add_node(category)

        # Define category relationships
        category_relationships = [
            # Architecture is foundational
            (
                "architecture_docs",
                "workflow_docs",
                DocumentEdgeType.FOUNDATION_FOR,
                "Architecture is foundation for workflow",
            ),
            (
                "architecture_docs",
                "memory_docs",
                DocumentEdgeType.FOUNDATION_FOR,
                "Architecture is foundation for memory",
            ),
            (
                "architecture_docs",
                "integration_docs",
                DocumentEdgeType.FOUNDATION_FOR,
                "Architecture is foundation for integration",
            ),
            # Workflow connects to specialized docs
            ("workflow_docs", "integration_docs", DocumentEdgeType.INFLUENCES, "Workflow influences integration"),
            ("workflow_docs", "optimization_docs", DocumentEdgeType.INFLUENCES, "Workflow influences optimization"),
            # Memory supports other categories
            ("memory_docs", "workflow_docs", DocumentEdgeType.SUPPORTS, "Memory supports workflow"),
            ("memory_docs", "integration_docs", DocumentEdgeType.SUPPORTS, "Memory supports integration"),
            # Governance influences all
            ("governance_docs", "architecture_docs", DocumentEdgeType.INFLUENCES, "Governance influences architecture"),
            ("governance_docs", "workflow_docs", DocumentEdgeType.INFLUENCES, "Governance influences workflow"),
            ("governance_docs", "memory_docs", DocumentEdgeType.INFLUENCES, "Governance influences memory"),
        ]

        # Add edges
        for source, target, edge_type, description in category_relationships:
            self._add_edge(source, target, edge_type, description, weight=0.8)

    def _build_navigation_patterns(self) -> None:
        """Build navigation patterns showing how users move through documentation"""
        # Navigation entry points
        entry_points = [
            DocumentNode(
                "memory_overview",
                "Memory System Overview",
                DocumentNodeType.CORE_GUIDE,
                "400_guides/400_00_memory-system-overview.md",
                "Primary entry point",
                content_type="entry",
                cross_reference_count=18,
            ),
            DocumentNode(
                "system_overview",
                "System Overview",
                DocumentNodeType.CORE_GUIDE,
                "400_guides/400_03_system-overview-and-architecture.md",
                "Architecture entry point",
                content_type="entry",
                cross_reference_count=20,
            ),
        ]

        # Development navigation path
        dev_path = [
            DocumentNode(
                "development_workflow",
                "Development Workflow",
                DocumentNodeType.CORE_GUIDE,
                "400_guides/400_04_development-workflow-and-standards.md",
                "Development process",
                content_type="workflow",
                cross_reference_count=16,
            ),
            DocumentNode(
                "codebase_organization",
                "Codebase Organization",
                DocumentNodeType.SPECIALIZED_GUIDE,
                "400_guides/400_05_codebase-organization-patterns.md",
                "Code organization",
                content_type="patterns",
                cross_reference_count=10,
            ),
            DocumentNode(
                "dspy_frameworks",
                "DSPy Frameworks",
                DocumentNodeType.SPECIALIZED_GUIDE,
                "400_guides/400_09_ai-frameworks-dspy.md",
                "AI framework integration",
                content_type="integration",
                cross_reference_count=12,
            ),
        ]

        # Research navigation path
        research_path = [
            DocumentNode(
                "research_index",
                "Research Index",
                DocumentNodeType.RESEARCH_DOCUMENT,
                "500_research/500_research-index.md",
                "Research overview",
                content_type="research",
                cross_reference_count=8,
            ),
            DocumentNode(
                "dspy_research",
                "DSPy Research",
                DocumentNodeType.RESEARCH_DOCUMENT,
                "500_research/500_dspy-research.md",
                "DSPy-specific research",
                content_type="research",
                cross_reference_count=6,
            ),
        ]

        # Add all nodes
        all_docs = entry_points + dev_path + research_path
        for doc in all_docs:
            self._add_node(doc)

        # Define navigation patterns
        navigation_flows = [
            # Entry point navigation
            (
                "memory_overview",
                "system_overview",
                DocumentEdgeType.NAVIGATES_TO,
                "Memory overview navigates to system overview",
            ),
            # Development navigation flow
            (
                "system_overview",
                "development_workflow",
                DocumentEdgeType.NAVIGATES_TO,
                "System overview navigates to development workflow",
            ),
            (
                "development_workflow",
                "codebase_organization",
                DocumentEdgeType.NAVIGATES_TO,
                "Development workflow navigates to codebase organization",
            ),
            (
                "codebase_organization",
                "dspy_frameworks",
                DocumentEdgeType.NAVIGATES_TO,
                "Codebase organization navigates to DSPy frameworks",
            ),
            # Research navigation flow
            (
                "system_overview",
                "research_index",
                DocumentEdgeType.NAVIGATES_TO,
                "System overview navigates to research index",
            ),
            (
                "research_index",
                "dspy_research",
                DocumentEdgeType.NAVIGATES_TO,
                "Research index navigates to DSPy research",
            ),
            # Cross-path navigation
            (
                "dspy_frameworks",
                "dspy_research",
                DocumentEdgeType.NAVIGATES_TO,
                "DSPy frameworks navigates to DSPy research",
            ),
        ]

        # Add edges
        for source, target, edge_type, description in navigation_flows:
            self._add_edge(source, target, edge_type, description, weight=0.8)

    def _build_documentation_health(self) -> None:
        """Build documentation health analysis showing quality metrics"""
        # Documents with different health levels
        healthy_docs = [
            DocumentNode(
                "context_priority_guide",
                "Context Priority Guide",
                DocumentNodeType.CORE_GUIDE,
                "400_guides/400_context-priority-guide.md",
                "High quality, well-referenced",
                content_type="priority",
                cross_reference_count=25,
                word_count=5000,
            ),
            DocumentNode(
                "ai_constitution",
                "AI Constitution",
                DocumentNodeType.CORE_GUIDE,
                "400_guides/400_02_governance-and-ai-constitution.md",
                "Well-maintained governance doc",
                content_type="governance",
                cross_reference_count=18,
                word_count=4500,
            ),
        ]

        medium_health_docs = [
            DocumentNode(
                "development_workflow",
                "Development Workflow",
                DocumentNodeType.CORE_GUIDE,
                "400_guides/400_04_development-workflow-and-standards.md",
                "Good coverage, needs updates",
                content_type="workflow",
                cross_reference_count=16,
                word_count=4000,
            ),
            DocumentNode(
                "system_overview",
                "System Overview",
                DocumentNodeType.CORE_GUIDE,
                "400_guides/400_03_system-overview-and-architecture.md",
                "Comprehensive but complex",
                content_type="architecture",
                cross_reference_count=12,
                word_count=6000,
            ),
        ]

        low_health_docs = [
            DocumentNode(
                "deployment_ops",
                "Deployment Operations",
                DocumentNodeType.SPECIALIZED_GUIDE,
                "400_guides/400_11_deployments-ops-and-observability.md",
                "Low coverage, needs attention",
                content_type="operations",
                cross_reference_count=3,
                word_count=2000,
            ),
            DocumentNode(
                "performance_optimization",
                "Performance Optimization",
                DocumentNodeType.SPECIALIZED_GUIDE,
                "400_guides/400_11_performance-optimization.md",
                "Minimal references, outdated",
                content_type="optimization",
                cross_reference_count=2,
                word_count=1500,
            ),
        ]

        # Add all nodes
        all_docs = healthy_docs + medium_health_docs + low_health_docs
        for doc in all_docs:
            self._add_node(doc)

        # Define health relationships
        health_relationships = [
            # Healthy docs support others
            (
                "context_priority_guide",
                "development_workflow",
                DocumentEdgeType.SUPPORTS,
                "Context priority supports development workflow",
            ),
            (
                "ai_constitution",
                "system_overview",
                DocumentEdgeType.VALIDATES,
                "AI constitution validates system overview",
            ),
            # Medium health docs need improvement
            (
                "development_workflow",
                "deployment_ops",
                DocumentEdgeType.NEEDS_IMPROVEMENT,
                "Development workflow needs deployment ops improvement",
            ),
            (
                "system_overview",
                "performance_optimization",
                DocumentEdgeType.NEEDS_IMPROVEMENT,
                "System overview needs performance optimization improvement",
            ),
            # Low health docs need attention
            (
                "deployment_ops",
                "performance_optimization",
                DocumentEdgeType.NEEDS_ATTENTION,
                "Both need significant attention",
            ),
        ]

        # Add edges
        for source, target, edge_type, description in health_relationships:
            self._add_edge(source, target, edge_type, description, weight=0.6)

    def _add_node(self, node: DocumentNode) -> None:
        """Add a node to the graph"""
        self.nodes[node.id] = node
        self.graph.add_node(
            node.id,
            name=node.name,
            node_type=node.node_type.value,
            file_path=node.file_path,
            description=node.description,
            tier=node.tier,
            priority=node.priority,
            content_type=node.content_type,
            last_updated=node.last_updated.isoformat() if node.last_updated else None,
            word_count=node.word_count,
            cross_reference_count=node.cross_reference_count,
            metadata=node.metadata,
            tags=node.tags,
        )

    def _add_edge(
        self,
        source: str,
        target: str,
        edge_type: DocumentEdgeType,
        description: str = "",
        weight: float = 1.0,
        strength: float = 1.0,
    ) -> None:
        """Add an edge to the graph"""
        edge = DocumentEdge(source, target, edge_type, weight, strength, description)
        self.edges.append(edge)
        self.graph.add_edge(
            source,
            target,
            edge_type=edge_type.value,
            weight=edge.weight,
            strength=edge.strength,
            description=description,
            link_type=edge.link_type,
            context=edge.context,
            metadata=edge.metadata,
        )

    def find_document_paths(self, source: str, target: str, max_length: int = 5) -> list[list[str]]:
        """Find paths between documents"""
        try:
            return list(nx.all_simple_paths(self.graph, source, target, cutoff=max_length))
        except nx.NetworkXNoPath:
            return []

    def find_document_clusters(self) -> list[list[str]]:
        """Find clusters of related documents"""
        try:
            import networkx.algorithms.community as nx_comm

            communities = nx_comm.greedy_modularity_communities(self.graph.to_undirected())
            return [list(community) for community in communities]
        except ImportError:
            return [list(component) for component in nx.connected_components(self.graph.to_undirected())]

    def analyze_documentation_health(self) -> dict[str, Any]:
        """Analyze documentation health and quality metrics"""
        if not self.graph.nodes():
            return {"error": "No nodes in documentation graph"}

        # Basic metrics
        num_nodes = self.graph.number_of_nodes()
        num_edges = self.graph.number_of_edges()
        density = float(nx.density(self.graph))

        # Document clusters
        clusters: Any = self.find_document_clusters()
        num_clusters = len(clusters)
        avg_cluster_size = sum(len(cluster) for cluster in clusters) / num_clusters if clusters else 0

        # Node analysis
        node_types = {}
        content_types = {}
        tiers = {}
        for node_id in self.graph.nodes():
            node_type = self.graph.nodes[node_id].get("node_type", "unknown")
            node_types[node_type] = node_types.get(node_type, 0) + 1

            content_type = self.graph.nodes[node_id].get("content_type", "unknown")
            content_types[content_type] = content_types.get(content_type, 0) + 1

            tier = self.graph.nodes[node_id].get("tier", 0)
            tiers[tier] = tiers.get(tier, 0) + 1

        # Edge analysis
        edge_types = {}
        for source, target in self.graph.edges():
            edge_type = self.graph.edges[source, target].get("edge_type", "unknown")
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1

        # Cross-reference analysis
        total_cross_references = sum(
            self.graph.nodes[node_id].get("cross_reference_count", 0) for node_id in self.graph.nodes()
        )
        avg_cross_references = total_cross_references / num_nodes if num_nodes > 0 else 0

        # Health scoring
        high_health_docs = sum(
            1 for node_id in self.graph.nodes() if self.graph.nodes[node_id].get("cross_reference_count", 0) >= 15
        )
        medium_health_docs = sum(
            1 for node_id in self.graph.nodes() if 5 <= self.graph.nodes[node_id].get("cross_reference_count", 0) < 15
        )
        low_health_docs = sum(
            1 for node_id in self.graph.nodes() if self.graph.nodes[node_id].get("cross_reference_count", 0) < 5
        )

        return {
            "documentation_type": self.doc_type.value,
            "total_documents": num_nodes,
            "total_relationships": num_edges,
            "density": density,
            "num_clusters": num_clusters,
            "avg_cluster_size": avg_cluster_size,
            "clusters": clusters,
            "node_type_distribution": node_types,
            "content_type_distribution": content_types,
            "tier_distribution": tiers,
            "edge_type_distribution": edge_types,
            "avg_cross_references": avg_cross_references,
            "health_distribution": {
                "high_health": high_health_docs,
                "medium_health": medium_health_docs,
                "low_health": low_health_docs,
            },
            "is_connected": nx.is_weakly_connected(self.graph),
            "has_cycles": not nx.is_directed_acyclic_graph(self.graph),
        }

    def visualize_documentation_graph(self, output_path: str = "documentation_graph.png") -> None:
        """Visualize the documentation knowledge graph"""
        try:
            import matplotlib.patches as mpatches  # type: ignore[import-untyped]
            import matplotlib.pyplot as plt  # type: ignore[import-untyped]
        except ImportError:
            print("Matplotlib not available for visualization")
            return

        plt.figure(figsize=(16, 12))

        # Use hierarchical layout
        pos: Any = nx.spring_layout(self.graph, k=3, iterations=50)

        # Color nodes by type
        node_colors = []
        node_type_colors = {
            "core_guide": "#FF6B6B",
            "specialized_guide": "#4ECDC4",
            "workflow_document": "#45B7D1",
            "reference_document": "#96CEB4",
            "template_document": "#FFEAA7",
            "research_document": "#DDA0DD",
            "setup_document": "#98D8C8",
            "memory_document": "#F7DC6F",
            "configuration_document": "#BB8FCE",
            "archive_document": "#85C1E9",
        }

        for node_id in self.graph.nodes():
            node_type = self.graph.nodes[node_id].get("node_type", "unknown")
            node_colors.append(node_type_colors.get(node_type, "#CCCCCC"))

        # Draw nodes
        nx.draw_networkx_nodes(self.graph, pos, node_color=node_colors, node_size=1000, alpha=0.8)

        # Draw edges with different styles for different types
        edge_styles = {
            "references": "solid",
            "depends_on": "solid",
            "prerequisite_for": "dashed",
            "extends": "dotted",
            "implements": "solid",
            "validates": "dashed",
            "supplements": "dotted",
            "replaces": "solid",
            "version_of": "dashed",
            "part_of": "solid",
            "contains": "solid",
            "links_to": "dotted",
            "cross_references": "solid",
            "navigates_to": "dashed",
            "follows_from": "dotted",
            "precedes": "solid",
        }

        for edge_type, style in edge_styles.items():
            edges = [(u, v) for u, v, d in self.graph.edges(data=True) if d.get("edge_type") == edge_type]
            if edges:
                nx.draw_networkx_edges(
                    self.graph,
                    pos,
                    edgelist=edges,
                    edge_color="gray",
                    style=style,
                    arrows=True,
                    arrowsize=20,
                    alpha=0.6,
                )

        # Draw labels
        labels = {node_id: self.graph.nodes[node_id].get("name", node_id) for node_id in self.graph.nodes()}
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=8)

        # Create legend
        legend_elements = [
            mpatches.Patch(color=color, label=node_type.title()) for node_type, color in node_type_colors.items()
        ]
        plt.legend(handles=legend_elements, loc="upper right")

        plt.title(
            f"{self.doc_type.value.replace('-', ' ').title()} Documentation Graph", fontsize=16, fontweight="bold"
        )
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"📊 Documentation graph saved: {output_path}")

    def export_documentation_data(self, output_path: str = "documentation_data.json") -> None:
        """Export documentation knowledge data to JSON"""
        data = {
            "documentation_type": self.doc_type.value,
            "created_at": datetime.now().isoformat(),
            "nodes": [
                {
                    "id": node.id,
                    "name": node.name,
                    "node_type": node.node_type.value,
                    "file_path": node.file_path,
                    "description": node.description,
                    "tier": node.tier,
                    "priority": node.priority,
                    "content_type": node.content_type,
                    "last_updated": node.last_updated.isoformat() if node.last_updated else None,
                    "word_count": node.word_count,
                    "cross_reference_count": node.cross_reference_count,
                    "metadata": node.metadata,
                    "tags": node.tags,
                }
                for node in self.nodes.values()
            ],
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "edge_type": edge.edge_type.value,
                    "weight": edge.weight,
                    "strength": edge.strength,
                    "description": edge.description,
                    "link_type": edge.link_type,
                    "context": edge.context,
                    "metadata": edge.metadata,
                }
                for edge in self.edges
            ],
            "analysis": self.analyze_documentation_health(),
        }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        print(f"💾 Documentation data exported: {output_path}")


def main() -> None:
    """Main function for command-line usage"""
    import argparse

    parser: Any = argparse.ArgumentParser(description="Documentation Knowledge Graph System")
    parser.add_argument(
        "--doc-type",
        choices=[dt.value for dt in DocumentationType],
        default=DocumentationType.HIERARCHY.value,
        help="Type of documentation relationships to model",
    )
    parser.add_argument("--analyze", action="store_true", help="Analyze documentation health and relationships")
    parser.add_argument("--visualize", action="store_true", help="Generate documentation graph visualization")
    parser.add_argument("--export", action="store_true", help="Export documentation data to JSON")
    parser.add_argument("--output-dir", default=".", help="Output directory for generated files")

    args: Any = parser.parse_args()

    # Create documentation graph
    doc_type = DocumentationType(args.doc_type)
    graph = DocumentationKnowledgeGraph(doc_type)

    print(f"🔧 Built {doc_type.value} documentation graph")
    print(f"📊 Total documents: {graph.graph.number_of_nodes()}")
    print(f"🔗 Total relationships: {graph.graph.number_of_edges()}")

    # Analyze documentation health
    if args.analyze:
        analysis: Any = graph.analyze_documentation_health()
        print("\n📈 Documentation Analysis:")
        print(f"   Density: {analysis['density']:.3f}")
        print(f"   Clusters: {analysis['num_clusters']}")
        print(f"   Avg cluster size: {analysis['avg_cluster_size']:.1f}")
        print(f"   Avg cross-references: {analysis['avg_cross_references']:.1f}")
        print(f"   Is connected: {analysis['is_connected']}")
        print(f"   Has cycles: {analysis['has_cycles']}")

        if analysis.get("health_distribution"):
            health = analysis["health_distribution"]
            print(
                f"   Health distribution: High={health['high_health']}, Medium={health['medium_health']}, Low={health['low_health']}"
            )

    # Visualize documentation graph
    if args.visualize:
        output_path = f"{args.output_dir}/documentation_{doc_type.value}.png"
        graph.visualize_documentation_graph(output_path)

    # Export documentation data
    if args.export:
        output_path = f"{args.output_dir}/documentation_{doc_type.value}.json"
        graph.export_documentation_data(output_path)


if __name__ == "__main__":
    main()
