#!/usr/bin/env python3
"""
Model Switcher for DSPy Multi-Agent System

Implements sequential model switching to enable multi-model orchestration
within hardware constraints. Loads/unloads models based on task requirements.
Enhanced with full DSPy signatures, optimization, and structured programming.
"""

import logging
import os
import sys
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import dspy
from dspy import LM, InputField, Module, OutputField, Signature

_LOG = logging.getLogger("model_switcher")

# Import monitoring system
try:
    import os
    import sys

    # Add utils to path for monitoring import
    utils_path = os.path.join(os.path.dirname(__file__), "..", "utils")
    if utils_path not in sys.path:
        sys.path.insert(0, utils_path)

    from context_monitoring import get_context_monitor, record_context_request

    MONITORING_AVAILABLE = True
except ImportError as e:
    MONITORING_AVAILABLE = False
    _LOG.warning(f"Context monitoring not available: {e}")

# Import performance optimization system
try:
    from context_performance import get_optimized_context, get_performance_optimizer

    PERFORMANCE_OPTIMIZATION_AVAILABLE = True
except ImportError as e:
    PERFORMANCE_OPTIMIZATION_AVAILABLE = False
    _LOG.warning(f"Performance optimization not available: {e}")

# Import security validation system
try:
    from context_security import get_security_stats, validate_context_request

    SECURITY_VALIDATION_AVAILABLE = True
except ImportError as e:
    SECURITY_VALIDATION_AVAILABLE = False
    _LOG.warning(f"Security validation not available: {e}")

# Context integration using subprocess to avoid import issues
MEMORY_REHYDRATOR_AVAILABLE = True

# Scribe integration for real-time context
try:
    from ..utils.scribe_context_provider import ScribeContextProvider, get_scribe_context_for_role

    SCRIBE_AVAILABLE = True
    _LOG.info("Scribe context provider available")
except ImportError as e:
    SCRIBE_AVAILABLE = False
    _LOG.warning(f"Scribe context provider not available: {e}")

# Simple cache for context to avoid repeated subprocess calls
_context_cache = {}
_cache_ttl = 300  # 5 minutes TTL
_failure_count = {}  # Track failures per role
_max_failures = 3  # Max failures before disabling context for role


