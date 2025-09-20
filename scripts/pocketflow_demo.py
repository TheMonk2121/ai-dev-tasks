"""PocketFlow smoke runner for default capture and answer flows."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime, timezone

from pocketflow.integration import default_answer_flow, default_capture_flow
from pocketflow.shared_state import ConversationTurn, RetrievedHit, SharedState


def _build_demo_state(question: str) -> SharedState:
    state = SharedState()
    state.retrieval.query = question
    state.turns.append(
        ConversationTurn(
            turn_id="demo-1",
            thread_id="demo-thread",
            role="user",
            content=question,
            created_at=datetime.now(UTC),
            metadata={"token_count": len(question.split())},
        )
    )
    return state


def main() -> None:
    parser = argparse.ArgumentParser(description="Run PocketFlow demo flows")
    parser.add_argument("question", help="Question to feed into the answer flow")
    args = parser.parse_args()

    state = _build_demo_state(args.question)

    capture_flow = default_capture_flow()
    state = capture_flow.run(state)

    answer_flow = default_answer_flow()
    state = answer_flow.run(state)

    print("=== PocketFlow Demo Result ===")
    print(state.answer or "(no answer produced)")


if __name__ == "__main__":
    main()
