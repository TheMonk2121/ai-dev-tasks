"""
Memory Rehydrator for LTST Memory System

This module provides automatic memory rehydration capabilities for the LTST Memory System,
including session continuity detection, intelligent context prioritization, and performance optimization.
"""

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from .context_merger import ContextMerger, MergedContext
from .conversation_storage import ConversationContext, ConversationMessage, ConversationStorage
from .session_manager import SessionManager

logger = logging.getLogger(__name__)

# Role instructions for different AI roles
ROLE_INSTRUCTIONS = {
    "coder": {
        "focus": "Code implementation, debugging, and technical problem-solving",
        "context": "Understand the codebase structure, existing patterns, and project requirements",
        "approach": "Write clean, efficient code following project standards",
        "priorities": ["Functionality", "Performance", "Maintainability"],
        "validation": "Ensure code passes all tests and meets quality standards",
        "required_standards": [
            "Follow existing code patterns and conventions",
            "Write comprehensive tests for new functionality",
            "Optimize for readability and performance",
            "Handle edge cases and error conditions",
        ],
        "safety_protocol": [
            "read_core_memory_context",
            "check_current_backlog",
            "understand_file_organization",
            "apply_tier_based_analysis",
            "run_conflict_detection",
            "validate_documentation",
        ],
        "quality_gates": [
            "Code review requirements",
            "Test coverage thresholds",
            "Performance benchmarks",
            "Security validations",
        ],
        "testing_guide": {
            "unit_tests": "Test individual functions and methods",
            "integration_tests": "Test component interactions",
            "performance_tests": "Validate performance requirements",
            "security_tests": "Check for security vulnerabilities",
            "system_tests": "End-to-end system validation",
        },
        "tool_usage": {
            "code_quality": "Use linting and formatting tools",
            "validation": "Run validation scripts and checks",
            "development": "Use development environment tools",
            "testing": "Execute test suites and coverage analysis",
            "monitoring": "Monitor system performance and logs",
            "pre_commit": "Run pre-commit hooks and checks",
            "memory_rehydration": "Use memory rehydration for context",
            "search_and_analysis": "Search codebase and analyze patterns",
        },
        "guidelines": [
            "Follow existing code patterns and conventions",
            "Write comprehensive tests for new functionality",
            "Optimize for readability and performance",
            "Handle edge cases and error conditions",
        ],
    },
    "planner": {
        "focus": "Strategic planning, task breakdown, and project organization",
        "approach": "Break down complex problems into manageable tasks",
        "priorities": ["Clarity", "Feasibility", "Dependencies"],
        "guidelines": [
            "Create clear, actionable task lists",
            "Identify dependencies and blockers",
            "Estimate effort and complexity",
            "Plan for testing and validation",
        ],
    },
    "implementer": {
        "focus": "Executing planned tasks and integrating components",
        "approach": "Implement solutions following established patterns",
        "priorities": ["Completeness", "Integration", "Quality"],
        "guidelines": [
            "Follow the established development workflow",
            "Ensure proper integration with existing systems",
            "Maintain code quality and documentation",
            "Test thoroughly before marking complete",
        ],
    },
    "researcher": {
        "focus": "Investigation, analysis, and knowledge discovery",
        "approach": "Gather information and provide insights",
        "priorities": ["Accuracy", "Completeness", "Relevance"],
        "guidelines": [
            "Research thoroughly before making recommendations",
            "Cite sources and provide evidence",
            "Consider multiple perspectives and approaches",
            "Document findings clearly and concisely",
        ],
    },
}

# Minimal role-to-file mapping for tests expecting ROLE_FILES
# Keys must include at least: coder, planner, implementer, researcher
# Values are project-relative markdown paths.
ROLE_FILES = {
    "coder": [
        "400_guides/400_04_development-workflow-and-standards.md",
        # Use existing docs focused on workflow, organization, and performance
        "400_guides/400_05_codebase-organization-patterns.md",
        "400_guides/400_11_performance-optimization.md",
        "100_memory/104_dspy-development-context.md",
        # Additional files for comprehensive coder support - pointing to existing core docs
        "000_core/003_process-task-list.md",  # Task processing guide
        "000_core/004_development-roadmap.md",  # Development roadmap
        "000_core/011_evaluation-profiles-guide.md",  # Evaluation guide
    ],
    # Other roles present for interface compatibility
    "planner": [],
    "implementer": [],
    "researcher": [],
}


@dataclass
class RehydrationRequest:
    """Request for memory rehydration."""

    session_id: str
    user_id: str
    current_message: str | None = None
    context_types: list[str] | None = None
    max_context_length: int = 10000
    include_conversation_history: bool = True
    history_limit: int = 20
    relevance_threshold: float = 0.7
    similarity_threshold: float = 0.8
    metadata: dict[str, Any] | None = None

    def __post_init__(self):
        """Initialize computed fields."""
        if self.context_types is None:
            self.context_types = ["conversation", "preference", "project", "user_info"]
        if self.metadata is None:
            self.metadata = {}