def get_context_for_role(role: str, task: str) -> str:
    """
    Get context for a specific role and task using memory rehydrator via subprocess.
    Enhanced with Scribe real-time context integration.

    Args:
        role: AI role (planner, implementer, coder, researcher, reviewer)
        task: Task description

    Returns:
        Context string for the role and task with real-time Scribe data
    """
    if not MEMORY_REHYDRATOR_AVAILABLE:
        return _get_fallback_context(role, task)

    # Security validation
    if SECURITY_VALIDATION_AVAILABLE:
        is_valid, message = validate_context_request(role, task, "default")
        if not is_valid:
            _LOG.warning(f"Security validation failed: {message}")
            return _get_fallback_context(role, task)

    # Check if this role has exceeded failure threshold
    if _failure_count.get(role, 0) >= _max_failures:
        _LOG.warning(f"Role {role} has exceeded failure threshold, using fallback context")
        return _get_fallback_context(role, task)

    # Get Scribe real-time context if available
    scribe_context = ""
    if SCRIBE_AVAILABLE:
        try:
            scribe_data = get_scribe_context_for_role(role)
            if scribe_data and not scribe_data.get("error"):
                scribe_context = _format_scribe_context(scribe_data, role)
                _LOG.info(f"Successfully integrated Scribe context for {role}")
            else:
                _LOG.warning(f"Scribe context unavailable for {role}: {scribe_data.get('error', 'Unknown error')}")
        except Exception as e:
            _LOG.warning(f"Error getting Scribe context for {role}: {e}")

    # Use performance optimization if available
    if PERFORMANCE_OPTIMIZATION_AVAILABLE:
        try:
            import asyncio

            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                context = loop.run_until_complete(get_optimized_context(role, task))
                return context
            finally:
                loop.close()
        except Exception as e:
            _LOG.warning(f"Performance optimization failed, falling back to standard method: {e}")
            # Fall back to standard method

    # Check cache first
    cache_key = f"{role}:{task[:100]}"  # Truncate long tasks
    current_time = time.time()

    if cache_key in _context_cache:
        cached_entry = _context_cache[cache_key]
        if current_time - cached_entry["timestamp"] < _cache_ttl:
            _LOG.info(f"Using cached context for role {role}")

            # Record monitoring metrics for cache hit
            if MONITORING_AVAILABLE:
                record_context_request(
                    role=role,
                    task=task,
                    start_time=time.time(),
                    success=True,
                    response_time=0.001,  # Very fast for cache hits
                    cache_hit=True,
                    fallback_used=False,
                )

            # Add Scribe context to cached context if available
            if SCRIBE_AVAILABLE and scribe_context:
                cached_context = cached_entry["context"]
                enhanced_context = f"{cached_context}\n\nREAL-TIME SCRIBE CONTEXT:\n{scribe_context}"
                _LOG.info(f"Added Scribe context to cached context for {role}")
                return enhanced_context
            return cached_entry["context"]
        else:
            # Remove expired entry
            del _context_cache[cache_key]

    # Retry logic for memory rehydrator
    max_retries = 2
    request_start_time = time.time()

    for attempt in range(max_retries + 1):
        try:
            import subprocess

            # Track timing for optimization
            start_time = time.time()

            # Run memory rehydrator via subprocess with optimizations
            cmd = [sys.executable, "scripts/cursor_memory_rehydrate.py", role, task, "--stability", "0.4"]

            # Change to project root directory
            current_dir = os.getcwd()
            project_root = os.path.join(current_dir, "..")

            # Optimize subprocess call with reduced timeout and fast mode
            env = os.environ.copy()
            env["REHYDRATE_FAST"] = "1"  # Enable fast mode

            # Progressive timeout reduction on retries
            timeout = 10 - (attempt * 2)  # 10s, 8s, 6s
            timeout = max(timeout, 4)  # Minimum 4s

            result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, timeout=timeout, env=env)

            context_time = time.time() - start_time
            _LOG.info(f"Context retrieval took {context_time:.2f}s for role {role} (attempt {attempt + 1})")

            if result.returncode == 0:
                # Parse the output to extract context
                output = result.stdout

                # Look for the bundle content in the output
                context = ""
                if "MEMORY REHYDRATION BUNDLE" in output:
                    # Extract the bundle content
                    start_marker = "================================================================================\n🧠 MEMORY REHYDRATION BUNDLE\n================================================================================\nCopy the content below into your Cursor conversation:\n================================================================================\n"
                    end_marker = "\n================================================================================\n📊 Bundle Statistics:"

                    start_idx = output.find(start_marker)
                    if start_idx != -1:
                        start_idx += len(start_marker)
                        end_idx = output.find(end_marker, start_idx)
                        if end_idx != -1:
                            bundle_content = output[start_idx:end_idx].strip()
                            context = f"PROJECT CONTEXT:\n{bundle_content}"

                # Fallback context if bundle not found
                if not context:
                    context = _get_fallback_context(role, task)

                # Cache the context for future use
                _context_cache[cache_key] = {"context": context, "timestamp": current_time}

                # Reset failure count on success
                if role in _failure_count:
                    del _failure_count[role]

                # Add Scribe real-time context if available
                if SCRIBE_AVAILABLE and scribe_context:
                    context = f"{context}\n\nREAL-TIME SCRIBE CONTEXT:\n{scribe_context}"
                    _LOG.info(f"Added Scribe context to {role} role context")
                    _LOG.debug(f"Scribe context length: {len(scribe_context)} characters")

                # Record monitoring metrics
                if MONITORING_AVAILABLE:
                    total_time = time.time() - request_start_time
                    record_context_request(
                        role=role,
                        task=task,
                        start_time=request_start_time,
                        success=True,
                        response_time=total_time,
                        cache_hit=False,
                        fallback_used=False,
                    )

                return context
            else:
                # Log specific error details
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                _LOG.warning(f"Memory rehydrator failed on attempt {attempt + 1}: {error_msg}")

                # If this is the last attempt, increment failure count
                if attempt == max_retries:
                    _failure_count[role] = _failure_count.get(role, 0) + 1
                    _LOG.error(f"Memory rehydrator failed after {max_retries + 1} attempts for role {role}")

                    # Record monitoring metrics for failure
                    if MONITORING_AVAILABLE:
                        total_time = time.time() - request_start_time
                        record_context_request(
                            role=role,
                            task=task,
                            start_time=request_start_time,
                            success=False,
                            response_time=total_time,
                            cache_hit=False,
                            error_type="subprocess",
                            fallback_used=True,
                        )

                    return _get_fallback_context(role, task)
                else:
                    # Wait briefly before retry
                    time.sleep(0.5 * (attempt + 1))  # Progressive backoff
                    continue

        except subprocess.TimeoutExpired:
            _LOG.warning(f"Memory rehydrator timeout on attempt {attempt + 1} for role {role}")
            if attempt == max_retries:
                _failure_count[role] = _failure_count.get(role, 0) + 1

                # Record monitoring metrics for timeout
                if MONITORING_AVAILABLE:
                    total_time = time.time() - request_start_time
                    record_context_request(
                        role=role,
                        task=task,
                        start_time=request_start_time,
                        success=False,
                        response_time=total_time,
                        cache_hit=False,
                        error_type="timeout",
                        fallback_used=True,
                    )

                return _get_fallback_context(role, task)
            else:
                time.sleep(0.5 * (attempt + 1))
                continue

        except Exception as e:
            _LOG.error(f"Memory rehydrator error on attempt {attempt + 1} for role {role}: {e}")
            if attempt == max_retries:
                _failure_count[role] = _failure_count.get(role, 0) + 1

                # Record monitoring metrics for general error
                if MONITORING_AVAILABLE:
                    total_time = time.time() - request_start_time
                    record_context_request(
                        role=role,
                        task=task,
                        start_time=request_start_time,
                        success=False,
                        response_time=total_time,
                        cache_hit=False,
                        error_type="general",
                        fallback_used=True,
                    )

                return _get_fallback_context(role, task)
            else:
                time.sleep(0.5 * (attempt + 1))
                continue

    # Fallback if all retries failed
    return _get_fallback_context(role, task)


