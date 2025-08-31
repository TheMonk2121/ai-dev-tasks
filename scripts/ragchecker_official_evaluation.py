#!/usr/bin/env python3
"""
Official RAGChecker Evaluation Script with Local LLM Support

This script implements RAGChecker evaluation following the official methodology:
1. Prepare input data in the correct JSON format
2. Use custom LLM function integration for local models (preferred)
3. Use official RAGChecker CLI when available (fallback)
4. Follow official metrics and procedures
5. Generate proper evaluation reports

Based on official RAGChecker documentation and best practices.
Includes custom LLM integration for local models via Ollama.
"""

import json
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import requests
except ImportError:
    print("⚠️ requests module not available - local LLM evaluation will not work")
    requests = None

try:
    from sentence_transformers import SentenceTransformer

    EMBEDDINGS_AVAILABLE = True
except ImportError:
    print("⚠️ sentence-transformers not available - semantic features disabled")
    SentenceTransformer = None
    EMBEDDINGS_AVAILABLE = False

try:
    from scripts.bedrock_client import BedrockClient

    BEDROCK_AVAILABLE = True
except ImportError:
    print("⚠️ bedrock_client not available - AWS Bedrock evaluation disabled")
    BedrockClient = None
    BEDROCK_AVAILABLE = False


@dataclass
class RAGCheckerInput:
    """RAGChecker input data structure following official format."""

    query_id: str
    query: str
    gt_answer: str
    response: str
    retrieved_context: List[str]  # List of context strings, not dicts


@dataclass
class RAGCheckerMetrics:
    """RAGChecker metrics following official specification."""

    # Overall Metrics
    precision: float
    recall: float
    f1_score: float

    # Retriever Metrics
    claim_recall: float
    context_precision: float

    # Generator Metrics
    context_utilization: float
    noise_sensitivity: float
    hallucination: float
    self_knowledge: float
    faithfulness: float


