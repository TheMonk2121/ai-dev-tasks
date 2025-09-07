#!/usr/bin/env python3
"""
Agent Memory Blueprint
- Operational memory (tools & evals)
- Task/episodic memory (conversation & working set)
- Retrieval memory (contextual augmentation)
- Memory management and lifecycle
"""

import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timedelta


@dataclass
class ToolDefinition:
    """Tool definition for registry"""
    
    name: str
    json_schema: Dict[str, Any]
    idempotency: bool
    dry_run: bool
    deadlines: int  # seconds
    allowed_errors: List[str]
    when_to_use: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "json_schema": self.json_schema,
            "idempotency": self.idempotency,
            "dry_run": self.dry_run,
            "deadlines": self.deadlines,
            "allowed_errors": self.allowed_errors,
            "when_to_use": self.when_to_use,
        }


@dataclass
class EvalMemory:
    """Evaluation memory"""
    
    run_id: str
    dataset_version: str
    metrics: Dict[str, Any]
    prompt_audit: Dict[str, Any]
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "run_id": self.run_id,
            "dataset_version": self.dataset_version,
            "metrics": self.metrics,
            "prompt_audit": self.prompt_audit,
            "timestamp": self.timestamp,
        }


@dataclass
class ConversationTurn:
    """Single conversation turn"""
    
    turn_id: str
    user_input: str
    agent_response: str
    tools_used: List[str]
    timestamp: str
    expires_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "turn_id": self.turn_id,
            "user_input": self.user_input,
            "agent_response": self.agent_response,
            "tools_used": tools_used,
            "timestamp": self.timestamp,
            "expires_at": self.expires_at,
        }


@dataclass
class WorkingSet:
    """Working set for current episode"""
    
    model_name: str
    chunk_size: int
    overlap_ratio: float
    jaccard_threshold: float
    prefix_policy: str
    reranker_name: str
    prompt_hash: str
    few_shot_ids: List[str]
    cot_enabled: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "model_name": self.model_name,
            "chunk_size": self.chunk_size,
            "overlap_ratio": self.overlap_ratio,
            "jaccard_threshold": self.jaccard_threshold,
            "prefix_policy": self.prefix_policy,
            "reranker_name": self.reranker_name,
            "prompt_hash": self.prompt_hash,
            "few_shot_ids": self.few_shot_ids,
            "cot_enabled": self.cot_enabled,
        }


@dataclass
class LongTermFact:
    """Long-term fact"""
    
    fact_id: str
    category: str
    content: str
    confidence: float
    last_updated: str
    access_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "fact_id": self.fact_id,
            "category": self.category,
            "content": self.content,
            "confidence": self.confidence,
            "last_updated": self.last_updated,
            "access_count": self.access_count,
        }


@dataclass
class RetrievalMemory:
    """Retrieval memory for contextual augmentation"""
    
    doc_id: str
    embedding_text: str  # With context prefix
    bm25_text: str       # Clean text
    metadata: Dict[str, Any]
    last_accessed: str
    access_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "doc_id": self.doc_id,
            "embedding_text": self.embedding_text,
            "bm25_text": self.bm25_text,
            "metadata": self.metadata,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count,
        }