def _format_scribe_context(scribe_data: Dict[str, Any], role: str) -> str:
    """
    Format Scribe context data into a readable string for DSPy roles.

    Args:
        scribe_data: Scribe context data dictionary
        role: The DSPy role

    Returns:
        Formatted context string
    """
    try:
        context_parts = []

        # Add role-specific focus
        role_focus = scribe_data.get("role_focus", {})
        if role_focus:
            context_parts.append(f"Role Focus: {role_focus.get('focus', 'General')}")
            context_parts.append(f"Context Priority: {role_focus.get('context_priority', 'low')}")

        # Add active sessions
        base_context = scribe_data.get("base_context", {})
        active_sessions = base_context.get("active_sessions", [])
        if active_sessions:
            session_info = [f"Active Sessions: {len(active_sessions)}"]
            for session in active_sessions[:3]:  # Limit to 3 sessions
                session_info.append(f"  - {session.get('backlog_id', 'Unknown')}: {session.get('status', 'Unknown')}")
            context_parts.extend(session_info)

        # Add current work context
        current_work = scribe_data.get("current_work", {})
        if current_work:
            context_parts.append(f"Current Branch: {current_work.get('current_branch', 'Unknown')}")
            context_parts.append(f"Recent Changes: {current_work.get('recent_changes', 0)} files")
            context_parts.append(f"Worklog Entries: {current_work.get('worklog_entries', 0)} recent")

        # Add relevant sessions for this role
        relevant_sessions = scribe_data.get("relevant_sessions", [])
        if relevant_sessions:
            context_parts.append(f"Relevant Sessions for {role}: {len(relevant_sessions)}")

        # Add timestamp
        timestamp = base_context.get("timestamp", "")
        if timestamp:
            context_parts.append(f"Context Updated: {timestamp}")

        return "\n".join(context_parts) if context_parts else ""

    except Exception as e:
        _LOG.error(f"Error formatting Scribe context: {e}")
        return ""