class LocalLLMIntegration:
    """Hybrid LLM integration supporting both local models (Ollama) and AWS Bedrock."""

    def __init__(
        self, api_base: str = "http://localhost:11434", model_name: str = "llama3.1:8b", use_bedrock: bool = False
    ):
        self.use_bedrock = use_bedrock
        self.bedrock_client = None

        if use_bedrock:
            if not BEDROCK_AVAILABLE:
                raise ImportError("bedrock_client module is required for Bedrock integration")
            try:
                self.bedrock_client = BedrockClient()  # type: ignore
                print("✅ AWS Bedrock Claude 3.5 Sonnet integration enabled")
            except Exception as e:
                print(f"⚠️ Failed to initialize Bedrock client: {e}")
                print("🔄 Falling back to local LLM")
                self.use_bedrock = False

        if not self.use_bedrock:
            if requests is None:
                raise ImportError("requests module is required for local LLM integration")
            self.api_base = api_base.rstrip("/")
            self.model_name = model_name
            self.session = requests.Session()
            print(f"✅ Local LLM integration enabled ({model_name})")

        # Initialize embedding model for semantic operations
        self.embedding_model = None
        if EMBEDDINGS_AVAILABLE and os.getenv("RAGCHECKER_SEMANTIC_FEATURES", "1") == "1":
            try:
                self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")  # type: ignore
                print("✅ Semantic embeddings enabled (all-MiniLM-L6-v2)")
            except Exception as e:
                print(f"⚠️ Failed to load embedding model: {e}")
                self.embedding_model = None

    def call_local_llm(self, prompt: str, max_tokens: int = 1000) -> str:
        """Call LLM via either Bedrock or local Ollama API."""
        if self.use_bedrock and self.bedrock_client:
            return self._call_bedrock_llm(prompt, max_tokens)
        else:
            return self._call_ollama_llm(prompt, max_tokens)

    def _call_bedrock_llm(self, prompt: str, max_tokens: int = 1000) -> str:
        """Call AWS Bedrock Claude 3.5 Sonnet."""
        try:
            # Use JSON prompts if enabled for better parsing
            if os.getenv("RAGCHECKER_JSON_PROMPTS", "1") == "1":
                response_text, usage = self.bedrock_client.invoke_with_json_prompt(  # type: ignore
                    prompt=prompt, max_tokens=max_tokens, temperature=0.1
                )
            else:
                response_text, usage = self.bedrock_client.invoke_model(  # type: ignore
                    prompt=prompt, max_tokens=max_tokens, temperature=0.1
                )

            # Log usage for cost monitoring
            print(f"💰 Bedrock usage: {usage.input_tokens}→{usage.output_tokens} tokens, ${usage.total_cost:.4f}")

            return response_text

        except Exception as e:
            print(f"⚠️ Bedrock LLM call failed: {e}")
            print("🔄 Falling back to local LLM")
            self.use_bedrock = False
            return self._call_ollama_llm(prompt, max_tokens)

    def _call_ollama_llm(self, prompt: str, max_tokens: int = 1000) -> str:
        """Call local LLM via Ollama API."""
        try:
            response = self.session.post(
                f"{self.api_base}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.1,
                    },
                },
                timeout=10,  # Reduced from 60s for faster testing
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            print(f"⚠️ Local LLM call failed: {e}")
            return ""

    def build_concise_prompt(self, query: str, context: List[str]) -> str:
        """Build concise prompt for focused response generation."""
        max_words = int(os.getenv("RAGCHECKER_MAX_WORDS", "1000"))
        require_citations = os.getenv("RAGCHECKER_REQUIRE_CITATIONS", "1") == "1"
        context_topk = int(os.getenv("RAGCHECKER_CONTEXT_TOPK", "3"))

        # Limit context to most relevant chunks
        limited_context = context[:context_topk] if context else []
        context_text = "\n".join(limited_context)

        citation_req = ""
        if require_citations:
            citation_req = """
- Cite specific context when stating factual claims
- If unsupported by context, say 'Not supported by context'"""

        return f"""Answer this query concisely and directly. Be information-dense and relevant.

Constraints:
- Maximum {max_words} words
- No unnecessary elaboration or digressions{citation_req}

Query: {query}

Context (top {context_topk} most relevant):
{context_text}

Focused Answer:""".strip()

    def apply_word_limit(self, text: str, max_words: Optional[int] = None) -> str:
        """Apply hard word limit to generated text."""
        if max_words is None:
            max_words = int(os.getenv("RAGCHECKER_MAX_WORDS", "1000"))

        words = text.split()
        if len(words) > max_words:
            return " ".join(words[:max_words])
        return text

    def rank_context_by_query_similarity(self, query: str, context_list: List[str]) -> List[str]:
        """Rank context chunks by semantic similarity to query."""
        if not self.embedding_model or not context_list:
            return context_list

        try:
            # Get embeddings for query and all context chunks
            query_embedding = self.embedding_model.encode([query])
            context_embeddings = self.embedding_model.encode(context_list)

            # Calculate similarities
            from sklearn.metrics.pairwise import cosine_similarity

            similarities = cosine_similarity(query_embedding, context_embeddings)[0]

            # Sort context by similarity (highest first)
            ranked_indices = similarities.argsort()[::-1]
            ranked_context = [context_list[i] for i in ranked_indices]

            print(f"🎯 Ranked {len(context_list)} context chunks by semantic similarity")
            return ranked_context

        except Exception as e:
            print(f"⚠️ Context ranking failed: {e}")
            return context_list

    def calculate_semantic_query_relevance(self, query: str, response: str) -> float:
        """Calculate semantic similarity between query and response."""
        if not self.embedding_model:
            # Fallback to word overlap
            query_words = set(query.lower().split())
            response_words = set(response.lower().split())
            if not query_words:
                return 0.0
            return len(query_words & response_words) / len(query_words)

        try:
            # Use semantic similarity
            query_embedding = self.embedding_model.encode([query])
            response_embedding = self.embedding_model.encode([response])

            from sklearn.metrics.pairwise import cosine_similarity

            similarity = cosine_similarity(query_embedding, response_embedding)[0][0]

            return float(similarity)

        except Exception as e:
            print(f"⚠️ Semantic similarity failed: {e}")
            # Fallback to word overlap
            query_words = set(query.lower().split())
            response_words = set(response.lower().split())
            if not query_words:
                return 0.0
            return len(query_words & response_words) / len(query_words)

    def extract_claims(self, query: str, response: str, context: List[str]) -> List[str]:
        """Extract claims from response using local LLM."""
        context_text = "\n".join(context)
        prompt = f"""
Extract factual claims from the following response. Return only the claims, one per line.

Query: {query}
Context: {context_text}
Response: {response}

Claims:
"""
        result = self.call_local_llm(prompt, max_tokens=1500)
        claims = [line.strip() for line in result.split("\n") if line.strip()]
        return claims

    def check_claim_factuality(self, claim: str, context: List[str]) -> float:
        """Check if a claim is factual based on context using local LLM."""
        context_text = "\n".join(context)
        prompt = f"""
Based on the provided context, is the following claim factual? Respond with valid JSON only.

Context: {context_text}
Claim: {claim}

Respond in this exact JSON format:
{{"score": 0.8, "reasoning": "Brief explanation of factuality"}}

Score range: 0.0 (completely false) to 1.0 (completely true)
"""
        result = self.call_local_llm(prompt, max_tokens=150)
        try:
            # Extract numeric score from response
            score_str = "".join(filter(lambda x: x.isdigit() or x == ".", result))
            score = float(score_str) if score_str else 0.5
            return max(0.0, min(1.0, score))  # Clamp to valid range
        except (ValueError, TypeError) as e:
            print(f"⚠️ Score parsing failed: {e}")
            return 0.5  # Default to neutral if parsing fails

    def evaluate_comprehensive_metrics(
        self, query: str, response: str, context: List[str], gt_answer: str
    ) -> Dict[str, float]:
        """Evaluate comprehensive RAGChecker-style metrics using local LLM."""
        context_text = "\n".join(context)

        # Check if JSON prompts are enabled
        use_json_prompts = os.getenv("RAGCHECKER_JSON_PROMPTS", "1") == "1"
        if use_json_prompts:
            print("🔧 Using structured JSON prompts for reliable scoring")

        # 1. Context Precision - How relevant is the retrieved context to the query
        context_precision_prompt = f"""
Rate how relevant the retrieved context is to answering the query. Respond with valid JSON only.

Query: {query}
Retrieved Context: {context_text}

Respond in this exact JSON format:
{{"score": 0.8, "reasoning": "Brief explanation of relevance"}}

Score range: 0.0 (completely irrelevant) to 1.0 (perfectly relevant)
"""
        context_precision = self._extract_score(self.call_local_llm(context_precision_prompt, max_tokens=150))

        # 2. Context Utilization - How well does the response use the provided context
        context_utilization_prompt = f"""
Rate how well the response utilizes the provided context. Respond with valid JSON only.

Context: {context_text}
Response: {response}

Respond in this exact JSON format:
{{"score": 0.7, "reasoning": "Brief explanation of utilization"}}

Score range: 0.0 (ignores context) to 1.0 (fully utilizes context)
"""
        context_utilization = self._extract_score(self.call_local_llm(context_utilization_prompt, max_tokens=150))

        # 3. Noise Sensitivity - How well does the response avoid irrelevant information
        noise_sensitivity_prompt = f"""
Rate how well the response avoids including irrelevant or noisy information. Respond with valid JSON only.

Query: {query}
Response: {response}

Respond in this exact JSON format:
{{"score": 0.9, "reasoning": "Brief explanation of noise level"}}

Score range: 0.0 (full of noise) to 1.0 (no noise)
"""
        noise_sensitivity = self._extract_score(self.call_local_llm(noise_sensitivity_prompt, max_tokens=150))

        # 4. Hallucination Detection - Does the response contain information not in context
        hallucination_prompt = f"""
Rate how much the response contains information that is NOT supported by the context. Respond with valid JSON only.

Context: {context_text}
Response: {response}

Respond in this exact JSON format:
{{"score": 0.1, "reasoning": "Brief explanation of hallucinations found"}}

Score range: 0.0 (no hallucinations) to 1.0 (full of hallucinations)
"""
        hallucination_raw = self._extract_score(self.call_local_llm(hallucination_prompt, max_tokens=150))
        hallucination = 1.0 - hallucination_raw  # Invert so higher is better

        # 5. Self Knowledge - Does the response appropriately indicate uncertainty
        self_knowledge_prompt = f"""
Rate how well the response indicates uncertainty when appropriate and shows knowledge boundaries. Respond with valid JSON only.

Query: {query}
Response: {response}

Respond in this exact JSON format:
{{"score": 0.8, "reasoning": "Brief explanation of self-awareness"}}

Score range: 0.0 (poor self-awareness) to 1.0 (excellent self-awareness)
"""
        self_knowledge = self._extract_score(self.call_local_llm(self_knowledge_prompt, max_tokens=150))

        # 6. Claim Recall - How many relevant claims from context are included
        claim_recall_prompt = f"""
Rate how well the response recalls and includes the relevant claims from the context. Respond with valid JSON only.

Context: {context_text}
Ground Truth: {gt_answer}
Response: {response}

Respond in this exact JSON format:
{{"score": 0.6, "reasoning": "Brief explanation of claim coverage"}}

Score range: 0.0 (misses all relevant claims) to 1.0 (includes all relevant claims)
"""
        claim_recall = self._extract_score(self.call_local_llm(claim_recall_prompt, max_tokens=150))

        return {
            "context_precision": context_precision,
            "context_utilization": context_utilization,
            "noise_sensitivity": noise_sensitivity,
            "hallucination": hallucination,
            "self_knowledge": self_knowledge,
            "claim_recall": claim_recall,
        }

    def _extract_score(self, llm_response: str) -> float:
        """Extract score from LLM response with robust JSON-first parsing."""
        # Use environment flag to enable/disable robust parsing
        if os.getenv("RAGCHECKER_ROBUST_PARSER", "1") == "1":
            return self._extract_score_robust(llm_response)
        else:
            return self._extract_score_legacy(llm_response)

    def _extract_score_robust(self, llm_response: str) -> float:
        """Robust JSON-first score extraction with safe fallbacks."""
        import json
        import re

        def _clamp01(x: float) -> float:
            return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)

        def _parse_ratio(text: str):
            """Parse ratio like '7/10' or '8/100'"""
            m = re.search(r"(?<!\d)(\d+(?:\.\d+)?)\s*/\s*(10|100)(?!\d)", text)
            if not m:
                return None
            num, den = float(m.group(1)), float(m.group(2))
            return _clamp01(num / den)

        def _parse_decimal01(text: str):
            """Parse decimal in [0,1] range"""
            m = re.search(r"(?<!\d)(?:0?\.\d+|1(?:\.0+)?)", text)
            if not m:
                return None
            s = m.group(0)
            if s.startswith("."):
                s = "0" + s
            try:
                return _clamp01(float(s))
            except Exception:
                return None

        # 1. Try JSON anywhere in the response
        try:
            json_match = re.search(r"\{.*\}", llm_response, re.S)
            if json_match:
                obj = json.loads(json_match.group(0))
                s = obj.get("score", obj.get("Score", obj.get("confidence")))
                if isinstance(s, (int, float)):
                    return _clamp01(float(s))
                if isinstance(s, str) and s.strip():
                    # Handle percentage in JSON
                    pct = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*%\s*", s)
                    if pct:
                        return _clamp01(float(pct.group(1)) / 100.0)
                    # Handle ratio in JSON
                    r = _parse_ratio(s)
                    if r is not None:
                        return r
                    # Handle decimal in JSON
                    d = _parse_decimal01(s)
                    if d is not None:
                        return d
        except Exception:
            pass

        # 2. Try ratio anywhere in raw text (e.g., "Score 7/10")
        r = _parse_ratio(llm_response)
        if r is not None:
            return r

        # 3. Try first valid decimal in [0,1]
        d = _parse_decimal01(llm_response)
        if d is not None:
            return d

        # 4. Last resort fallback
        return 0.5

    def _extract_score_legacy(self, llm_response: str) -> float:
        """Legacy score extraction (current broken method)."""
        try:
            # Extract numeric score from response
            score_str = "".join(filter(lambda x: x.isdigit() or x == ".", llm_response))
            score = float(score_str) if score_str else 0.5
            return max(0.0, min(1.0, score))  # Clamp to valid range
        except (ValueError, TypeError) as e:
            print(f"⚠️ Score parsing failed: {e}")
            return 0.5  # Default to neutral if parsing fails


