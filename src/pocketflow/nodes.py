"""Core PocketFlow nodes wrapping existing Lean Hybrid Memory operations."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from pocketflow.shared_state import (
    ConversationSummary,
    ConversationTurn,
    RetrievedHit,
    SharedState,
)

PersistTurnFn = Callable[[SharedState, ConversationTurn], ConversationTurn]
SummarizeFn = Callable[[Sequence[ConversationTurn]], ConversationSummary | str]
ExtractFactsFn = Callable[[Sequence[ConversationTurn], str], list[dict[str, Any]]]
IndexFactsFn = Callable[[list[dict[str, Any]], SharedState], None]
RetrieveFn = Callable[[SharedState], list[RetrievedHit]]
ComposeAnswerFn = Callable[[SharedState], str]


@dataclass
class AppendTurnNode:
    """Write-through append for the latest conversation turn."""

    persist_turn: PersistTurnFn

    def run(self, state: SharedState) -> SharedState:
        if not state.turns:
            return state
        latest = state.turns[-1]
        saved = self.persist_turn(state, latest)
        state.turns[-1] = saved
        return state


@dataclass
class MaybeSummarizeNode:
    """Optional summarization of long transcripts."""

    summarizer: SummarizeFn
    token_budget: int = 4096

    def run(self, state: SharedState) -> SharedState:
        total_tokens = sum(t.metadata.get("token_count", 0) for t in state.turns)
        if total_tokens <= self.token_budget:
            return state
        summary = self.summarizer(state.turns)
        if isinstance(summary, ConversationSummary):
            state.summary = summary
        else:
            token_count = len(summary.split())
            state.summary = ConversationSummary(text=summary, token_count=token_count)
        return state


@dataclass
class ExtractFactsNode:
    """Derive facts/entities from recent turns."""

    extractor: ExtractFactsFn

    def run(self, state: SharedState) -> SharedState:
        summary_text = state.summary.text if state.summary else ""
        facts = self.extractor(state.turns, summary_text)
        state.new_facts.extend(facts)
        return state


@dataclass
class IndexFactsNode:
    """Persist extracted facts and keep shared state consistent."""

    indexer: IndexFactsFn

    def run(self, state: SharedState) -> SharedState:
        if not state.new_facts:
            return state
        self.indexer(state.new_facts, state)
        state.new_facts.clear()
        return state


@dataclass
class RetrieveNode:
    """Generic retrieval node for a specific source."""

    source: str
    retriever: RetrieveFn

    def run(self, state: SharedState) -> SharedState:
        hits = self.retriever(state)
        if hits:
            state.retrieval.hits[self.source] = hits
        return state


@dataclass
class MergeResultsNode:
    """Merge results from multiple retrieval channels using custom policy."""

    merger: Callable[[dict[str, list[RetrievedHit]]], list[RetrievedHit]]

    def run(self, state: SharedState) -> SharedState:
        state.retrieval.merged = self.merger(state.retrieval.hits)
        return state


@dataclass
class ComposeAnswerNode:
    """LLM answer composition using current shared state."""

    composer: ComposeAnswerFn

    def run(self, state: SharedState) -> SharedState:
        state.answer = self.composer(state)
        return state


__all__ = [
    "AppendTurnNode",
    "MaybeSummarizeNode",
    "ExtractFactsNode",
    "IndexFactsNode",
    "RetrieveNode",
    "MergeResultsNode",
    "ComposeAnswerNode",
]