def _get_fallback_context(role: str, task: str) -> str:
    """
    Get fallback context when memory rehydrator is unavailable or fails.

    Args:
        role: AI role (planner, implementer, coder, researcher)
        task: Task description

    Returns:
        Role-specific fallback context
    """
    role_contexts = {
        "coder": """PROJECT CONTEXT (FALLBACK):
You are a Python developer working on an AI development ecosystem project.

Key Guidelines:
• Follow PEP 8 coding standards
• Use type hints (Python 3.12+ with PEP 585 built-in generics)
• Add comprehensive docstrings (Google style)
• Implement proper error handling with try/except blocks
• Use absolute imports and avoid sys.path manipulation
• Write tests first (TDD approach)
• Follow the project's existing patterns and conventions
• Use Ruff for linting and Black for formatting

Best Practices:
• Keep functions focused and single-purpose
• Use descriptive variable and function names
• Add logging for debugging and monitoring
• Handle edge cases and validate inputs
• Write secure code following OWASP guidelines""",
        "planner": """PROJECT CONTEXT (FALLBACK):
You are a strategic planner for an AI development ecosystem project.

Focus Areas:
• Strategic planning and task prioritization
• System architecture and design decisions
• Project roadmap and milestone planning
• Risk assessment and mitigation strategies
• Resource allocation and optimization

Key Considerations:
• Balance between local and cloud AI models
• Hardware constraints (Mac M4 Silicon, 128GB RAM)
• Performance vs. quality trade-offs
• Maintainability and scalability
• Integration with existing workflows""",
        "implementer": """PROJECT CONTEXT (FALLBACK):
You are a system implementer for an AI development ecosystem project.

Technical Focus:
• DSPy framework integration and optimization
• Multi-agent system architecture
• Database and vector store management
• Workflow automation and scripting
• Performance monitoring and optimization

Implementation Guidelines:
• Use DSPy for structured AI programming
• Implement proper error handling and resilience
• Design for scalability and maintainability
• Follow the project's coding standards
• Document implementation decisions""",
        "researcher": """PROJECT CONTEXT (FALLBACK):
You are a researcher for an AI development ecosystem project.

Research Areas:
• AI model capabilities and limitations
• Performance benchmarking and analysis
• Integration patterns and best practices
• Emerging technologies and frameworks
• Security and privacy considerations

Research Approach:
• Evidence-based analysis and recommendations
• Systematic evaluation of alternatives
• Documentation of findings and insights
• Consideration of real-world constraints""",
        "reviewer": """PROJECT CONTEXT (FALLBACK):
You are a code reviewer for an AI development ecosystem project.

Review Focus:
• Code quality and maintainability
• Security vulnerabilities and best practices
• Performance implications and optimizations
• Architecture and design patterns
• Testing coverage and quality

Review Standards:
• Follow established coding standards (PEP 8, type hints)
• Ensure proper error handling and edge cases
• Verify documentation and comments
• Check for security issues and vulnerabilities
• Validate testing and quality assurance""",
    }

    fallback = role_contexts.get(role, role_contexts["coder"])
    _LOG.info(f"Using fallback context for role {role}")
    return fallback


# ---------- DSPy Signatures ----------


class LocalTaskSignature(Signature):
    """Signature for local model task execution with structured I/O"""

    task = InputField(desc="The task to perform")
    task_type = InputField(desc="Type of task (planning, coding, analysis, etc.)")
    role = InputField(desc="AI role (planner, implementer, coder, researcher)")
    complexity = InputField(desc="Task complexity (simple, moderate, complex)")

    result = OutputField(desc="Task execution result")
    confidence = OutputField(desc="Confidence score (0-1)")
    model_used = OutputField(desc="Model that was used for this task")
    reasoning = OutputField(desc="Reasoning for model selection and approach")


class MultiModelOrchestrationSignature(Signature):
    """Signature for multi-model task orchestration"""

    task = InputField(desc="The main task to orchestrate")
    task_type = InputField(desc="Type of task")
    role = InputField(desc="Primary AI role")

    plan = OutputField(desc="Planning phase result")
    execution = OutputField(desc="Execution phase result")
    review = OutputField(desc="Review phase result")
    final_result = OutputField(desc="Final orchestrated result")
    orchestration_notes = OutputField(desc="Notes about the orchestration process")


class ModelSelectionSignature(Signature):
    """Signature for intelligent model selection"""

    task = InputField(desc="Task description")
    task_type = InputField(desc="Type of task")
    complexity = InputField(desc="Task complexity")
    context_size = InputField(desc="Estimated context size")

    selected_model = OutputField(desc="Selected model for the task")
    reasoning = OutputField(desc="Reasoning for model selection")
    confidence = OutputField(desc="Confidence in selection (0-1)")
    expected_performance = OutputField(desc="Expected performance characteristics")


# ---------- Model Definitions ----------