@dataclass
class RehydrationResult:
    """Result of memory rehydration operation."""

    session_id: str
    user_id: str
    rehydrated_context: str
    conversation_history: list[ConversationMessage]
    user_preferences: dict[str, Any]
    project_context: dict[str, Any]
    relevant_contexts: list[ConversationContext]
    merged_contexts: list[MergedContext]
    session_continuity_score: float
    context_relevance_scores: dict[str, float]
    rehydration_time_ms: float
    cache_hit: bool
    metadata: dict[str, Any]

    def __post_init__(self):
        """Initialize computed fields."""
        if self.metadata is None:
            self.metadata = {}


class MemoryRehydrator:
    """Handles automatic memory rehydration for the LTST Memory System."""

    def __init__(self, conversation_storage: ConversationStorage | None = None):
        """Initialize memory rehydrator."""
        if conversation_storage is None:
            self.conversation_storage = ConversationStorage()
        else:
            self.conversation_storage = conversation_storage

        self.context_merger = ContextMerger(self.conversation_storage)
        self.session_manager = SessionManager(self.conversation_storage)

        # Cache for performance optimization
        self.rehydration_cache = {}
        self.cache_ttl = timedelta(minutes=15)
        self.cache_timestamps = {}

        # Configuration
        self.default_relevance_threshold = 0.7
        self.default_similarity_threshold = 0.8
        self.max_conversation_history = 50
        self.max_context_length = 10000
        self.session_continuity_window = timedelta(hours=24)

    def _get_cached_rehydration(self, request: RehydrationRequest) -> RehydrationResult | None:
        """Get rehydration result from cache if available and fresh."""
        cache_key = self._generate_cache_key(request)

        if cache_key in self.rehydration_cache:
            timestamp = self.cache_timestamps.get(cache_key)
            if timestamp and datetime.now() - timestamp < self.cache_ttl:
                return self.rehydration_cache[cache_key]

        return None

    def _cache_rehydration(self, request: RehydrationRequest, result: RehydrationResult):
        """Cache rehydration result for future use."""
        cache_key = self._generate_cache_key(request)
        self.rehydration_cache[cache_key] = result
        self.cache_timestamps[cache_key] = datetime.now()

    def _generate_cache_key(self, request: RehydrationRequest) -> str:
        """Generate cache key for the rehydration request."""
        cache_data = {
            "session_id": request.session_id,
            "user_id": request.user_id,
            "current_message_hash": hashlib.sha256((request.current_message or "").encode()).hexdigest()[:16],
            "context_types": sorted(request.context_types or []),
            "max_context_length": request.max_context_length,
            "include_conversation_history": request.include_conversation_history,
            "history_limit": request.history_limit,
            "relevance_threshold": request.relevance_threshold,
            "similarity_threshold": request.similarity_threshold,
        }
        return hashlib.sha256(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()

    def _detect_session_continuity(self, session_id: str, user_id: str) -> float:
        """Detect session continuity based on recent activity."""
        try:
            # Get recent sessions for the user using SessionManager
            recent_sessions = self.session_manager.get_user_sessions(user_id, limit=5, active_only=False)

            if not recent_sessions:
                return 0.0

            # Check if current session is in recent sessions
            current_session_found = any(s.session_id == session_id for s in recent_sessions)

            if current_session_found:
                # High continuity for current session
                return 0.9

            # Check for similar session names or context
            current_session = self._get_session_info(session_id)
            if not current_session:
                return 0.0

            # Calculate similarity with recent sessions
            max_similarity = 0.0
            for recent_session in recent_sessions:
                similarity = self._calculate_session_similarity(
                    current_session,
                    {
                        "session_id": recent_session.session_id,
                        "session_name": recent_session.session_id,  # Using session_id as name for now
                        "context_summary": "",
                        "metadata": {},
                    },
                )
                max_similarity = max(max_similarity, similarity)

            return max_similarity

        except Exception as e:
            logger.error(f"Session continuity detection failed: {e}")
            return 0.0

    def _get_session_info(self, session_id: str) -> dict[str, Any] | None:
        """Get session information."""
        try:
            # Get session summary using ConversationStorage
            session_summary = self.conversation_storage.get_session_summary(session_id)
            if not session_summary:
                return None

            return {
                "session_id": session_id,
                "session_name": session_summary.get("session_name", session_id),
                "context_summary": session_summary.get("context_summary", ""),
                "metadata": session_summary.get("metadata", {}),
            }

        except Exception as e:
            logger.error(f"Failed to get session info: {e}")
            return None

    def _calculate_session_similarity(self, session1: dict[str, Any], session2: dict[str, Any]) -> float:
        """Calculate similarity between two sessions."""
        try:
            # Simple text-based similarity for session names and context
            name1 = (session1.get("session_name") or "").lower()
            name2 = (session2.get("session_name") or "").lower()

            context1 = (session1.get("context_summary") or "").lower()
            context2 = (session2.get("context_summary") or "").lower()

            # Calculate name similarity
            name_tokens1 = set(name1.split())
            name_tokens2 = set(name2.split())

            name_similarity = 0.0
            if name_tokens1 and name_tokens2:
                intersection = len(name_tokens1.intersection(name_tokens2))
                union = len(name_tokens1.union(name_tokens2))
                name_similarity = intersection / union if union > 0 else 0.0

            # Calculate context similarity
            context_tokens1 = set(context1.split())
            context_tokens2 = set(context2.split())

            context_similarity = 0.0
            if context_tokens1 and context_tokens2:
                intersection = len(context_tokens1.intersection(context_tokens2))
                union = len(context_tokens1.union(context_tokens2))
                context_similarity = intersection / union if union > 0 else 0.0

            # Weighted average
            return (name_similarity * 0.4) + (context_similarity * 0.6)

        except Exception as e:
            logger.error(f"Session similarity calculation failed: {e}")
            return 0.0

    def _get_conversation_history(self, session_id: str, limit: int) -> list[ConversationMessage]:
        """Get conversation history for a session."""
        try:
            # Get messages using ConversationStorage
            message_dicts = self.conversation_storage.retrieve_session_messages(session_id, limit=limit)

            messages = []
            for msg_dict in message_dicts:
                message = ConversationMessage(
                    session_id=msg_dict["session_id"],
                    role=msg_dict["role"],
                    content=msg_dict["content"],
                    message_type=msg_dict["message_type"],
                    metadata=msg_dict.get("metadata", {}),
                    parent_message_id=msg_dict.get("parent_message_id"),
                    is_context_message=msg_dict.get("is_context_message", False),
                    relevance_score=msg_dict.get("relevance_score", 0.5),
                )
                messages.append(message)

            return messages

        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []

    def _get_user_preferences(self, user_id: str) -> dict[str, Any]:
        """Get user preferences for context rehydration."""
        try:
            # Get user preferences using ConversationStorage
            preference_dicts = self.conversation_storage.retrieve_user_preferences(user_id, limit=50)

            preferences = {}
            for pref_dict in preference_dicts:
                preferences[pref_dict["preference_key"]] = {
                    "value": pref_dict["preference_value"],
                    "metadata": {
                        "confidence_score": pref_dict["confidence_score"],
                        "source": pref_dict["source"],
                        "usage_count": pref_dict.get("usage_count", 0),
                    },
                }

            return preferences

        except Exception as e:
            logger.error(f"Failed to get user preferences: {e}")
            return {}

    def _get_project_context(self, session_id: str) -> dict[str, Any]:
        """Get project context for the session."""
        try:
            contexts = self.context_merger.merge_contexts(
                session_id, context_type="project", relevance_threshold=self.default_relevance_threshold
            )

            project_context = {}
            for merged_context in contexts.merged_contexts:
                project_context[merged_context.context_type] = {
                    "content": merged_context.merged_content,
                    "relevance": merged_context.relevance_score,
                    "metadata": merged_context.metadata,
                }

            return project_context

        except Exception as e:
            logger.error(f"Failed to get project context: {e}")
            return {}

    def _get_relevant_contexts(self, request: RehydrationRequest) -> list[ConversationContext]:
        """Get relevant contexts based on the request."""
        try:
            relevant_contexts = []

            for context_type in request.context_types or []:
                contexts = self.context_merger.merge_contexts(
                    request.session_id,
                    context_type=context_type,
                    relevance_threshold=request.relevance_threshold,
                    similarity_threshold=request.similarity_threshold,
                )

                # Convert merged contexts back to conversation contexts
                for merged_context in contexts.merged_contexts:
                    for source_context in merged_context.source_contexts:
                        if source_context not in relevant_contexts:
                            relevant_contexts.append(source_context)

            # Add decision intelligence contexts
            decision_contexts = self._get_decision_contexts(request)
            relevant_contexts.extend(decision_contexts)

            return relevant_contexts

        except Exception as e:
            logger.error(f"Failed to get relevant contexts: {e}")
            return []

    def _get_decision_contexts(self, request: RehydrationRequest) -> list[ConversationContext]:
        """Get decision contexts with decision intelligence scoring."""
        try:
            # Extract entities from current message for entity overlap scoring
            query_entities = (
                self._extract_entities_from_message(request.current_message) if request.current_message else None
            )

            # Get decision contexts using the specialized merger
            merge_result = self.context_merger.merge_decision_contexts(
                request.session_id,
                query_entities=query_entities,
                relevance_threshold=request.relevance_threshold,
                similarity_threshold=request.similarity_threshold,
            )

            # Convert merged decision contexts back to conversation contexts
            decision_contexts = []
            for merged_context in merge_result.merged_contexts:
                for source_context in merged_context.source_contexts:
                    # Create enhanced context with decision intelligence
                    enhanced_context = ConversationContext(
                        session_id=source_context.session_id,
                        context_type=source_context.context_type,
                        context_key=source_context.context_key,
                        context_value=source_context.context_value,
                        relevance_score=merged_context.relevance_score,  # Use merged score
                        metadata={
                            **(source_context.metadata or {}),
                            "decision_head": getattr(source_context, "decision_head", None),
                            "decision_status": getattr(source_context, "decision_status", "open"),
                            "entities": getattr(source_context, "entities", []),
                            "files": getattr(source_context, "files", []),
                            "merged_score": merged_context.relevance_score,
                            "semantic_similarity": merged_context.semantic_similarity,
                        },
                    )
                    decision_contexts.append(enhanced_context)

            logger.info(f"Retrieved {len(decision_contexts)} decision contexts for session {request.session_id}")
            return decision_contexts

        except Exception as e:
            logger.error(f"Failed to get decision contexts: {e}")
            return []

    def _extract_entities_from_message(self, message: str) -> list[str]:
        """Extract potential entities from a message for decision context scoring."""
        try:
            if not message:
                return []

            # Simple entity extraction - look for common patterns
            entities = []

            # Extract project names (e.g., "project:alpha", "rag_system")
            import re

            project_patterns = [r"project:(\w+)", r"(\w+)_system", r"(\w+)_project", r"(\w+)_pipeline"]

            for pattern in project_patterns:
                matches = re.findall(pattern, message.lower())
                entities.extend(matches)

            # Extract technology names
            tech_keywords = [
                "python",
                "postgresql",
                "pgvector",
                "dspy",
                "rag",
                "ltst",
                "vector",
                "embedding",
                "memory",
                "context",
                "decision",
            ]

            for keyword in tech_keywords:
                if keyword.lower() in message.lower():
                    entities.append(keyword)

            # Remove duplicates and return
            return list(set(entities))

        except Exception as e:
            logger.warning(f"Failed to extract entities from message: {e}")
            return []

    def _get_decision_insights(self, session_id: str) -> dict[str, Any]:
        """Get insights about decisions for a session."""
        try:
            # Get decision contexts
            decision_contexts = self.conversation_storage.retrieve_context(session_id, "decision", limit=100)

            if not decision_contexts:
                return {
                    "total_decisions": 0,
                    "open_decisions": 0,
                    "closed_decisions": 0,
                    "superseded_decisions": 0,
                    "top_entities": [],
                    "recent_decisions": [],
                }

            # Analyze decision statuses
            status_counts = {"open": 0, "closed": 0, "superseded": 0}
            all_entities = []
            recent_decisions = []

            for ctx in decision_contexts:
                status = ctx.get("decision_status", "open")
                status_counts[status] = status_counts.get(status, 0) + 1

                # Collect entities
                entities = ctx.get("entities", [])
                if isinstance(entities, str):
                    try:
                        import json

                        entities = json.loads(entities)
                    except:
                        entities = []
                all_entities.extend(entities)

                # Collect recent decisions
                if len(recent_decisions) < 5:
                    recent_decisions.append(
                        {
                            "head": ctx.get("decision_head", "Unknown"),
                            "status": status,
                            "content": ctx.get("context_value", "")[:100] + "...",
                        }
                    )

            # Get top entities
            from collections import Counter

            entity_counts = Counter(all_entities)
            top_entities = [entity for entity, count in entity_counts.most_common(10)]

            return {
                "total_decisions": len(decision_contexts),
                "open_decisions": status_counts["open"],
                "closed_decisions": status_counts["closed"],
                "superseded_decisions": status_counts["superseded"],
                "top_entities": top_entities,
                "recent_decisions": recent_decisions,
            }

        except Exception as e:
            logger.error(f"Failed to get decision insights: {e}")
            return {"total_decisions": 0, "error": str(e)}

    def _calculate_context_relevance_scores(
        self,
        conversation_history: list[ConversationMessage],
        user_preferences: dict[str, Any],
        project_context: dict[str, Any],
        relevant_contexts: list[ConversationContext],
        current_message: str | None,
    ) -> dict[str, float]:
        """Calculate relevance scores for different context types."""
        try:
            scores = {}

            # Conversation history relevance
            if conversation_history:
                recent_messages = conversation_history[-5:]  # Last 5 messages
                avg_relevance = sum(msg.relevance_score for msg in recent_messages) / len(recent_messages)
                scores["conversation_history"] = min(avg_relevance, 1.0)
            else:
                scores["conversation_history"] = 0.0

            # User preferences relevance
            if user_preferences:
                scores["user_preferences"] = 0.8  # High relevance for user preferences
            else:
                scores["user_preferences"] = 0.0

            # Project context relevance
            if project_context:
                total_relevance = sum(data["relevance"] for data in project_context.values())
                scores["project_context"] = total_relevance / len(project_context) if project_context else 0.0
            else:
                scores["project_context"] = 0.0

            # Relevant contexts relevance
            if relevant_contexts:
                total_relevance = sum(ctx.relevance_score for ctx in relevant_contexts)
                scores["relevant_contexts"] = total_relevance / len(relevant_contexts)
            else:
                scores["relevant_contexts"] = 0.0

            # Overall relevance
            scores["overall"] = sum(scores.values()) / len(scores)

            return scores

        except Exception as e:
            logger.error(f"Failed to calculate relevance scores: {e}")
            return {"overall": 0.0}

    def _merge_rehydrated_context(
        self,
        conversation_history: list[ConversationMessage],
        user_preferences: dict[str, Any],
        project_context: dict[str, Any],
        relevant_contexts: list[ConversationContext],
        current_message: str | None,
        max_length: int,
    ) -> str:
        """Merge all rehydrated context into a single string."""
        try:
            merged_parts = []

            # Add conversation history
            if conversation_history:
                history_text = "Conversation History:\n"
                for msg in conversation_history[-10:]:  # Last 10 messages
                    role_label = "User" if msg.role == "human" else "Assistant"
                    history_text += f"{role_label}: {msg.content}\n"
                merged_parts.append(history_text)

            # Add decision contexts first (highest priority)
            decision_contexts = [ctx for ctx in relevant_contexts if ctx.context_type == "decision"]
            if decision_contexts:
                # Sort by relevance score (highest first)
                decision_contexts.sort(key=lambda x: x.relevance_score, reverse=True)

                decisions_text = "Key Decisions:\n"
                for ctx in decision_contexts[:5]:  # Top 5 decisions
                    status = ctx.metadata.get("decision_status", "open") if ctx.metadata else "open"
                    status_emoji = "🟢" if status == "open" else "🔴" if status == "superseded" else "🟡"
                    decisions_text += f"{status_emoji} {ctx.context_value}\n"

                    # Add decision metadata if available
                    if ctx.metadata:
                        if ctx.metadata.get("decision_head"):
                            decisions_text += f"   Summary: {ctx.metadata['decision_head']}\n"
                        if ctx.metadata.get("entities"):
                            decisions_text += f"   Entities: {', '.join(ctx.metadata['entities'])}\n"
                        if ctx.metadata.get("files"):
                            decisions_text += f"   Files: {', '.join(ctx.metadata['files'])}\n"

                    decisions_text += "\n"

                merged_parts.append(decisions_text)

            # Add user preferences
            if user_preferences:
                prefs_text = "User Preferences:\n"
                for key, data in user_preferences.items():
                    prefs_text += f"  {key}: {data['value']}\n"
                merged_parts.append(prefs_text)

            # Add project context
            if project_context:
                project_text = "Project Context:\n"
                for context_type, data in project_context.items():
                    project_text += f"  {context_type}: {data['content']}\n"
                merged_parts.append(project_text)

            # Add relevant contexts
            if relevant_contexts:
                context_text = "Relevant Context:\n"
                for ctx in relevant_contexts[:5]:  # Top 5 contexts
                    context_text += f"  {ctx.context_type}: {ctx.context_value}\n"
                merged_parts.append(context_text)

            # Add current message if provided
            if current_message:
                merged_parts.append(f"Current Message: {current_message}")

            # Join all parts
            merged_content = "\n\n".join(merged_parts)

            # Truncate if too long
            if len(merged_content) > max_length:
                merged_content = merged_content[:max_length] + "\n\n[Content truncated due to length]"

            return merged_content

        except Exception as e:
            logger.error(f"Failed to merge rehydrated context: {e}")
            return f"Current Message: {current_message}" if current_message else ""

    def rehydrate_memory(self, request: RehydrationRequest) -> RehydrationResult:
        """
        Rehydrate memory for a session.

        Args:
            request: Rehydration request with parameters

        Returns:
            RehydrationResult with all rehydrated context
        """
        start_time = time.time()

        try:
            # Check cache first
            cached_result = self._get_cached_rehydration(request)
            if cached_result:
                logger.info(f"Using cached rehydration for session {request.session_id}")
                return cached_result

            # Detect session continuity
            session_continuity_score = self._detect_session_continuity(request.session_id, request.user_id)

            # Get conversation history
            conversation_history = []
            if request.include_conversation_history:
                conversation_history = self._get_conversation_history(request.session_id, request.history_limit)

            # Get user preferences
            user_preferences = self._get_user_preferences(request.user_id)

            # Get project context
            project_context = self._get_project_context(request.session_id)

            # Get session insights for enhanced context
            session_insights = self.get_session_insights_for_rehydration(request.session_id, request.user_id)

            # Get decision insights for enhanced context
            decision_insights = self._get_decision_insights(request.session_id)

            # Get relevant contexts
            relevant_contexts = self._get_relevant_contexts(request)

            # Get merged contexts for detailed analysis
            merged_contexts = []
            for context_type in request.context_types or []:
                merge_result = self.context_merger.merge_contexts(
                    request.session_id,
                    context_type=context_type,
                    relevance_threshold=request.relevance_threshold,
                    similarity_threshold=request.similarity_threshold,
                )
                merged_contexts.extend(merge_result.merged_contexts)

            # Add decision contexts with decision intelligence
            decision_merge_result = self.context_merger.merge_decision_contexts(
                request.session_id,
                query_entities=(
                    self._extract_entities_from_message(request.current_message) if request.current_message else None
                ),
                relevance_threshold=request.relevance_threshold,
                similarity_threshold=request.similarity_threshold,
            )
            merged_contexts.extend(decision_merge_result.merged_contexts)

            # Calculate relevance scores
            context_relevance_scores = self._calculate_context_relevance_scores(
                conversation_history, user_preferences, project_context, relevant_contexts, request.current_message
            )

            # Merge all context
            rehydrated_context = self._merge_rehydrated_context(
                conversation_history,
                user_preferences,
                project_context,
                relevant_contexts,
                request.current_message,
                request.max_context_length,
            )

            rehydration_time_ms = (time.time() - start_time) * 1000

            # Create result
            result = RehydrationResult(
                session_id=request.session_id,
                user_id=request.user_id,
                rehydrated_context=rehydrated_context,
                conversation_history=conversation_history,
                user_preferences=user_preferences,
                project_context=project_context,
                relevant_contexts=relevant_contexts,
                merged_contexts=merged_contexts,
                session_continuity_score=session_continuity_score,
                context_relevance_scores=context_relevance_scores,
                rehydration_time_ms=rehydration_time_ms,
                cache_hit=False,
                metadata={
                    **(request.metadata or {}),
                    "session_insights": session_insights,
                    "decision_insights": decision_insights,
                },
            )

            # Cache the result
            self._cache_rehydration(request, result)

            logger.info(
                f"Memory rehydration completed for session {request.session_id}: "
                f"{rehydration_time_ms:.2f}ms, "
                f"{len(merged_contexts)} merged contexts, "
                f"{len(conversation_history)} conversation messages"
            )

            return result

        except Exception as e:
            logger.error(f"Memory rehydration failed for session {request.session_id}: {e}")
            raise

    def rehydrate_memory_simple(
        self,
        query: str,
        limit: int = 5,
        user_id: str | None = None,
        session_id: str | None = None,
        context_types: list[str] | None = None,
        include_history: bool = True,
        include_preferences: bool = True,
        include_project_context: bool = True,
        include_decision_insights: bool = True,
        min_relevance_score: float = 0.5,
    ) -> RehydrationResult:
        """
        Simplified rehydrate_memory method for backward compatibility.

        Args:
            query: Query string for context retrieval
            limit: Maximum number of contexts to retrieve
            user_id: User identifier
            session_id: Session identifier
            context_types: Types of context to include
            include_history: Whether to include conversation history
            include_preferences: Whether to include user preferences
            include_project_context: Whether to include project context
            include_decision_insights: Whether to include decision insights
            min_relevance_score: Minimum relevance score for contexts

        Returns:
            RehydrationResult with rehydrated context
        """
        if not session_id:
            raise ValueError("session_id is required")
        if not user_id:
            user_id = "default_user"

        # Create RehydrationRequest
        request = RehydrationRequest(
            session_id=session_id,
            user_id=user_id,
            current_message=query,
            context_types=context_types or ["conversation", "preference", "project", "decision"],
            max_context_length=10000,
            include_conversation_history=include_history,
            history_limit=limit,
            relevance_threshold=min_relevance_score,
            similarity_threshold=0.8,
        )

        return self.rehydrate_memory(request)

    def rehydrate_decision_memory(
        self,
        session_id: str,
        user_id: str,
        current_message: str | None = None,
        max_decisions: int = 10,
        include_metadata: bool = True,
    ) -> RehydrationResult:
        """
        Specialized rehydration focused on decision intelligence.

        Args:
            session_id: Session identifier
            user_id: User identifier
            current_message: Current message for entity extraction
            max_decisions: Maximum number of decisions to include
            include_metadata: Whether to include decision metadata

        Returns:
            RehydrationResult with decision-focused context
        """
        start_time = time.time()

        try:
            # Create specialized request
            request = RehydrationRequest(
                session_id=session_id,
                user_id=user_id,
                current_message=current_message,
                context_types=["decision"],  # Focus only on decisions
                max_context_length=8000,  # Smaller context for decisions
                include_conversation_history=False,  # Focus on decisions, not chat history
                relevance_threshold=0.6,  # Lower threshold to get more decisions
                similarity_threshold=0.7,
            )

            # Get decision contexts with entity overlap scoring
            query_entities = self._extract_entities_from_message(current_message) if current_message else None
            decision_merge_result = self.context_merger.merge_decision_contexts(
                session_id,
                query_entities=query_entities,
                relevance_threshold=request.relevance_threshold,
                similarity_threshold=request.similarity_threshold,
            )

            # Get decision insights
            decision_insights = self._get_decision_insights(session_id)

            # Build decision-focused context
            decision_context = self._build_decision_context(
                decision_merge_result.merged_contexts, decision_insights, max_decisions, include_metadata
            )

            rehydration_time_ms = (time.time() - start_time) * 1000

            # Create specialized result
            result = RehydrationResult(
                session_id=session_id,
                user_id=user_id,
                rehydrated_context=decision_context,
                conversation_history=[],  # No conversation history for decision focus
                user_preferences={},  # No user preferences for decision focus
                project_context={},  # No project context for decision focus
                relevant_contexts=[],  # Will be populated from merged contexts
                merged_contexts=decision_merge_result.merged_contexts,
                session_continuity_score=1.0,  # High continuity for decisions
                context_relevance_scores={"decisions": 0.9},  # High relevance for decisions
                rehydration_time_ms=rehydration_time_ms,
                cache_hit=False,
                metadata={
                    "decision_focus": True,
                    "decision_insights": decision_insights,
                    "total_decisions": decision_insights.get("total_decisions", 0),
                    "query_entities": query_entities or [],
                },
            )

            logger.info(
                f"Decision memory rehydration completed for session {session_id}: "
                f"{rehydration_time_ms:.2f}ms, "
                f"{len(decision_merge_result.merged_contexts)} decision contexts, "
                f"{decision_insights.get('total_decisions', 0)} total decisions"
            )

            return result

        except Exception as e:
            logger.error(f"Decision memory rehydration failed for session {session_id}: {e}")
            raise

    def _build_decision_context(
        self,
        merged_decisions: list[MergedContext],
        decision_insights: dict[str, Any],
        max_decisions: int,
        include_metadata: bool,
    ) -> str:
        """Build a focused decision context string."""
        try:
            if not merged_decisions:
                return "No decision contexts available for this session."

            # Sort by relevance score
            sorted_decisions = sorted(merged_decisions, key=lambda x: x.relevance_score, reverse=True)

            # Build context
            context_parts = []

            # Add summary
            total_decisions = decision_insights.get("total_decisions", 0)
            open_decisions = decision_insights.get("open_decisions", 0)
            context_parts.append(f"Decision Summary: {total_decisions} total decisions, {open_decisions} open")

            # Add top decisions
            context_parts.append("\nKey Decisions:")
            for i, decision in enumerate(sorted_decisions[:max_decisions]):
                status = "open"
                if decision.metadata:
                    status = (
                        decision.metadata.get("decision_statuses", ["open"])[0]
                        if isinstance(decision.metadata.get("decision_statuses"), list)
                        else "open"
                    )

                status_emoji = "🟢" if status == "open" else "🔴" if status == "superseded" else "🟡"
                context_parts.append(f"{i + 1}. {status_emoji} {decision.merged_content}")

                if include_metadata and decision.metadata:
                    if decision.metadata.get("decision_heads"):
                        heads = decision.metadata["decision_heads"]
                        if heads and heads[0]:
                            context_parts.append(f"   Summary: {heads[0]}")

                    if decision.metadata.get("source_contexts"):
                        context_parts.append(f"   Sources: {', '.join(decision.metadata['source_contexts'][:3])}")

            # Add entity insights
            top_entities = decision_insights.get("top_entities", [])
            if top_entities:
                context_parts.append(f"\nTop Entities: {', '.join(top_entities[:5])}")

            return "\n".join(context_parts)

        except Exception as e:
            logger.error(f"Failed to build decision context: {e}")
            return "Error building decision context"

    def get_rehydration_statistics(self) -> dict[str, Any]:
        """Get statistics about rehydration operations."""
        try:
            return {
                "cache_size": len(self.rehydration_cache),
                "cache_entries": list(self.rehydration_cache.keys()),
                "cache_ttl_seconds": self.cache_ttl.total_seconds(),
                "default_relevance_threshold": self.default_relevance_threshold,
                "default_similarity_threshold": self.default_similarity_threshold,
                "max_conversation_history": self.max_conversation_history,
                "max_context_length": self.max_context_length,
                "session_continuity_window_hours": self.session_continuity_window.total_seconds() / 3600,
            }
        except Exception as e:
            logger.error(f"Failed to get rehydration statistics: {e}")
            return {"error": str(e)}

    def get_session_insights_for_rehydration(self, session_id: str, user_id: str) -> dict[str, Any]:
        """Get session insights to enhance rehydration context."""
        try:
            # Get session insights using SessionManager
            insights = self.session_manager.get_session_insights(session_id)

            if "error" in insights:
                return {}

            # Enhance insights with additional context
            enhanced_insights = {
                "session_metrics": {
                    "message_count": insights.get("message_count", 0),
                    "context_count": insights.get("context_count", 0),
                    "preference_count": insights.get("preference_count", 0),
                    "user_engagement": insights.get("user_engagement", 0.0),
                    "session_duration": insights.get("session_duration", "0:00:00"),
                },
                "conversation_analysis": {
                    "topics": insights.get("conversation_topics", []),
                    "learning_opportunities": insights.get("learning_opportunities", []),
                    "learned_preferences": insights.get("learned_preferences", 0),
                },
                "user_patterns": {
                    "engagement_level": (
                        "high"
                        if insights.get("user_engagement", 0.0) > 0.7
                        else "medium" if insights.get("user_engagement", 0.0) > 0.4 else "low"
                    ),
                    "preferred_topics": insights.get("conversation_topics", [])[:3],
                    "communication_style": self._infer_communication_style(insights),
                },
            }

            return enhanced_insights

        except Exception as e:
            logger.error(f"Failed to get session insights for rehydration: {e}")
            return {}

    def _infer_communication_style(self, insights: dict[str, Any]) -> str:
        """Infer user communication style from session insights."""
        try:
            engagement = insights.get("user_engagement", 0.0)
            topics = insights.get("conversation_topics", [])
            opportunities = insights.get("learning_opportunities", [])

            if engagement > 0.8 and "technical" in topics:
                return "technical_detailed"
            elif engagement > 0.6 and len(topics) > 2:
                return "exploratory"
            elif "tutorial_requested" in opportunities:
                return "learning_focused"
            elif engagement < 0.4:
                return "concise"
            else:
                return "balanced"

        except Exception as e:
            logger.error(f"Failed to infer communication style: {e}")
            return "balanced"

    def cleanup_expired_cache(self) -> int:
        """Clean up expired cache entries."""
        try:
            current_time = datetime.now()
            expired_keys = []

            for cache_key, timestamp in self.cache_timestamps.items():
                if current_time - timestamp > self.cache_ttl:
                    expired_keys.append(cache_key)

            for key in expired_keys:
                del self.rehydration_cache[key]
                del self.cache_timestamps[key]

            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired rehydration cache entries")

            return len(expired_keys)

        except Exception as e:
            logger.error(f"Rehydration cache cleanup failed: {e}")
            return 0


@dataclass
class HydrationBundle:
    """Bundle containing rehydrated memory content and metadata."""

    text: str
    meta: dict[str, Any]


def build_hydration_bundle(
    role: str = "general", task: str = "general context", limit: int = 8, token_budget: int = 1200
) -> HydrationBundle:
    """
    Build a hydration bundle for the MCP server.

    Args:
        role: The AI role requesting the bundle
        task: The specific task or context needed
        limit: Maximum number of context items to include
        token_budget: Approximate token budget for the bundle

    Returns:
        HydrationBundle: Contains text content and metadata
    """
    try:
        # Create a rehydrator instance
        rehydrator = MemoryRehydrator()

        # Create a rehydration request with correct parameters
        request = RehydrationRequest(
            session_id=f"mcp_{int(time.time())}",
            user_id=f"mcp_{role}",
            current_message=task,
            max_context_length=token_budget,
            history_limit=limit,
            metadata={"role": role, "task": task, "token_budget": token_budget, "source": "mcp_server"},
        )

        # Get rehydrated memory
        result = rehydrator.rehydrate_memory(request)

        # Build the bundle text from rehydrated context
        bundle_text = result.rehydrated_context if result.rehydrated_context else ""

        # If no context found, provide a default message
        if not bundle_text.strip():
            bundle_text = f"# Memory Rehydration for {role}\n\nNo specific context found for task: {task}\n\nThis is a general memory bundle for the {role} role."

        # Build metadata
        metadata = {
            "role": role,
            "task": task,
            "session_id": request.session_id,
            "user_id": request.user_id,
            "total_tokens": len(bundle_text.split()),  # Rough token count
            "cache_hit": getattr(result, "cache_hit", False),
            "generated_at": datetime.now().isoformat(),
            "context_length": len(bundle_text),
        }

        return HydrationBundle(text=bundle_text, meta=metadata)

    except Exception as e:
        logger.error(f"Failed to build hydration bundle: {e}")
        # Return a fallback bundle
        fallback_text = f"# Memory Rehydration for {role}\n\nNo specific context found for task: {task}\n\nThis is a general memory bundle for the {role} role."
        fallback_meta = {
            "role": role,
            "task": task,
            "error": str(e),
            "generated_at": datetime.now().isoformat(),
            "fallback": True,
        }
        return HydrationBundle(text=fallback_text, meta=fallback_meta)


def rehydrate(query: str, role: str = "planner", **config: Any) -> HydrationBundle:
    """
    Compatibility wrapper that builds a hydration bundle.

    Args:
        query: Task/query description
        role: Role requesting context (planner/implementer/researcher/coder/reviewer)
        **config: Optional knobs; recognized keys are mapped into metadata
                 - limit: int (maps to build_hydration_bundle limit)
                 - token_budget or max_context_length: int (maps to token_budget)
                 - stability, use_rrf, dedupe, expand_query, use_entity_expansion: recorded in meta only

    Returns:
        HydrationBundle with text and metadata.
    """
    try:
        limit = int(config.get("limit", 8))
        token_budget = int(config.get("token_budget", config.get("max_context_length", 1200)))

        bundle = build_hydration_bundle(role=role, task=query, limit=limit, token_budget=token_budget)

        # Attach passthrough config to metadata for transparency
        passthrough_keys = [
            "stability",
            "use_rrf",
            "dedupe",
            "expand_query",
            "use_entity_expansion",
        ]
        extra_meta = {k: config[k] for k in passthrough_keys if k in config}
        bundle.meta.update(
            {
                "query": query,
                "requested_role": role,
                "limit": limit,
                "token_budget": token_budget,
                **extra_meta,
            }
        )
        return bundle
    except Exception as e:
        # Fall back to a minimal bundle
        logger.error(f"rehydrate wrapper failed: {e}")
        return HydrationBundle(
            text=f"# Memory Rehydration for {role}\n\nNo specific context found for task: {query}",
            meta={
                "role": role,
                "task": query,
                "error": str(e),
                "fallback": True,
                "generated_at": datetime.now().isoformat(),
            },
        )