class AgentMemoryManager:
    """Manages agent memory across all types"""
    
    def __init__(self):
        # Operational memory
        self.tool_registry: Dict[str, ToolDefinition] = {}
        self.eval_memory: List[EvalMemory] = []
        
        # Task/episodic memory
        self.conversation_buffer: List[ConversationTurn] = []
        self.working_set: Optional[WorkingSet] = None
        self.long_term_facts: Dict[str, LongTermFact] = {}
        
        # Retrieval memory
        self.retrieval_memory: Dict[str, RetrievalMemory] = {}
        
        # Memory lifecycle settings
        self.conversation_ttl_hours = 24
        self.retrieval_ttl_days = 7
        self.max_conversation_turns = 100
        self.max_retrieval_items = 10000
    
    def register_tool(self, tool_def: ToolDefinition) -> None:
        """Register a tool in the registry"""
        self.tool_registry[tool_def.name] = tool_def
        print(f"🔧 Registered tool: {tool_def.name}")
        print(f"   When to use: {tool_def.when_to_use}")
        print(f"   Idempotency: {tool_def.idempotency}")
        print(f"   Dry run: {tool_def.dry_run}")
    
    def get_tool_definition(self, tool_name: str) -> Optional[ToolDefinition]:
        """Get tool definition by name"""
        return self.tool_registry.get(tool_name)
    
    def get_tool_registry(self) -> Dict[str, ToolDefinition]:
        """Get complete tool registry"""
        return self.tool_registry
    
    def store_eval_memory(self, eval_memory: EvalMemory) -> None:
        """Store evaluation memory"""
        self.eval_memory.append(eval_memory)
        
        # Keep only last 100 evaluations
        if len(self.eval_memory) > 100:
            self.eval_memory = self.eval_memory[-100:]
        
        print(f"📊 Stored eval memory: {eval_memory.run_id}")
    
    def get_latest_eval_memory(self) -> Optional[EvalMemory]:
        """Get latest evaluation memory"""
        return self.eval_memory[-1] if self.eval_memory else None
    
    def add_conversation_turn(self, turn: ConversationTurn) -> None:
        """Add conversation turn to buffer"""
        # Set expiration
        expires_at = datetime.now() + timedelta(hours=self.conversation_ttl_hours)
        turn.expires_at = expires_at.isoformat()
        
        self.conversation_buffer.append(turn)
        
        # Clean up expired turns
        self._cleanup_expired_turns()
        
        # Limit buffer size
        if len(self.conversation_buffer) > self.max_conversation_turns:
            self.conversation_buffer = self.conversation_buffer[-self.max_conversation_turns:]
    
    def _cleanup_expired_turns(self) -> None:
        """Remove expired conversation turns"""
        now = datetime.now()
        self.conversation_buffer = [
            turn for turn in self.conversation_buffer
            if not turn.expires_at or datetime.fromisoformat(turn.expires_at) > now
        ]
    
    def get_recent_conversation(self, limit: int = 10) -> List[ConversationTurn]:
        """Get recent conversation turns"""
        return self.conversation_buffer[-limit:] if self.conversation_buffer else []
    
    def set_working_set(self, working_set: WorkingSet) -> None:
        """Set working set for current episode"""
        self.working_set = working_set
        print(f"🎯 Working set updated:")
        print(f"   Model: {working_set.model_name}")
        print(f"   Chunk size: {working_set.chunk_size}")
        print(f"   Prompt hash: {working_set.prompt_hash}")
    
    def get_working_set(self) -> Optional[WorkingSet]:
        """Get current working set"""
        return self.working_set
    
    def store_long_term_fact(self, fact: LongTermFact) -> None:
        """Store long-term fact"""
        self.long_term_facts[fact.fact_id] = fact
        print(f"🧠 Stored long-term fact: {fact.fact_id}")
        print(f"   Category: {fact.category}")
        print(f"   Confidence: {fact.confidence}")
    
    def get_long_term_fact(self, fact_id: str) -> Optional[LongTermFact]:
        """Get long-term fact by ID"""
        if fact_id in self.long_term_facts:
            fact = self.long_term_facts[fact_id]
            fact.access_count += 1
            return fact
        return None
    
    def search_long_term_facts(self, category: str = None, min_confidence: float = 0.0) -> List[LongTermFact]:
        """Search long-term facts"""
        facts = list(self.long_term_facts.values())
        
        if category:
            facts = [f for f in facts if f.category == category]
        
        if min_confidence > 0:
            facts = [f for f in facts if f.confidence >= min_confidence]
        
        # Sort by access count (most accessed first)
        facts.sort(key=lambda f: f.access_count, reverse=True)
        
        return facts
    
    def store_retrieval_memory(self, retrieval: RetrievalMemory) -> None:
        """Store retrieval memory"""
        self.retrieval_memory[retrieval.doc_id] = retrieval
        
        # Clean up old retrieval items
        self._cleanup_old_retrieval()
        
        # Limit retrieval memory size
        if len(self.retrieval_memory) > self.max_retrieval_items:
            # Remove least accessed items
            sorted_items = sorted(
                self.retrieval_memory.items(),
                key=lambda x: x[1].access_count
            )
            items_to_remove = sorted_items[:len(sorted_items) - self.max_retrieval_items]
            for doc_id, _ in items_to_remove:
                del self.retrieval_memory[doc_id]
    
    def _cleanup_old_retrieval(self) -> None:
        """Remove old retrieval items"""
        cutoff_date = datetime.now() - timedelta(days=self.retrieval_ttl_days)
        
        to_remove = []
        for doc_id, retrieval in self.retrieval_memory.items():
            last_accessed = datetime.fromisoformat(retrieval.last_accessed)
            if last_accessed < cutoff_date:
                to_remove.append(doc_id)
        
        for doc_id in to_remove:
            del self.retrieval_memory[doc_id]
    
    def get_retrieval_memory(self, doc_id: str) -> Optional[RetrievalMemory]:
        """Get retrieval memory by doc ID"""
        if doc_id in self.retrieval_memory:
            retrieval = self.retrieval_memory[doc_id]
            retrieval.access_count += 1
            retrieval.last_accessed = datetime.now().isoformat()
            return retrieval
        return None
    
    def search_retrieval_memory(self, query: str, limit: int = 10) -> List[RetrievalMemory]:
        """Search retrieval memory (simple text matching)"""
        # Simple text matching - in production, you'd use proper search
        results = []
        query_lower = query.lower()
        
        for retrieval in self.retrieval_memory.values():
            if (query_lower in retrieval.embedding_text.lower() or 
                query_lower in retrieval.bm25_text.lower()):
                results.append(retrieval)
        
        # Sort by access count
        results.sort(key=lambda r: r.access_count, reverse=True)
        
        return results[:limit]
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get memory usage summary"""
        return {
            "tool_registry": {
                "total_tools": len(self.tool_registry),
                "tools": list(self.tool_registry.keys()),
            },
            "eval_memory": {
                "total_evaluations": len(self.eval_memory),
                "latest_run_id": self.eval_memory[-1].run_id if self.eval_memory else None,
            },
            "conversation_buffer": {
                "total_turns": len(self.conversation_buffer),
                "recent_turns": len(self.get_recent_conversation()),
            },
            "working_set": {
                "set": self.working_set.to_dict() if self.working_set else None,
            },
            "long_term_facts": {
                "total_facts": len(self.long_term_facts),
                "categories": list(set(f.category for f in self.long_term_facts.values())),
            },
            "retrieval_memory": {
                "total_items": len(self.retrieval_memory),
                "most_accessed": sorted(
                    self.retrieval_memory.values(),
                    key=lambda r: r.access_count,
                    reverse=True
                )[:5],
            },
        }
    
    def save_memory_state(self, filepath: str) -> None:
        """Save complete memory state"""
        memory_state = {
            "tool_registry": {name: tool.to_dict() for name, tool in self.tool_registry.items()},
            "eval_memory": [eval_mem.to_dict() for eval_mem in self.eval_memory],
            "conversation_buffer": [turn.to_dict() for turn in self.conversation_buffer],
            "working_set": self.working_set.to_dict() if self.working_set else None,
            "long_term_facts": {fact_id: fact.to_dict() for fact_id, fact in self.long_term_facts.items()},
            "retrieval_memory": {doc_id: retrieval.to_dict() for doc_id, retrieval in self.retrieval_memory.items()},
            "summary": self.get_memory_summary(),
        }
        
        with open(filepath, "w") as f:
            json.dump(memory_state, f, indent=2)
        
        print(f"💾 Memory state saved to: {filepath}")
    
    def load_memory_state(self, filepath: str) -> None:
        """Load memory state from file"""
        with open(filepath, "r") as f:
            memory_state = json.load(f)
        
        # Load tool registry
        self.tool_registry = {}
        for name, tool_data in memory_state.get("tool_registry", {}).items():
            self.tool_registry[name] = ToolDefinition(**tool_data)
        
        # Load eval memory
        self.eval_memory = []
        for eval_data in memory_state.get("eval_memory", []):
            self.eval_memory.append(EvalMemory(**eval_data))
        
        # Load conversation buffer
        self.conversation_buffer = []
        for turn_data in memory_state.get("conversation_buffer", []):
            self.conversation_buffer.append(ConversationTurn(**turn_data))
        
        # Load working set
        working_set_data = memory_state.get("working_set")
        if working_set_data:
            self.working_set = WorkingSet(**working_set_data)
        
        # Load long-term facts
        self.long_term_facts = {}
        for fact_id, fact_data in memory_state.get("long_term_facts", {}).items():
            self.long_term_facts[fact_id] = LongTermFact(**fact_data)
        
        # Load retrieval memory
        self.retrieval_memory = {}
        for doc_id, retrieval_data in memory_state.get("retrieval_memory", {}).items():
            self.retrieval_memory[doc_id] = RetrievalMemory(**retrieval_data)
        
        print(f"💾 Memory state loaded from: {filepath}")


def create_agent_memory_manager() -> AgentMemoryManager:
    """Create an agent memory manager"""
    return AgentMemoryManager()