class LocalModel(Enum):
    """Available local models for switching"""

    LLAMA_3_1_8B = "llama3.1:8b"
    MISTRAL_7B = "mistral:7b"
    PHI_3_5_3_8B = "phi3.5:3.8b"


@dataclass
class ModelCapabilities:
    """Capabilities and characteristics of each local model"""

    model: LocalModel
    max_context: int
    reasoning_strength: float  # 0-1
    code_generation: float  # 0-1
    speed: float  # 0-1 (higher = faster)
    memory_usage_gb: float
    best_for: List[str]
    load_time_seconds: float


# ---------- Model Capabilities Configuration ----------

LOCAL_MODEL_CAPABILITIES = {
    LocalModel.LLAMA_3_1_8B: ModelCapabilities(
        model=LocalModel.LLAMA_3_1_8B,
        max_context=8192,
        reasoning_strength=0.8,
        code_generation=0.8,
        speed=0.85,
        memory_usage_gb=16.0,
        best_for=["planning", "research", "reasoning", "moderate_coding"],
        load_time_seconds=15.0,
    ),
    LocalModel.MISTRAL_7B: ModelCapabilities(
        model=LocalModel.MISTRAL_7B,
        max_context=8192,
        reasoning_strength=0.75,
        code_generation=0.8,
        speed=0.95,
        memory_usage_gb=14.0,
        best_for=["fast_completions", "quick_tasks", "rapid_prototyping", "light_coding"],
        load_time_seconds=10.0,
    ),
    LocalModel.PHI_3_5_3_8B: ModelCapabilities(
        model=LocalModel.PHI_3_5_3_8B,
        max_context=128000,
        reasoning_strength=0.8,
        code_generation=0.85,
        speed=0.85,
        memory_usage_gb=8.0,
        best_for=["large_context", "documentation_analysis", "memory_rehydration"],
        load_time_seconds=8.0,
    ),
}

# ---------- Task Type to Model Mapping ----------

TASK_MODEL_MAPPING = {
    "planning": LocalModel.LLAMA_3_1_8B,
    "research": LocalModel.LLAMA_3_1_8B,
    "reasoning": LocalModel.LLAMA_3_1_8B,
    "fast_completion": LocalModel.MISTRAL_7B,
    "quick_task": LocalModel.MISTRAL_7B,
    "rapid_prototyping": LocalModel.MISTRAL_7B,
    "light_coding": LocalModel.MISTRAL_7B,
    "large_context": LocalModel.PHI_3_5_3_8B,
    "documentation_analysis": LocalModel.PHI_3_5_3_8B,
    "memory_rehydration": LocalModel.PHI_3_5_3_8B,
    "moderate_coding": LocalModel.LLAMA_3_1_8B,
}

# ---------- Model Switcher Class ----------


