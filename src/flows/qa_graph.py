from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict
from src.agents.qa import Deps, QAAnswer, agent
    from pydantic_graph import Graph, Node  # type: ignore[import-untyped]
        import httpx
from typing import Any, Dict, List, Optional, Union
"""Typed graph with state persistence for QA flows."""





if TYPE_CHECKING:  # type-only imports to satisfy Pyright without runtime dependency
else:
    Graph = object  # type: ignore[assignment]

    class Node:  # type: ignore
        pass


class FlowState(BaseModel):
    """State for the QA flow."""

    model_config = ConfigDict(strict=True)
    flow_id: UUID
    last_node: str | None = None
    question: str
    draft: str | None = None
    final: QAAnswer | None = None


# Node types
@dataclass
class Start(Node[FlowState, Literal["Draft", "End"]]):  # type: ignore
    """Starting node that determines flow path."""

    async def call(self, state: FlowState) -> type[Draft] | type[End]:
        return Draft if len(state.question) > 120 else End


@dataclass
class Draft(Node[FlowState, Literal["End"]]):  # type: ignore
    """Draft generation node."""

    async def call(self, state: FlowState) -> type[End]:

        deps = Deps(http_client=httpx.AsyncClient())
        res = await agent.run(state.question, deps=deps)  # returns AgentRunResult[QAAnswer]
        state.draft = res.data.answer  # type: ignore[attr-defined]
        return End


@dataclass
class End(Node[FlowState, None]):  # type: ignore
    """Terminal node."""

    async def call(self, state: FlowState) -> None:
        # no-op, terminal node
        return None


graph = Graph[FlowState, Start, End](start=Start(), end=End())  # type: ignore


# ----- A simple durable runner with persistence hooks -----
class FlowStore:
    """Abstract flow store for persistence."""

    async def load(self, flow_id: UUID) -> FlowState | None:
        """Load flow state by ID."""
        # Implementation would load from database/storage
        return None

    async def save(self, state: FlowState) -> None:
        """Save flow state."""
        # Implementation would save to database/storage
        pass


async def run_flow(store: FlowStore, state: FlowState) -> FlowState:
    """Run a flow with persistence between nodes."""
    node: type[Node] | None = Start  # type: ignore
    while node is not None:
        # record "where we are" for resumability
        state.last_node = node.__name__
        await store.save(state)
        node = await graph.next(state, node)  # type: ignore[attr-defined]
    await store.save(state)
    return state


def export_mermaid_diagram(output_path: str = "docs/qa_graph.png") -> None:
    """Export the graph as a Mermaid diagram."""
    graph.mermaid_save(output_path)  # type: ignore[call-arg]
