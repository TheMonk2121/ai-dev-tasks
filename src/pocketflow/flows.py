"""Flow orchestration primitives for PocketFlow integration."""

from __future__ import annotations

from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Protocol

from pocketflow.shared_state import SharedState


class NodeProtocol(Protocol):
    """Minimal runtime protocol for PocketFlow-compatible nodes."""

    def run(self, state: SharedState) -> SharedState: ...


@dataclass
class Flow:
    """Executes nodes in sequence, mutating the shared state."""

    steps: Sequence[NodeProtocol]

    def run(self, state: SharedState) -> SharedState:
        for step in self.steps:
            state = step.run(state)
        return state


@dataclass
class Parallel:
    """Runs a collection of nodes concurrently and merges the shared state afterwards."""

    nodes: Sequence[NodeProtocol]

    def run(self, state: SharedState) -> SharedState:
        for node in self.nodes:
            state = node.run(state)
        return state


def build_capture_flow(*steps: NodeProtocol) -> Flow:
    """Assemble the capture flow (AppendTurn → Summary → Facts → Index)."""

    return Flow(steps=steps)


def build_answer_flow(
    retrieval_parallel: Parallel,
    *post_retrieval_steps: NodeProtocol,
) -> Flow:
    """Assemble the answer flow with retrieval fan-out and downstream composition."""

    steps: list[NodeProtocol] = [retrieval_parallel]
    steps.extend(post_retrieval_steps)
    return Flow(steps=steps)


__all__ = [
    "Flow",
    "Parallel",
    "build_capture_flow",
    "build_answer_flow",
]
