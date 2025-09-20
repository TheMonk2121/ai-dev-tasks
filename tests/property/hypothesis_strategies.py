"""
Advanced Hypothesis strategies for AI Dev Tasks project.

This module provides reusable, composable strategies that leverage
Hypothesis's full capabilities including @composite, stateful testing,
and domain-specific data generation.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta
from typing import Any

import numpy as np
from hypothesis import assume, example, given, settings
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays as hnp_arrays
from hypothesis.stateful import Bundle, RuleBasedStateMachine, rule, run_state_machine_as_test

# ============================================================================
# Domain-Specific Strategies
# ============================================================================


@st.composite
def eval_profile_strategy(draw: st.DrawFn) -> str:
    """Generate evaluation profile names."""
    return draw(st.sampled_from(["gold", "real", "mock"]))


@st.composite
def memory_system_strategy(draw: st.DrawFn) -> str:
    """Generate memory system names."""
    return draw(st.sampled_from(["ltst", "cursor", "go_cli", "prime"]))


@st.composite
def dspy_model_strategy(draw: st.DrawFn) -> str:
    """Generate DSPy model names."""
    return draw(
        st.sampled_from(
            [
                "anthropic.claude-3-haiku-20240307-v1:0",
                "anthropic.claude-3-sonnet-20240229-v1:0",
                "ollama/llama3.1:8b",
                "ollama/mistral:7b",
            ]
        )
    )


@st.composite
def database_dsn_strategy(draw: st.DrawFn) -> str:
    """Generate valid database DSN strings."""
    scheme = draw(st.sampled_from(["postgresql", "postgres", "mysql", "sqlite"]))

    if scheme == "sqlite":
        return f"sqlite:///{draw(st.text(min_size=1, max_size=50))}.db"

    host = draw(
        st.text(min_size=1, max_size=50, alphabet=st.characters(min_codepoint=ord("a"), max_codepoint=ord("z")))
    )
    port = draw(st.integers(min_value=1, max_value=65535))
    database = draw(
        st.text(min_size=1, max_size=50, alphabet=st.characters(min_codepoint=ord("a"), max_codepoint=ord("z")))
    )

    # Optional username and password
    username = draw(st.one_of(st.none(), st.text(min_size=1, max_size=50)))
    password = draw(st.one_of(st.none(), st.text(min_size=1, max_size=50)))

    if username and password:
        return f"{scheme}://{username}:{password}@{host}:{port}/{database}"
    elif username:
        return f"{scheme}://{username}@{host}:{port}/{database}"
    else:
        return f"{scheme}://{host}:{port}/{database}"


@st.composite
def conversation_message_strategy(draw: st.DrawFn) -> dict[str, Any]:
    """Generate conversation message data."""
    message_id = draw(st.text(min_size=1, max_size=50))
    thread_id = draw(st.text(min_size=1, max_size=50))
    content = draw(st.text(min_size=1, max_size=1000))
    role = draw(st.sampled_from(["user", "assistant", "system"]))
    timestamp = draw(st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime.now()))

    metadata = draw(
        st.dictionaries(
            st.text(min_size=1, max_size=50),
            st.one_of(
                st.text(min_size=1, max_size=100),
                st.integers(),
                st.booleans(),
                st.floats(allow_infinity=False, allow_nan=False),
            ),
            min_size=0,
            max_size=10,
        )
    )

    return {
        "message_id": message_id,
        "thread_id": thread_id,
        "content": content,
        "role": role,
        "timestamp": timestamp.isoformat(),
        "metadata": metadata,
    }


@st.composite
def retrieval_result_strategy(draw: st.DrawFn) -> dict[str, Any]:
    """Generate retrieval result data."""
    chunk_id = draw(st.text(min_size=1, max_size=50))
    content = draw(st.text(min_size=1, max_size=2000))
    score = draw(st.floats(min_value=0.0, max_value=1.0))
    source_path = draw(st.text(min_size=1, max_size=200))

    metadata = draw(
        st.dictionaries(
            st.text(min_size=1, max_size=50),
            st.one_of(
                st.text(min_size=1, max_size=100),
                st.integers(),
                st.booleans(),
                st.floats(allow_infinity=False, allow_nan=False),
            ),
            min_size=0,
            max_size=15,
        )
    )

    return {"chunk_id": chunk_id, "content": content, "score": score, "source_path": source_path, "metadata": metadata}


@st.composite
def embedding_vector_strategy(draw: st.DrawFn, dimension: int = 384) -> np.ndarray:
    """Generate embedding vectors."""
    return draw(
        hnp_arrays(
            dtype=np.float32,
            shape=(dimension,),
            elements=st.floats(min_value=-1.0, max_value=1.0, allow_infinity=False, allow_nan=False),
        )
    )


@st.composite
def evaluation_metrics_strategy(draw: st.DrawFn) -> dict[str, float]:
    """Generate evaluation metrics data."""
    return {
        "precision": draw(st.floats(min_value=0.0, max_value=1.0)),
        "recall": draw(st.floats(min_value=0.0, max_value=1.0)),
        "f1_score": draw(st.floats(min_value=0.0, max_value=1.0)),
        "faithfulness": draw(st.floats(min_value=0.0, max_value=1.0)),
        "latency_ms": draw(st.floats(min_value=0.0, max_value=5000.0)),
    }


# ============================================================================
# Stateful Testing
# ============================================================================


class MemorySystemStateMachine(RuleBasedStateMachine):
    """Stateful testing for memory system operations."""

    def __init__(self):
        super().__init__()
        self.memory_systems = {}
        self.conversations = {}
        self.current_thread_id = None

    @rule()
    def initialize_memory_system(self, system_name=memory_system_strategy()):
        """Initialize a memory system."""
        self.memory_systems[system_name] = {"initialized": True, "last_accessed": datetime.now(), "message_count": 0}
        return f"Initialized {system_name}"

    @rule()
    def create_conversation_thread(self, thread_id=st.text(min_size=1, max_size=50)):
        """Create a new conversation thread."""
        assume(thread_id not in self.conversations)
        self.conversations[thread_id] = {"messages": [], "created_at": datetime.now(), "last_updated": datetime.now()}
        self.current_thread_id = thread_id
        return f"Created thread {thread_id}"

    @rule()
    def add_message(self, message=conversation_message_strategy()):
        """Add a message to the current thread."""
        assume(self.current_thread_id is not None)
        assume(self.current_thread_id in self.conversations)

        self.conversations[self.current_thread_id]["messages"].append(message)
        self.conversations[self.current_thread_id]["last_updated"] = datetime.now()

        # Update memory system message counts
        for system_name in self.memory_systems:
            if self.memory_systems[system_name]["initialized"]:
                self.memory_systems[system_name]["message_count"] += 1

        return f"Added message to thread {self.current_thread_id}"

    @rule()
    def query_memory_system(self, system_name=memory_system_strategy(), query=st.text(min_size=1, max_size=200)):
        """Query a memory system."""
        assume(system_name in self.memory_systems)
        assume(self.memory_systems[system_name]["initialized"])

        # Simulate memory query
        thread_count = len(self.conversations)
        message_count = sum(len(conv.get("messages", [])) for conv in self.conversations)

        return {
            "system": system_name,
            "query": query,
            "thread_count": thread_count,
            "message_count": message_count,
            "timestamp": datetime.now().isoformat(),
        }

    @rule()
    def cleanup_old_conversations(self, max_age_hours=st.integers(min_value=1, max_value=24)):
        """Clean up old conversations."""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        old_threads = [
            thread_id for thread_id, conv in self.conversations.items()
            if conv.get("last_activity", datetime.now()) < cutoff_time
        ]

        for thread_id in old_threads:
            del self.conversations[thread_id]

        return f"Cleaned up {len(old_threads)} old conversations"


class DatabaseStateMachine(RuleBasedStateMachine):
    """Stateful testing for database operations."""

    def __init__(self):
        super().__init__()
        self.connection = None
        self.tables = {}
        self.transaction_active = False

    @rule()
    def connect_database(self, dsn=database_dsn_strategy()):
        """Connect to a database."""
        assume(not self.connection)
        self.connection = f"connected_to_{dsn}"
        return f"Connected to {dsn}"

    @rule()
    def create_table(self, table_name=st.text(min_size=1, max_size=50)):
        """Create a table."""
        assume(self.connection)
        assume(table_name not in self.tables)

        self.tables[table_name] = {"columns": [], "rows": [], "created_at": datetime.now()}
        return f"Created table {table_name}"

    @rule()
    def insert_data(self, table_name=st.text(min_size=1, max_size=50), data=st.dictionaries(st.text(), st.text())):
        """Insert data into a table."""
        assume(self.connection)
        assume(table_name in self.tables)

        self.tables[table_name]["rows"].append(data)
        return f"Inserted data into {table_name}"

    @rule()
    def query_table(self, table_name=st.text(min_size=1, max_size=50)):
        """Query a table."""
        assume(self.connection)
        assume(table_name in self.tables)

        row_count = len(self.tables[table_name]["rows"])
        return f"Table {table_name} has {row_count} rows"


# ============================================================================
# Advanced Testing Utilities
# ============================================================================


def with_assume_preconditions(*preconditions):
    """Decorator to add assume() preconditions to tests."""

    def decorator(test_func):
        def wrapper(*args, **kwargs):
            for precondition in preconditions:
                assume(precondition(*args, **kwargs))
            return test_func(*args, **kwargs)

        return wrapper

    return decorator


def critical_examples(*examples):
    """Decorator to add critical test examples."""

    def decorator(test_func):
        for example_value in examples:
            test_func = example(example_value)(test_func)
        return test_func

    return decorator


# ============================================================================
# Predefined Test Examples
# ============================================================================

CRITICAL_DSN_EXAMPLES = [
    "postgresql://user:pass@localhost:5432/testdb",
    "sqlite:///test.db",
    "mysql://root@localhost:3306/testdb",
]

CRITICAL_EVAL_PROFILES = ["gold", "real", "mock"]

CRITICAL_MEMORY_SYSTEMS = ["ltst", "cursor", "go_cli", "prime"]

CRITICAL_MESSAGE_EXAMPLES = [
    {"role": "user", "content": "Hello", "thread_id": "test_thread"},
    {"role": "assistant", "content": "Hi there!", "thread_id": "test_thread"},
    {"role": "system", "content": "System message", "thread_id": "test_thread"},
]

# ============================================================================
# Strategy Collections
# ============================================================================

# Common strategy combinations
COMMON_STRATEGIES = {
    "eval_profile": eval_profile_strategy(),
    "memory_system": memory_system_strategy(),
    "dspy_model": dspy_model_strategy(),
    "database_dsn": database_dsn_strategy(),
    "conversation_message": conversation_message_strategy(),
    "retrieval_result": retrieval_result_strategy(),
    "embedding_vector": embedding_vector_strategy(),
    "evaluation_metrics": evaluation_metrics_strategy(),
}

# Stateful testing machines
STATEFUL_MACHINES = {"memory_system": MemorySystemStateMachine, "database": DatabaseStateMachine}