class ModelSwitcher:
    """Manages model switching for DSPy multi-agent system"""

    def __init__(self, ollama_base_url: str = "http://localhost:11434"):
        """
        Initialize the model switcher.

        Args:
            ollama_base_url: Base URL for Ollama API
        """
        self.ollama_base_url = ollama_base_url
        self.current_model: Optional[LocalModel] = None
        self.current_lm: Optional[LM] = None
        self.model_load_times: Dict[LocalModel, float] = {}
        self.switch_count = 0

        # Initialize DSPy configuration
        self._configure_dspy()

    def _configure_dspy(self):
        """Configure DSPy with Ollama integration"""
        try:
            # Test connection to Ollama
            import requests

            response = requests.get(f"{self.ollama_base_url}/api/tags")
            if response.status_code == 200:
                _LOG.info("Ollama connection successful")
                # Initialize with default model
                self.switch_model(LocalModel.LLAMA_3_1_8B)
            else:
                _LOG.warning("Ollama connection failed, will use cloud fallback")
        except Exception as e:
            _LOG.warning(f"Ollama not available: {e}")

    def switch_model(self, model: LocalModel) -> bool:
        """
        Switch to a specific model.

        Args:
            model: Model to switch to

        Returns:
            True if switch successful, False otherwise
        """
        if self.current_model == model:
            _LOG.debug(f"Already using {model.value}")
            return True

        _LOG.info(f"Switching from {self.current_model.value if self.current_model else 'none'} to {model.value}")

        try:
            # Create new DSPy LM for the model using Ollama provider
            self.current_lm = dspy.LM(
                model=f"ollama/{model.value}",
                temperature=0.0,
                max_tokens=4096,
            )

            # Configure DSPy to use the new model
            dspy.configure(lm=self.current_lm)

            self.current_model = model
            self.switch_count += 1

            # Record load time
            start_time = time.time()
            # Test the model with a simple query
            self.current_lm("Test")
            load_time = time.time() - start_time
            self.model_load_times[model] = load_time

            _LOG.info(f"Successfully switched to {model.value} (load time: {load_time:.2f}s)")
            return True

        except Exception as e:
            _LOG.error(f"Failed to switch to {model.value}: {e}")
            return False

    def get_model_for_task(self, task_type: str, complexity: str = "moderate") -> LocalModel:
        """
        Get the best model for a given task type.

        Args:
            task_type: Type of task
            complexity: Task complexity (simple, moderate, complex)

        Returns:
            Recommended model for the task
        """
        # Direct mapping for specific task types
        if task_type in TASK_MODEL_MAPPING:
            return TASK_MODEL_MAPPING[task_type]

        # Fallback based on complexity
        if complexity == "simple":
            return LocalModel.MISTRAL_7B  # Fastest for simple tasks
        elif complexity == "complex":
            return LocalModel.LLAMA_3_1_8B  # Best reasoning for complex tasks
        else:
            return LocalModel.LLAMA_3_1_8B  # Default for moderate complexity

    def get_model_for_role(self, role: str) -> LocalModel:
        """
        Get the best model for a given role.

        Args:
            role: AI role (planner, implementer, coder, researcher)

        Returns:
            Recommended model for the role
        """
        role_model_mapping = {
            "planner": LocalModel.LLAMA_3_1_8B,  # Good reasoning for planning
            "implementer": LocalModel.MISTRAL_7B,  # Fast for implementation
            "coder": LocalModel.LLAMA_3_1_8B,  # Good code generation
            "researcher": LocalModel.LLAMA_3_1_8B,  # Good reasoning for research
            "reviewer": LocalModel.PHI_3_5_3_8B,  # Large context for review
        }

        return role_model_mapping.get(role, LocalModel.LLAMA_3_1_8B)

    def _analyze_task_content(self, task: str) -> LocalModel:
        """
        Analyze task content to determine the best model.

        Args:
            task: The task description

        Returns:
            Recommended model based on task content
        """
        task_lower = task.lower()

        # Quick/simple tasks → Mistral 7B (fastest)
        if any(word in task_lower for word in ["quick", "simple", "fast", "prototype", "basic", "easy"]):
            return LocalModel.MISTRAL_7B

        # Large context tasks → Phi-3.5 3.8B (largest context)
        if any(word in task_lower for word in ["analyze", "review", "large", "document", "comprehensive", "detailed"]):
            return LocalModel.PHI_3_5_3_8B

        # Planning/reasoning tasks → Llama 3.1 8B (best reasoning)
        if any(word in task_lower for word in ["plan", "design", "architecture", "strategy", "complex", "algorithm"]):
            return LocalModel.LLAMA_3_1_8B

        # Default to Llama 3.1 8B for general tasks (best overall capability)
        return LocalModel.LLAMA_3_1_8B

    def select_model_for_task(
        self, task: str, task_type: Optional[str] = None, role: Optional[str] = None
    ) -> LocalModel:
        """
        Select the best model for a task using intelligent analysis.

        Args:
            task: The task description
            task_type: Type of task (optional)
            role: AI role (optional)

        Returns:
            Recommended model for the task
        """
        # Priority 1: Explicit role assignment
        if role:
            return self.get_model_for_role(role)

        # Priority 2: Task type mapping
        if task_type and task_type in TASK_MODEL_MAPPING:
            return TASK_MODEL_MAPPING[task_type]

        # Priority 3: Content analysis
        return self._analyze_task_content(task)

    def orchestrate_task(self, task: str, task_type: str, role: str) -> Dict[str, Any]:
        """
        Orchestrate a task across multiple models using intelligent model selection.

        Args:
            task: The task to perform
            task_type: Type of task
            role: AI role

        Returns:
            Dictionary with task results from different models
        """
        results = {}

        # Get context for the role and task
        context = get_context_for_role(role, task)

        # Step 1: Planning (Intelligent model selection)
        planning_model = self.select_model_for_task(task, "planning", "planner")
        if self.switch_model(planning_model) and self.current_lm:
            plan_prompt = f"""You are a planner AI assistant with access to project context.

{context}

As a planner, create a detailed plan for this task: {task}

Please consider the project's architecture, standards, and best practices in your planning."""
            response = self.current_lm(plan_prompt)
            results["plan"] = response[0] if isinstance(response, list) else str(response)

        # Step 2: Execution (Intelligent model selection)
        execution_model = self.select_model_for_task(task, "rapid_prototyping", "implementer")
        if self.switch_model(execution_model) and self.current_lm:
            execute_prompt = f"""You are an implementer AI assistant with access to project context.

{context}

Based on this plan: {results.get('plan', '')}

Execute this task: {task}

Please follow the project's coding standards and best practices."""
            response = self.current_lm(execute_prompt)
            results["execution"] = response[0] if isinstance(response, list) else str(response)

        # Step 3: Review (Intelligent model selection)
        review_model = self.select_model_for_task(task, "documentation_analysis", "reviewer")
        if self.switch_model(review_model) and self.current_lm:
            review_prompt = f"""You are a reviewer AI assistant with access to project context.

{context}

Review this execution: {results.get('execution', '')}

Original task: {task}

Please provide a comprehensive review considering the project's quality standards and best practices."""
            response = self.current_lm(review_prompt)
            results["review"] = response[0] if isinstance(response, list) else str(response)

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get model switching statistics."""
        return {
            "current_model": self.current_model.value if self.current_model else None,
            "switch_count": self.switch_count,
            "model_load_times": {model.value: time for model, time in self.model_load_times.items()},
            "available_models": [model.value for model in LocalModel],
        }


# ---------- Enhanced DSPy Modules ----------


class IntelligentModelSelector(Module):
    """DSPy module for intelligent model selection with reasoning"""

    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(ModelSelectionSignature)

    def forward(
        self, task: str, task_type: str, complexity: str = "moderate", context_size: int = 1000
    ) -> Dict[str, Any]:
        """Select the best model for a task with reasoning"""
        result = self.predict(task=task, task_type=task_type, complexity=complexity, context_size=context_size)
        return {
            "selected_model": result.selected_model,
            "reasoning": result.reasoning,
            "confidence": result.confidence,
            "expected_performance": result.expected_performance,
        }


class LocalTaskExecutor(Module):
    """DSPy module for executing tasks with local models using structured I/O"""

    def __init__(self, model_switcher: ModelSwitcher):
        super().__init__()
        self.model_switcher = model_switcher
        self.predict = dspy.Predict(LocalTaskSignature)

    def forward(self, task: str, task_type: str, role: str, complexity: str = "moderate") -> Dict[str, Any]:
        """Execute a task with local model using structured DSPy signature"""

        # Get context for the role and task
        context = get_context_for_role(role, task)

        # Get model selection reasoning
        selector = IntelligentModelSelector()
        model_selection = selector.forward(task, task_type, complexity)

        # Get appropriate model for task
        model = self.model_switcher.get_model_for_task(task_type, complexity)

        # Switch to the model
        if self.model_switcher.switch_model(model) and self.model_switcher.current_lm:
            # Build enhanced prompt with context
            if context:
                enhanced_prompt = f"""You are a {role} AI assistant with access to project context.

