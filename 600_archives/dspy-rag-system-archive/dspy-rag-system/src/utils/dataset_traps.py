#!/usr/bin/env python3
"""
Dataset Design Traps
- Coverage grid for comprehensive evaluation
- Negative controls and adversarial placement
- Multi-hop and needle-in-haystack tests
"""

import json
import random
from dataclasses import dataclass
from typing import Any

from .config_lock import LockedConfig


@dataclass
class TestCase:
    """Individual test case"""

    id: str
    question: str
    answer: str
    context: list[str]
    category: str
    difficulty: str
    expected_retrieval_size: int
    has_answer: bool
    is_adversarial: bool = False
    is_negative_control: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "question": self.question,
            "answer": self.answer,
            "context": self.context,
            "category": self.category,
            "difficulty": self.difficulty,
            "expected_retrieval_size": self.expected_retrieval_size,
            "has_answer": self.has_answer,
            "is_adversarial": self.is_adversarial,
            "is_negative_control": self.is_negative_control,
        }


class DatasetTrapManager:
    """Manages dataset design traps and test case generation"""

    def __init__(self, config: LockedConfig):
        self.config = config
        self.test_cases: list[TestCase] = []

        # Coverage grid categories
        self.categories = [
            "ops_healthchecks",
            "db_workflows",
            "rag_qa",
            "meta_ops",
            "needle_in_haystack",
            "multi_hop",
            "date_numeric",
            "negative_control",
        ]

        # Difficulty levels
        self.difficulties = ["easy", "medium", "hard", "expert"]

    def generate_coverage_grid(self, num_cases_per_category: int = 5) -> list[TestCase]:
        """Generate comprehensive coverage grid"""
        print("🎯 Generating Coverage Grid")
        print("=" * 40)

        test_cases = []

        # Ops/Healthchecks
        test_cases.extend(self._generate_ops_healthcheck_cases(num_cases_per_category))

        # DB Workflows
        test_cases.extend(self._generate_db_workflow_cases(num_cases_per_category))

        # RAG QA
        test_cases.extend(self._generate_rag_qa_cases(num_cases_per_category))

        # Meta-ops
        test_cases.extend(self._generate_meta_ops_cases(num_cases_per_category))

        # Needle in haystack
        test_cases.extend(self._generate_needle_cases(num_cases_per_category))

        # Multi-hop
        test_cases.extend(self._generate_multi_hop_cases(num_cases_per_category))

        # Date/Numeric
        test_cases.extend(self._generate_date_numeric_cases(num_cases_per_category))

        # Negative controls
        test_cases.extend(self._generate_negative_control_cases(num_cases_per_category))

        self.test_cases = test_cases

        print(f"✅ Generated {len(test_cases)} test cases across {len(self.categories)} categories")

        return test_cases

    def _generate_ops_healthcheck_cases(self, num_cases: int) -> list[TestCase]:
        """Generate ops/healthcheck test cases"""
        cases = []

        ops_questions = [
            "Is the document index present and healthy?",
            "Are there any prefix leakage issues in BM25?",
            "What is the current chunk size configuration?",
            "How many chunks are over the token budget?",
            "What is the deduplication rate?",
            "Is the reranker loaded and ready?",
            "What is the current ingest run ID?",
            "Are there any token budget violations?",
        ]

        for i, question in enumerate(ops_questions[:num_cases]):
            case = TestCase(
                id=f"ops_healthcheck_{i+1}",
                question=question,
                answer="System health check response",
                context=["System configuration", "Health metrics", "Index status"],
                category="ops_healthchecks",
                difficulty="medium",
                expected_retrieval_size=30,
                has_answer=True,
            )
            cases.append(case)

        return cases

    def _generate_db_workflow_cases(self, num_cases: int) -> list[TestCase]:
        """Generate database workflow test cases"""
        cases = []

        db_questions = [
            "How do I troubleshoot database connection issues?",
            "What are the steps to perform a database backup?",
            "How do I optimize database query performance?",
            "What is the database schema for document chunks?",
            "How do I monitor database health?",
            "What are the database indexing strategies?",
            "How do I handle database migrations?",
            "What are the database connection pool settings?",
        ]

        for i, question in enumerate(db_questions[:num_cases]):
            case = TestCase(
                id=f"db_workflow_{i+1}",
                question=question,
                answer="Database workflow instructions",
                context=["Database documentation", "Troubleshooting guide", "Schema reference"],
                category="db_workflows",
                difficulty="medium",
                expected_retrieval_size=40,
                has_answer=True,
            )
            cases.append(case)

        return cases

    def _generate_rag_qa_cases(self, num_cases: int) -> list[TestCase]:
        """Generate RAG QA test cases"""
        cases = []

        rag_questions = [
            "What is DSPy and how does it work?",
            "How does the RAG system retrieve relevant documents?",
            "What are the main components of the chunking system?",
            "How does the enhanced chunking algorithm work?",
            "What is the difference between embedding and BM25 text?",
            "How does the recursive splitting algorithm work?",
            "What are the benefits of contextual prefixes?",
            "How does the Jaccard similarity threshold work?",
        ]

        for i, question in enumerate(rag_questions[:num_cases]):
            case = TestCase(
                id=f"rag_qa_{i+1}",
                question=question,
                answer="RAG system explanation",
                context=["DSPy documentation", "RAG system overview", "Chunking algorithms"],
                category="rag_qa",
                difficulty="medium",
                expected_retrieval_size=50,
                has_answer=True,
            )
            cases.append(case)

        return cases

    def _generate_meta_ops_cases(self, num_cases: int) -> list[TestCase]:
        """Generate meta-ops test cases"""
        cases = []

        meta_questions = [
            "Explain the tool schema for the configuration system",
            "Generate an evaluation runbook for the current setup",
            "What are the available tools and their parameters?",
            "How do I create a new evaluation dataset?",
            "What is the tool registry structure?",
            "How do I validate tool outputs?",
            "What are the tool timeout and retry policies?",
            "How do I monitor tool usage and performance?",
        ]

        for i, question in enumerate(meta_questions[:num_cases]):
            case = TestCase(
                id=f"meta_ops_{i+1}",
                question=question,
                answer="Meta-operations guide",
                context=["Tool documentation", "Schema definitions", "Usage examples"],
                category="meta_ops",
                difficulty="hard",
                expected_retrieval_size=35,
                has_answer=True,
            )
            cases.append(case)

        return cases

    def _generate_needle_cases(self, num_cases: int) -> list[TestCase]:
        """Generate needle-in-haystack test cases"""
        cases = []

        needle_questions = [
            "What is the exact value of the Jaccard threshold in the current configuration?",
            "What is the specific chunk size used in the enhanced chunking system?",
            "What is the exact overlap ratio configured for document splitting?",
            "What is the specific embedder name used in the current setup?",
            "What is the exact prefix policy (A or B) currently active?",
            "What is the specific tokenizer hash for the current configuration?",
            "What is the exact config hash for the locked configuration?",
            "What is the specific shadow table name for the current rollout?",
        ]

        for i, question in enumerate(needle_questions[:num_cases]):
            case = TestCase(
                id=f"needle_{i+1}",
                question=question,
                answer=f"Specific configuration value {i+1}",
                context=["Configuration details", "System settings", "Technical specifications"],
                category="needle_in_haystack",
                difficulty="expert",
                expected_retrieval_size=60,
                has_answer=True,
                is_adversarial=True,
            )
            cases.append(case)

        return cases

    def _generate_multi_hop_cases(self, num_cases: int) -> list[TestCase]:
        """Generate multi-hop reasoning test cases"""
        cases = []

        multi_hop_questions = [
            "If the chunk size is 450 and overlap ratio is 0.10, what is the effective overlap in tokens?",
            "Given that the Jaccard threshold is 0.8 and ngram size is 5, how many similar chunks would be deduplicated?",
            "If the embedder supports 1024 tokens and we have 450 token chunks, how many chunks can fit in one embedding?",
            "Given the current configuration, what would be the total number of chunks for a 10,000 token document?",
            "If the deduplication rate is 20% and we start with 1000 chunks, how many chunks remain after deduplication?",
            "Given the prefix policy A and contextual prefix length, what is the total token count for embedding text?",
            "If the retrieval snapshot size is 50 and we have 12 context documents, what is the utilization rate?",
            "Given the current chunk version and config hash, what is the complete ingest run ID?",
        ]

        for i, question in enumerate(multi_hop_questions[:num_cases]):
            case = TestCase(
                id=f"multi_hop_{i+1}",
                question=question,
                answer=f"Multi-hop calculation result {i+1}",
                context=["Configuration parameters", "Calculation methods", "System metrics"],
                category="multi_hop",
                difficulty="hard",
                expected_retrieval_size=45,
                has_answer=True,
            )
            cases.append(case)

        return cases

    def _generate_date_numeric_cases(self, num_cases: int) -> list[TestCase]:
        """Generate date/numeric test cases"""
        cases = []

        date_numeric_questions = [
            "What was the configuration created on 2025-09-07?",
            "How many chunks were processed in the last ingest run?",
            "What is the token count for a 1000-character document?",
            "What is the processing time for 10,000 tokens?",
            "How many documents were processed in the last 24 hours?",
            "What is the average chunk size in the current dataset?",
            "What is the maximum token count observed in the system?",
            "How many evaluation runs were performed this week?",
        ]

        for i, question in enumerate(date_numeric_questions[:num_cases]):
            case = TestCase(
                id=f"date_numeric_{i+1}",
                question=question,
                answer=f"Numeric/date answer {i+1}",
                context=["System metrics", "Processing logs", "Performance data"],
                category="date_numeric",
                difficulty="medium",
                expected_retrieval_size=40,
                has_answer=True,
            )
            cases.append(case)

        return cases

    def _generate_negative_control_cases(self, num_cases: int) -> list[TestCase]:
        """Generate negative control test cases (no answer in corpus)"""
        cases = []

        negative_questions = [
            "What is the weather like today?",
            "How do I cook a perfect steak?",
            "What are the latest stock market prices?",
            "How do I fix a broken washing machine?",
            "What is the capital of Mars?",
            "How do I learn to play the piano?",
            "What are the best restaurants in Tokyo?",
            "How do I build a rocket ship?",
        ]

        for i, question in enumerate(negative_questions[:num_cases]):
            case = TestCase(
                id=f"negative_control_{i+1}",
                question=question,
                answer="I don't have information about this topic in my knowledge base.",
                context=[],
                category="negative_control",
                difficulty="easy",
                expected_retrieval_size=0,
                has_answer=False,
                is_negative_control=True,
            )
            cases.append(case)

        return cases

    def add_adversarial_placement(self, test_cases: list[TestCase]) -> list[TestCase]:
        """Add adversarial placement to catch 'lost-in-the-middle' effects"""
        print("🎯 Adding Adversarial Placement")
        print("=" * 40)

        # Find cases that should have middle-placed gold
        adversarial_cases = []

        for case in test_cases:
            if case.has_answer and not case.is_negative_control:
                # Mark some cases as adversarial (gold in middle)
                if random.random() < 0.3:  # 30% of cases
                    case.is_adversarial = True
                    adversarial_cases.append(case)

        print(f"✅ Marked {len(adversarial_cases)} cases as adversarial (gold in middle)")

        return test_cases

    def validate_dataset_coverage(self) -> dict[str, Any]:
        """Validate dataset coverage"""
        if not self.test_cases:
            return {"valid": False, "error": "No test cases generated"}

        coverage = {}
        issues = []
        warnings = []

        # Check category coverage
        for category in self.categories:
            category_cases = [case for case in self.test_cases if case.category == category]
            coverage[category] = len(category_cases)

            if len(category_cases) == 0:
                issues.append(f"No test cases for category: {category}")
            elif len(category_cases) < 3:
                warnings.append(f"Low coverage for category {category}: {len(category_cases)} cases")

        # Check difficulty distribution
        difficulty_counts = {}
        for case in self.test_cases:
            difficulty_counts[case.difficulty] = difficulty_counts.get(case.difficulty, 0) + 1

        # Check negative controls
        negative_controls = [case for case in self.test_cases if case.is_negative_control]
        if len(negative_controls) == 0:
            issues.append("No negative control cases")
        elif len(negative_controls) < 3:
            warnings.append(f"Low negative control coverage: {len(negative_controls)} cases")

        # Check adversarial cases
        adversarial_cases = [case for case in self.test_cases if case.is_adversarial]
        if len(adversarial_cases) == 0:
            warnings.append("No adversarial placement cases")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "coverage": coverage,
            "difficulty_distribution": difficulty_counts,
            "total_cases": len(self.test_cases),
            "negative_controls": len(negative_controls),
            "adversarial_cases": len(adversarial_cases),
        }

    def save_test_cases(self, filepath: str) -> None:
        """Save test cases to file"""
        test_data = {
            "config": {
                "chunk_version": self.config.chunk_version,
                "config_hash": self.config.get_config_hash(),
                "chunk_size": self.config.chunk_size,
                "overlap_ratio": self.config.overlap_ratio,
                "jaccard_threshold": self.config.jaccard_threshold,
                "prefix_policy": self.config.prefix_policy,
            },
            "test_cases": [case.to_dict() for case in self.test_cases],
            "coverage_validation": self.validate_dataset_coverage(),
        }

        with open(filepath, "w") as f:
            json.dump(test_data, f, indent=2)

        print(f"📝 Test cases saved to: {filepath}")


def create_dataset_trap_manager(config: LockedConfig) -> DatasetTrapManager:
    """Create a dataset trap manager for the given configuration"""
    return DatasetTrapManager(config)