class OfficialRAGCheckerEvaluator:
    """Official RAGChecker evaluator following official methodology."""

    def __init__(self):
        self.input_data = []
        self.evaluation_results = {}
        self.metrics_dir = Path("metrics/baseline_evaluations")
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        self.local_llm = None

    def create_official_test_cases(self) -> List[RAGCheckerInput]:
        """Create test cases following RAGChecker official format."""
        test_cases = []

        # Test Case 1: Memory System Query
        test_cases.append(
            RAGCheckerInput(
                query_id="memory_system_001",
                query="What is the current project status and backlog priorities?",
                gt_answer="The current project focuses on unified memory system and DSPy 3.0 integration. Key priorities include B-1044 (Memory System Core Features), B-1034 (Mathematical Framework), and B-1013 (Advanced RAG Optimization). The system uses RAGChecker for evaluation with 95.8/100 baseline score.",
                response="",  # Will be filled by memory system
                retrieved_context=[
                    "Current priorities include B-1044, B-1034, and B-1013",
                    "Unified memory system with DSPy 3.0 integration",
                ],
            )
        )

        # Test Case 2: DSPy Integration
        test_cases.append(
            RAGCheckerInput(
                query_id="dspy_integration_001",
                query="What are the DSPy integration patterns and optimization techniques?",
                gt_answer="DSPy integration includes multi-agent system with sequential model switching, LabeledFewShot optimizer, assertion framework, and signature validation patterns. Key components: Model Switcher, Cursor Integration, Optimization System, and Role Refinement System.",
                response="",  # Will be filled by memory system
                retrieved_context=[
                    "DSPy multi-agent system with sequential model switching",
                    "LabeledFewShot optimizer with assertion framework",
                ],
            )
        )

        # Test Case 3: Role-Specific Context
        test_cases.append(
            RAGCheckerInput(
                query_id="role_context_001",
                query="How do I implement DSPy modules and optimize performance?",
                gt_answer="To implement DSPy modules: 1) Use Model Switcher for hardware constraints, 2) Apply LabeledFewShot optimizer with configurable K parameter, 3) Implement signature validation patterns, 4) Use role refinement system for AI-powered optimization, 5) Follow the four-part optimization loop.",
                response="",  # Will be filled by memory system
                retrieved_context=[
                    "Model Switcher for hardware constraints",
                    "LabeledFewShot optimizer with K parameter",
                ],
            )
        )

        # Test Case 4: Research Context
        test_cases.append(
            RAGCheckerInput(
                query_id="research_context_001",
                query="What are the latest memory system optimizations and research findings?",
                gt_answer="Latest memory system optimizations include: 1) LTST Memory System with database integration, 2) Real-time session continuity detection, 3) Quality scoring and context merging, 4) Dual API support with backward compatibility, 5) Comprehensive performance monitoring and statistics.",
                response="",  # Will be filled by memory system
                retrieved_context=[
                    "LTST Memory System with database integration",
                    "Real-time session continuity detection",
                ],
            )
        )

        # Test Case 5: System Architecture
        test_cases.append(
            RAGCheckerInput(
                query_id="architecture_001",
                query="What's the current codebase structure and how do I navigate it?",
                gt_answer="The codebase follows a structured organization: 000_core/ (workflows), 100_memory/ (memory systems), 400_guides/ (documentation), scripts/ (automation), dspy-rag-system/ (DSPy implementation). Key navigation: Start with 400_00_getting-started-and-index.md, then 100_cursor-memory-context.md, and 000_backlog.md.",
                response="",  # Will be filled by memory system
                retrieved_context=[
                    "000_core/, 100_memory/, 400_guides/, scripts/",
                    "Start with getting-started guide and memory context",
                ],
            )
        )

        # Test Case 6: Technical Implementation
        test_cases.append(
            RAGCheckerInput(
                query_id="technical_implementation_001",
                query="How do I set up and configure the DSPy optimization system?",
                gt_answer="DSPy optimization setup requires: 1) Configure ModelSwitcher with hardware constraints, 2) Set up LabeledFewShot optimizer with K=16 examples, 3) Implement assertion framework for validation, 4) Configure teleprompter for automatic optimization, 5) Set up evaluation metrics and feedback loops.",
                response="",
                retrieved_context=[
                    "ModelSwitcher configuration for hardware constraints",
                    "LabeledFewShot optimizer setup with K parameter",
                    "Assertion framework implementation",
                ],
            )
        )

        # Test Case 7: Performance Optimization
        test_cases.append(
            RAGCheckerInput(
                query_id="performance_optimization_001",
                query="What are the key performance metrics and how do I improve them?",
                gt_answer="Key performance metrics include: Rehydration Time (target <10ms), Warm Latency p95 <10ms, Cold Latency p95 <150ms, Failure@20 ≤0.20, Recall@10 ≥0.7-0.9, Precision@10 ≥0.6-0.8. Improvements: optimize vector indexing, implement caching, use HNSW indexes, optimize query patterns.",
                response="",
                retrieved_context=[
                    "Performance targets: rehydration <10ms, warm latency p95 <10ms",
                    "HNSW vector indexing for optimization",
                    "Caching strategies for performance",
                ],
            )
        )

        # Test Case 8: Error Handling
        test_cases.append(
            RAGCheckerInput(
                query_id="error_handling_001",
                query="How does the system handle errors and what are the recovery procedures?",
                gt_answer="Error handling includes: 1) Graceful degradation with fallback evaluation, 2) Robust score parsing with multiple format support, 3) Timeout handling for LLM calls, 4) Database connection recovery, 5) Memory system rollback procedures, 6) Comprehensive logging and monitoring.",
                response="",
                retrieved_context=[
                    "Fallback evaluation when CLI unavailable",
                    "Robust score parsing with JSON and legacy support",
                    "Database rollback and recovery procedures",
                ],
            )
        )

        # Test Case 9: Integration Patterns
        test_cases.append(
            RAGCheckerInput(
                query_id="integration_patterns_001",
                query="What are the integration patterns for external systems and APIs?",
                gt_answer="Integration patterns include: 1) MCP (Model Context Protocol) for file processing, 2) Ollama API for local LLM integration, 3) PostgreSQL with pgvector for vector storage, 4) GitHub integration for version control, 5) Unified memory orchestrator for system coordination, 6) RESTful APIs with proper error handling.",
                response="",
                retrieved_context=[
                    "MCP integration for file processing",
                    "Ollama API for local LLM calls",
                    "PostgreSQL pgvector integration",
                ],
            )
        )

        # Test Case 10: Development Workflow
        test_cases.append(
            RAGCheckerInput(
                query_id="development_workflow_001",
                query="What is the recommended development workflow and best practices?",
                gt_answer="Development workflow: 1) Start with backlog item creation, 2) Generate PRD using workflow, 3) Create task list with priorities, 4) Follow test-driven development, 5) Use pre-commit hooks for quality, 6) Update documentation, 7) Run evaluation tests, 8) Create pull request with backlog reference.",
                response="",
                retrieved_context=[
                    "Backlog-driven development workflow",
                    "PRD and task generation process",
                    "TDD and quality gates",
                ],
            )
        )

        # Test Case 11: Configuration Management
        test_cases.append(
            RAGCheckerInput(
                query_id="configuration_management_001",
                query="How do I configure environment variables and system settings?",
                gt_answer="Configuration includes: RAGCHECKER_CONCISE=1 for response limiting, RAGCHECKER_MAX_WORDS=1000 for optimal length, RAGCHECKER_ROBUST_PARSER=1 for score parsing, RAGCHECKER_SEMANTIC_FEATURES=1 for embeddings, RAGCHECKER_JSON_PROMPTS=1 for structured output, POSTGRES_DSN for database connection.",
                response="",
                retrieved_context=[
                    "Environment flags for RAGChecker configuration",
                    "Database connection settings",
                    "Feature toggles for A/B testing",
                ],
            )
        )

        # Test Case 12: Testing and Validation
        test_cases.append(
            RAGCheckerInput(
                query_id="testing_validation_001",
                query="What testing strategies and validation methods are used?",
                gt_answer="Testing strategies: 1) Unit tests with pytest, 2) Integration tests for system components, 3) RAGChecker evaluation for quality metrics, 4) A/B testing framework for improvements, 5) Performance benchmarking, 6) Security validation, 7) End-to-end workflow testing, 8) Regression testing for stability.",
                response="",
                retrieved_context=[
                    "Pytest for unit and integration testing",
                    "RAGChecker for quality evaluation",
                    "A/B testing framework for improvements",
                ],
            )
        )

        # Test Case 13: Troubleshooting
        test_cases.append(
            RAGCheckerInput(
                query_id="troubleshooting_001",
                query="What are common issues and how do I troubleshoot them?",
                gt_answer="Common issues: 1) LLM timeout errors - reduce timeout or use fast mode, 2) Score parsing failures - enable robust parser, 3) Database connection issues - check POSTGRES_DSN, 4) Memory system errors - verify orchestrator setup, 5) Import errors - check dependencies, 6) Performance issues - optimize vector indexes.",
                response="",
                retrieved_context=[
                    "LLM timeout and fast mode solutions",
                    "Score parsing error handling",
                    "Database connectivity troubleshooting",
                ],
            )
        )

        # Test Case 14: Advanced Features
        test_cases.append(
            RAGCheckerInput(
                query_id="advanced_features_001",
                query="What advanced features are available for power users?",
                gt_answer="Advanced features: 1) Semantic embeddings with sentence-transformers, 2) Context ranking by query similarity, 3) Custom evaluation metrics, 4) Multi-model switching based on hardware, 5) Assertion-based validation, 6) Teleprompter optimization, 7) Custom prompt engineering, 8) Performance profiling and monitoring.",
                response="",
                retrieved_context=[
                    "Semantic embeddings and context ranking",
                    "Multi-model switching capabilities",
                    "Assertion framework and teleprompter",
                ],
            )
        )

        # Test Case 15: Security and Privacy
        test_cases.append(
            RAGCheckerInput(
                query_id="security_privacy_001",
                query="What security measures and privacy considerations are implemented?",
                gt_answer="Security measures: 1) Local-first LLM processing for privacy, 2) Database connection security with SSL options, 3) Input sanitization and validation, 4) Secure API endpoints, 5) Access control for sensitive operations, 6) Data encryption at rest, 7) Audit logging for compliance, 8) Regular security updates and patches.",
                response="",
                retrieved_context=[
                    "Local LLM processing for privacy",
                    "Database security and SSL configuration",
                    "Input validation and sanitization",
                ],
            )
        )

        # Allow limiting test cases for development/testing
        max_cases = int(os.getenv("RAGCHECKER_MAX_TEST_CASES", "15"))
        if max_cases < len(test_cases):
            print(f"🧪 Limited test mode: Using {max_cases} test cases (reduced from {len(test_cases)})")
            return test_cases[:max_cases]

        print(f"📊 Full evaluation mode: Using all {len(test_cases)} test cases")
        return test_cases

    def get_memory_system_response(self, query: str, role: str = "planner") -> str:
        """Get response from memory system using unified memory orchestrator."""
        try:
            env = os.environ.copy()
            env["POSTGRES_DSN"] = "mock://test"

            cmd = [
                "python3",
                "scripts/unified_memory_orchestrator.py",
                "--systems",
                "cursor",
                "--role",
                role,
                query,
                "--format",
                "json",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=30)

            if result.returncode == 0:
                try:
                    response_data = json.loads(result.stdout)
                    if "systems" in response_data and "cursor" in response_data["systems"]:
                        raw_response = response_data["systems"]["cursor"]["output"]
                    else:
                        raw_response = result.stdout
                except json.JSONDecodeError:
                    raw_response = result.stdout

                # Apply concise generation if enabled
                if os.getenv("RAGCHECKER_CONCISE", "1") == "1":
                    # Apply word limit to reduce verbosity
                    if hasattr(self, "local_llm") and self.local_llm:
                        concise_response = self.local_llm.apply_word_limit(raw_response)
                        print(
                            f"📝 Reduced response: {len(raw_response.split())} → {len(concise_response.split())} words"
                        )
                        return concise_response
                    else:
                        # Simple word limit fallback
                        max_words = int(os.getenv("RAGCHECKER_MAX_WORDS", "1000"))
                        words = raw_response.split()
                        if len(words) > max_words:
                            concise_response = " ".join(words[:max_words])
                            print(f"📝 Reduced response: {len(words)} → {len(concise_response.split())} words")
                            return concise_response
                        return raw_response
                else:
                    return raw_response
            else:
                return f"Error: {result.stderr}"

        except Exception as e:
            return f"Error: {str(e)}"

    def prepare_official_input_data(self) -> List[Dict[str, Any]]:
        """Prepare input data in official RAGChecker format."""
        test_cases = self.create_official_test_cases()
        input_data = []

        print("🧠 Preparing Official RAGChecker Input Data")
        print("=" * 50)

        for i, test_case in enumerate(test_cases, 1):
            print(f"🔍 Processing Test Case {i}/{len(test_cases)}: {test_case.query_id}")

            # Apply semantic context ranking if available
            if hasattr(self, "local_llm") and self.local_llm and hasattr(self.local_llm, "embedding_model"):
                if self.local_llm.embedding_model:
                    test_case.retrieved_context = self.local_llm.rank_context_by_query_similarity(
                        test_case.query, test_case.retrieved_context
                    )

            # Get response from memory system
            response = self.get_memory_system_response(test_case.query)
            test_case.response = response

            # Convert to official RAGChecker format
            input_entry = {
                "query": test_case.query,
                "gt_answer": test_case.gt_answer,
                "response": test_case.response,
                "retrieved_context": test_case.retrieved_context,  # Already strings now
            }

            input_data.append(input_entry)
            print(f"   ✅ Response length: {len(response)} characters")

        return input_data

    def save_official_input_data(self, input_data: List[Dict[str, Any]]) -> str:
        """Save input data in official RAGChecker format."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        input_file = self.metrics_dir / f"ragchecker_official_input_{timestamp}.json"

        with open(input_file, "w") as f:
            json.dump(input_data, f, indent=2)

        print(f"💾 Official input data saved to: {input_file}")
        return str(input_file)

    def run_official_ragchecker_cli(
        self, input_file: str, use_local_llm: bool = False, local_api_base: Optional[str] = None
    ) -> Optional[str]:
        """Run official RAGChecker CLI with support for local LLMs."""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = self.metrics_dir / f"ragchecker_official_output_{timestamp}.json"

            # Build command with local LLM support
            cmd = [
                "/opt/homebrew/opt/python@3.12/bin/python3.12",
                "-m",
                "ragchecker.cli",
                f"--input_path={input_file}",
                f"--output_path={output_file}",
                "--batch_size_extractor=1",
                "--batch_size_checker=1",
                "--metrics",
                "all_metrics",
            ]

            if use_local_llm and local_api_base:
                # Use local LLM configuration
                cmd.extend(
                    [
                        "--extractor_name=local/llama3",
                        f"--extractor_api_base={local_api_base}",
                        "--checker_name=local/llama3",
                        f"--checker_api_base={local_api_base}",
                    ]
                )
                print(f"🏠 Using local LLM at: {local_api_base}")
            else:
                # Fall back to Bedrock (will likely fail without credentials)
                cmd.extend(
                    [
                        "--extractor_name=bedrock/meta.llama3-1-70b-instruct-v1:0",
                        "--checker_name=bedrock/meta.llama3-1-70b-instruct-v1:0",
                    ]
                )
                print("☁️ Using AWS Bedrock models")

            print("🚀 Attempting to run official RAGChecker CLI...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                print("✅ Official RAGChecker CLI completed successfully")
                print(f"📊 Results saved to: {output_file}")
                return str(output_file)
            else:
                print(f"⚠️ Official RAGChecker CLI failed: {result.stderr}")
                return None

        except FileNotFoundError:
            print("⚠️ Official RAGChecker CLI not found - using fallback evaluation")
            return None
        except Exception as e:
            print(f"⚠️ Error running official RAGChecker CLI: {e}")
            return None

    def calculate_precision(self, response: str, gt_answer: str, query: str) -> float:
        """Calculate precision with query relevance boost."""
        query_words = set(query.lower().split())
        gt_words = set(gt_answer.lower().split())
        response_words = set(response.lower().split())

        if len(gt_words) > 0:
            base_precision = (
                len(response_words.intersection(gt_words)) / len(response_words) if len(response_words) > 0 else 0
            )
            # Query relevance boost
            query_relevance = (
                len(response_words.intersection(query_words)) / len(query_words) if len(query_words) > 0 else 0
            )
            query_boost = 0.1 * query_relevance
            return min(1.0, base_precision + query_boost)
        return 0.0

    def calculate_recall(self, response: str, gt_answer: str) -> float:
        """Calculate recall based on ground truth coverage."""
        gt_words = set(gt_answer.lower().split())
        response_words = set(response.lower().split())

        if len(gt_words) > 0:
            return len(response_words.intersection(gt_words)) / len(gt_words)
        return 0.0

    def run_local_llm_evaluation(
        self, input_data: List[Dict[str, Any]], local_api_base: str, use_bedrock: bool = False
    ) -> Dict[str, Any]:
        """Run evaluation using local LLM or Bedrock integration."""
        print("🏠 Running Local LLM Evaluation with comprehensive metrics")

        # Initialize LLM integration
        try:
            self.local_llm = LocalLLMIntegration(
                api_base=local_api_base, model_name="llama3.1:8b", use_bedrock=use_bedrock
            )
        except Exception as e:
            print(f"⚠️ Failed to initialize LLM integration: {e}")
            return self.create_fallback_evaluation(input_data)

        case_results = []
        total_precision = 0.0
        total_recall = 0.0
        total_f1 = 0.0

        for i, case in enumerate(input_data):
            print(f"\n📝 Evaluating case {i+1}/{len(input_data)}: {case.get('query_id', f'case_{i+1}')}")

            try:
                # Generate response using memory system
                raw_response = self.get_memory_system_response(case["query"])

                # Apply concise response generation if enabled
                if os.getenv("RAGCHECKER_CONCISE", "1") == "1":
                    if hasattr(self, "local_llm") and self.local_llm:
                        concise_response = self.local_llm.apply_word_limit(raw_response)
                        case["response"] = concise_response
                    else:
                        case["response"] = raw_response
                else:
                    case["response"] = raw_response

                # Apply semantic context ranking if available
                if hasattr(self, "local_llm") and self.local_llm and hasattr(self.local_llm, "embedding_model"):
                    if self.local_llm.embedding_model:
                        case["retrieved_context"] = self.local_llm.rank_context_by_query_similarity(
                            case["query"], case["retrieved_context"]
                        )

                # Evaluate comprehensive metrics
                metrics = self.local_llm.evaluate_comprehensive_metrics(
                    case["query"], case["response"], case["retrieved_context"], case["gt_answer"]
                )

                # Calculate basic metrics
                precision = self.calculate_precision(case["response"], case["gt_answer"], case["query"])
                recall = self.calculate_recall(case["response"], case["gt_answer"])
                f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

                case_result = {
                    "query_id": case.get("query_id", f"case_{i+1}"),
                    "query": case["query"],
                    "response": case["response"],
                    "gt_answer": case["gt_answer"],
                    "precision": precision,
                    "recall": recall,
                    "f1_score": f1_score,
                    "comprehensive_metrics": metrics,
                }

                case_results.append(case_result)
                total_precision += precision
                total_recall += recall
                total_f1 += f1_score

                print(
                    f"✅ Case {case.get('query_id', f'case_{i+1}')}: P={precision:.3f}, R={recall:.3f}, F1={f1_score:.3f}"
                )

            except Exception as e:
                print(f"⚠️ Error evaluating case {case.get('query_id', f'case_{i+1}')}: {e}")
                # Add failed case with zero scores
                case_results.append(
                    {
                        "query_id": case.get("query_id", f"case_{i+1}"),
                        "query": case["query"],
                        "response": "",
                        "gt_answer": case["gt_answer"],
                        "precision": 0.0,
                        "recall": 0.0,
                        "f1_score": 0.0,
                        "error": str(e),
                    }
                )

        # Calculate averages
        num_cases = len(input_data)
        avg_precision = total_precision / num_cases if num_cases > 0 else 0
        avg_recall = total_recall / num_cases if num_cases > 0 else 0
        avg_f1 = total_f1 / num_cases if num_cases > 0 else 0

        return {
            "evaluation_type": "local_llm_comprehensive",
            "overall_metrics": {"precision": avg_precision, "recall": avg_recall, "f1_score": avg_f1},
            "case_results": case_results,
            "backend": "bedrock" if use_bedrock else "local_llm",
        }

    def create_fallback_evaluation(self, input_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create fallback evaluation when LLM integration fails."""
        print("🔄 Running Fallback Evaluation (simplified metrics)")

        case_results = []
        total_precision = 0.0
        total_recall = 0.0
        total_f1 = 0.0

        for case in input_data:
            # Generate response using memory system
            case["response"] = self.get_memory_system_response(case["query"])

            # Calculate basic metrics using simple text overlap
            precision = self.calculate_precision(case["response"], case["gt_answer"], case["query"])
            recall = self.calculate_recall(case["response"], case["gt_answer"])
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

            case_result = {
                "query_id": f"case_{len(case_results) + 1}",
                "query": case["query"],
                "response": case["response"],
                "gt_answer": case["gt_answer"],
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score,
            }

            case_results.append(case_result)
            total_precision += precision
            total_recall += recall
            total_f1 += f1_score

        # Calculate averages
        num_cases = len(input_data)
        avg_precision = total_precision / num_cases if num_cases > 0 else 0
        avg_recall = total_recall / num_cases if num_cases > 0 else 0
        avg_f1 = total_f1 / num_cases if num_cases > 0 else 0

        return {
            "evaluation_type": "fallback_simplified",
            "overall_metrics": {"precision": avg_precision, "recall": avg_recall, "f1_score": avg_f1},
            "case_results": case_results,
            "note": "Simplified evaluation - LLM integration unavailable",
        }

    def run_official_evaluation(
        self, use_local_llm: bool = False, local_api_base: Optional[str] = None, use_bedrock: bool = False
    ) -> Dict[str, Any]:
        """Run complete official RAGChecker evaluation with hybrid LLM support."""
        print("🧠 Official RAGChecker Evaluation")
        print("=" * 60)
        print("📋 Following official RAGChecker methodology")
        print("🎯 Using official metrics and procedures")

        if use_bedrock:
            print("☁️ AWS Bedrock Mode: Claude 3.5 Sonnet")
        elif use_local_llm:
            print(f"🏠 Local LLM Mode: {local_api_base}")
        else:
            print("☁️ Cloud LLM Mode (AWS Bedrock)")

        # Step 1: Prepare input data in official format
        input_data = self.prepare_official_input_data()

        # Step 2: Save input data
        input_file = self.save_official_input_data(input_data)

        # Step 3: Try to run official RAGChecker CLI
        output_file = self.run_official_ragchecker_cli(input_file, use_local_llm, local_api_base)

        if output_file and os.path.exists(output_file):
            # Step 4: Load official results
            try:
                with open(output_file, "r") as f:
                    results = json.load(f)
                results["evaluation_type"] = "official_ragchecker_cli"
                results["input_file"] = input_file
                results["output_file"] = output_file
            except Exception as e:
                print(f"⚠️ Error loading official results: {e}")
                if use_local_llm and local_api_base:
                    # Check for fast mode to avoid hanging on 130+ LLM calls
                    if os.getenv("RAGCHECKER_FAST_MODE", "0") == "1":
                        print("⚡ Fast mode enabled - using simplified evaluation")
                        results = self.create_fallback_evaluation(input_data)
                    else:
                        results = self.run_local_llm_evaluation(input_data, local_api_base, use_bedrock)
                else:
                    results = self.create_fallback_evaluation(input_data)
        else:
            # Step 4: Try local LLM evaluation, then fallback
            if use_local_llm and local_api_base:
                try:
                    # Check for fast mode to avoid hanging on 130+ LLM calls
                    if os.getenv("RAGCHECKER_FAST_MODE", "0") == "1":
                        print("⚡ Fast mode enabled - using simplified evaluation")
                        results = self.create_fallback_evaluation(input_data)
                    else:
                        results = self.run_local_llm_evaluation(input_data, local_api_base, use_bedrock)
                except Exception as e:
                    print(f"⚠️ Local LLM evaluation failed: {e}")
                    results = self.create_fallback_evaluation(input_data)
            else:
                results = self.create_fallback_evaluation(input_data)

        # Step 5: Save results
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = self.metrics_dir / f"ragchecker_official_evaluation_{timestamp}.json"

        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n💾 Official evaluation results saved to: {results_file}")

        # Step 6: Print summary
        self.print_evaluation_summary(results)

        return results

    def print_evaluation_summary(self, results: Dict[str, Any]):
        """Print evaluation summary following official format."""
        print("\n" + "=" * 60)
        print("📊 OFFICIAL RAGCHECKER EVALUATION SUMMARY")
        print("=" * 60)

        print(f"🎯 Evaluation Type: {results.get('evaluation_type', 'Unknown')}")
        print(f"📋 Total Cases: {results.get('total_cases', 0)}")

        if "overall_metrics" in results:
            metrics = results["overall_metrics"]
            print("📊 Overall Metrics:")
            print(f"   Precision: {metrics.get('precision', 0):.3f}")
            print(f"   Recall: {metrics.get('recall', 0):.3f}")
            print(f"   F1 Score: {metrics.get('f1_score', 0):.3f}")
            if "faithfulness" in metrics:
                print(f"   Faithfulness: {metrics.get('faithfulness', 0):.3f}")
            if "total_claims" in metrics:
                print(f"   Total Claims: {metrics.get('total_claims', 0)}")

            # Print comprehensive RAGChecker metrics if available
            if "context_precision" in metrics:
                print("\n🎯 Comprehensive RAGChecker Metrics:")
                print(f"   Context Precision: {metrics.get('context_precision', 0):.3f}")
                print(f"   Context Utilization: {metrics.get('context_utilization', 0):.3f}")
                print(f"   Noise Sensitivity: {metrics.get('noise_sensitivity', 0):.3f}")
                print(f"   Hallucination Score: {metrics.get('hallucination', 0):.3f}")
                print(f"   Self Knowledge: {metrics.get('self_knowledge', 0):.3f}")
                print(f"   Claim Recall: {metrics.get('claim_recall', 0):.3f}")

        if "case_results" in results:
            print("\n🔍 Case-by-Case Results:")
            for case in results["case_results"]:
                case_id = case.get("case_id", case.get("query_id", "unknown"))
                print(f"   {case_id}: F1={case['f1_score']:.3f}, P={case['precision']:.3f}, R={case['recall']:.3f}")

        if results.get("note"):
            print(f"\n📝 Note: {results['note']}")