{context}

TASK: {task}

Please provide a detailed response following the project's coding standards and best practices."""
            else:
                enhanced_prompt = task

            # Execute task with enhanced prompt
            response = self.model_switcher.current_lm(enhanced_prompt)
            result_text = response[0] if isinstance(response, list) else str(response)

            # Use DSPy signature for structured output
            signature_result = self.predict(task=task, task_type=task_type, role=role, complexity=complexity)

            return {
                "result": result_text,
                "confidence": signature_result.confidence,
                "model_used": model.value,
                "reasoning": signature_result.reasoning,
                "model_selection": model_selection,
            }
        else:
            raise RuntimeError("No model available for task")


class MultiModelOrchestrator(Module):
    """DSPy module for orchestrating tasks across multiple models"""

    def __init__(self, model_switcher: ModelSwitcher):
        super().__init__()
        self.model_switcher = model_switcher
        self.predict = dspy.Predict(MultiModelOrchestrationSignature)

    def forward(self, task: str, task_type: str, role: str) -> Dict[str, Any]:
        """Orchestrate a task across multiple models with structured output"""

        # Perform multi-model orchestration
        orchestration_results = self.model_switcher.orchestrate_task(task, task_type, role)

        # Use DSPy signature for structured output
        signature_result = self.predict(task=task, task_type=task_type, role=role)

        return {
            "plan": orchestration_results.get("plan", ""),
            "execution": orchestration_results.get("execution", ""),
            "review": orchestration_results.get("review", ""),
            "final_result": signature_result.final_result,
            "orchestration_notes": signature_result.orchestration_notes,
        }


class ModelSwitchingModule(Module):
    """DSPy module that automatically switches models based on task requirements"""

    def __init__(self, model_switcher: ModelSwitcher):
        super().__init__()
        self.model_switcher = model_switcher

    def forward(self, task: str, task_type: str = "moderate_coding", role: str = "coder") -> str:
        """
        Forward pass with automatic model switching.

        Args:
            task: Task to perform
            task_type: Type of task
            role: AI role

        Returns:
            Task result
        """
        # Get appropriate model for task
        model = self.model_switcher.get_model_for_task(task_type, role)

        # Get context for the role and task
        context = get_context_for_role(role, task)

        # Switch to the model
        if self.model_switcher.switch_model(model) and self.model_switcher.current_lm:
            # Build enhanced prompt with context
            if context:
                enhanced_prompt = f"""You are a {role} AI assistant with access to project context.

{context}

TASK: {task}

Please provide a detailed response following the project's coding standards and best practices."""
            else:
                enhanced_prompt = task

            # Perform the task with enhanced prompt
            response = self.model_switcher.current_lm(enhanced_prompt)
            return response[0] if isinstance(response, list) else str(response)
        else:
            # Fallback to current model or error
            if self.model_switcher.current_lm:
                response = self.model_switcher.current_lm(task)
                return response[0] if isinstance(response, list) else str(response)
            else:
                raise RuntimeError("No model available for task")


# ---------- Cursor AI Integration Functions ----------


def cursor_execute_task(task: str, task_type: str = "moderate_coding", role: str = "coder") -> Dict[str, Any]:
    """
    Cursor AI integration function - execute task with local models

    Args:
        task: Task to perform
        task_type: Type of task
        role: AI role

    Returns:
        Dictionary with task results and metadata
    """
    switcher = ModelSwitcher()
    executor = LocalTaskExecutor(switcher)

    try:
        result = executor.forward(task, task_type, role)
        return {
            "success": True,
            "result": result["result"],
            "model_used": result["model_used"],
            "confidence": result["confidence"],
            "reasoning": result["reasoning"],
        }
    except Exception as e:
        return {"success": False, "error": str(e), "fallback": "Using Cursor AI fallback"}


def cursor_orchestrate_task(task: str, task_type: str = "moderate_coding", role: str = "coder") -> Dict[str, Any]:
    """
    Cursor AI integration function - orchestrate task across multiple models

    Args:
        task: Task to orchestrate
        task_type: Type of task
        role: AI role

    Returns:
        Dictionary with orchestration results
    """
    switcher = ModelSwitcher()
    orchestrator = MultiModelOrchestrator(switcher)

    try:
        result = orchestrator.forward(task, task_type, role)
        return {
            "success": True,
            "plan": result["plan"],
            "execution": result["execution"],
            "review": result["review"],
            "final_result": result["final_result"],
            "orchestration_notes": result["orchestration_notes"],
        }
    except Exception as e:
        return {"success": False, "error": str(e), "fallback": "Using Cursor AI fallback"}


# ---------- Usage Example ----------


def create_model_switcher() -> ModelSwitcher:
    """Create and configure a model switcher instance."""
    switcher = ModelSwitcher()

    # Initialize with default model
    switcher.switch_model(LocalModel.LLAMA_3_1_8B)

    return switcher


def example_usage():
    """Example usage of the enhanced model switcher."""
    switcher = create_model_switcher()

    # Example: Multi-model task orchestration
    task = "Create a Python script to analyze a CSV file"
    results = switcher.orchestrate_task(task, "moderate_coding", "coder")

    print("Task Results:")
    for step, result in results.items():
        print(f"{step}: {result}")

    # Print statistics
    stats = switcher.get_stats()
    print(f"Model switches: {stats['switch_count']}")
    print(f"Load times: {stats['model_load_times']}")


if __name__ == "__main__":
    example_usage()