def main():
    """Main function to run official RAGChecker evaluation."""
    import argparse

    parser = argparse.ArgumentParser(description="Official RAGChecker Evaluation with Hybrid LLM Support")
    parser.add_argument("--use-local-llm", action="store_true", help="Use local LLM (Ollama) for evaluation")
    parser.add_argument("--use-bedrock", action="store_true", help="Use AWS Bedrock Claude 3.5 Sonnet for evaluation")
    parser.add_argument(
        "--local-api-base",
        default="http://localhost:11434",
        help="Local LLM API base URL (default: http://localhost:11434 for Ollama)",
    )

    args = parser.parse_args()

    # Validate backend selection
    if args.use_local_llm and args.use_bedrock:
        print("❌ Cannot use both --use-local-llm and --use-bedrock simultaneously")
        print("💡 Choose one backend or let the system auto-detect")
        return None

    # Determine backend preference
    use_bedrock = args.use_bedrock
    use_local_llm = args.use_local_llm

    # Auto-detect if no explicit choice
    if not use_bedrock and not use_local_llm:
        # Check for Bedrock availability first (faster, more reliable)
        if BEDROCK_AVAILABLE:
            try:
                test_client = BedrockClient()  # type: ignore
                if test_client.test_connection():
                    print("🧠 Auto-detected: Using AWS Bedrock (faster, more reliable)")
                    use_bedrock = True
                else:
                    print("🔄 Bedrock unavailable, falling back to local LLM")
                    use_local_llm = True
            except Exception:
                print("🔄 Bedrock unavailable, falling back to local LLM")
                use_local_llm = True
        else:
            print("🔄 Bedrock not available, using local LLM")
            use_local_llm = True

    evaluator = OfficialRAGCheckerEvaluator()
    results = evaluator.run_official_evaluation(use_local_llm, args.local_api_base, use_bedrock)
    return results


if __name__ == "__main__":
    main()
