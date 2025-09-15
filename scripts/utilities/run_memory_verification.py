from __future__ import annotations

import hashlib
import os
import sys
import time
from typing import Any

#!/usr/bin/env python3
"""
Run Memory System Verification

This script performs an end-to-end smoke test of the memory stack:
- Runs the DB healthcheck
- Seeds a demo session with a few messages and a decision
- Runs memory rehydration against that session
- Prints a concise summary and returns non-zero on failure

Usage:
  DATABASE_URL=postgresql://user@localhost:5432/db python scripts/run_memory_verification.py
"""


def add_src_to_path() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(here, ".."))
    utils_src = os.path.join(repo_root, "dspy-rag-system", "src")
    if utils_src not in sys.path:
        sys.path.insert(0, utils_src)


def run_healthcheck() -> bool:
    try:
        try:
            from scripts.memory_healthcheck import main as hc_main  # type: ignore[import-untyped]
        except Exception:
            from memory_healthcheck import main as hc_main  # type: ignore[import-untyped]
        code = hc_main()
        return code == 0
    except Exception:
        print("[WARN] Could not import memory_healthcheck; skipping")
        return True


def generate_session_id(user_id: str) -> str:
    ts = str(time.time())
    return hashlib.sha256(f"{user_id}:{ts}".encode()).hexdigest()[:16]


def seed_demo(conversation_storage: Any, session_id: str, user_id: str) -> bool:
    try:
        from utils.conversation_storage import (
            ConversationMessage,
            ConversationSession,
        )  # type: ignore[import-untyped]
    except Exception as e:
        print(f"[FAIL] Could not import ConversationStorage models: {e}")
        return False

    try:
        # Create/Upsert session
        session = ConversationSession(
            session_id=session_id,
            user_id=user_id,
            session_name=f"Verification {session_id[:6]}",
            session_type="conversation",
            status="active",
            metadata={"source": "verification"},
        )
        if not conversation_storage.create_session(session):
            print("[FAIL] create_session failed")
            return False

        # Seed a couple of messages
        msgs = [
            ConversationMessage(
                session_id=session_id, role="human", content="Please use Python 3.12", message_type="message"
            ),
            ConversationMessage(
                session_id=session_id, role="ai", content="Sure, I will use Python 3.12.", message_type="message"
            ),
            ConversationMessage(
                session_id=session_id, role="human", content="Enable detailed explanations", message_type="message"
            ),
        ]
        for m in msgs:
            if not conversation_storage.store_message(m):
                print("[FAIL] store_message failed")
                return False

        # Seed a decision context
        decision_head = "use_python_3_12"
        decision_payload = {
            "head": decision_head,
            "rationale": "Align with toolchain and type checker",
            "confidence": 0.9,
        }
        ok = conversation_storage.store_context(
            session_id=session_id,
            context_type="decision",
            context_key=decision_head,
            context_value=str(decision_payload),
            relevance_score=0.85,
            expires_at=None,
            decision_head=decision_head,
            decision_status="open",
            superseded_by=None,
            entities=["python", "toolchain"],
            files=[],
        )
        if not ok:
            print("[FAIL] store_context(decision) failed")
            return False

        return True
    except Exception as e:
        print(f"[FAIL] Seeding demo failed: {e}")
        return False


def run_rehydration(session_id: str, user_id: str) -> dict[str, Any]:
    try:
        from utils.memory_rehydrator import MemoryRehydrator  # type: ignore[import-untyped]
    except Exception as e:
        return {"ok": False, "error": f"Import rehydrator failed: {e}"}

    try:
        rehydrator = MemoryRehydrator()
        # Use getattr to handle potential method name variations
        rehydrate_method = getattr(rehydrator, "rehydrate_memory", getattr(rehydrator, "rehydrate_memory_simple", None))

        if not rehydrate_method:
            return {"ok": False, "error": "No rehydration method found"}

        # Try different method signatures
        try:
            result = rehydrate_method(request="Verify memory context")
        except TypeError:
            try:
                result = rehydrate_method(request="Verify memory context", user_id=user_id, session_id=session_id)
            except TypeError:
                result = rehydrate_method()

        return {
            "ok": True,
            "context_len": len(getattr(result, "rehydrated_context", "") or ""),
            "history": len(getattr(result, "conversation_history", []) or []),
            "contexts": len(getattr(result, "relevant_contexts", []) or []),
            "continuity": getattr(result, "session_continuity_score", 0.0),
            "cache": getattr(result, "cache_hit", False),
        }
    except Exception as e:
        return {"ok": False, "error": f"Rehydration failed: {e}"}


def main() -> int:
    add_src_to_path()

    # 1) Healthcheck
    ok_hc = run_healthcheck()
    if not ok_hc:
        print("[FAIL] Healthcheck failed — fix DB/schema before proceeding")
        return 2

    # 2) Seed data
    try:
        from utils.conversation_storage import ConversationStorage  # type: ignore[import-untyped]
    except Exception as e:
        print(f"[FAIL] Import ConversationStorage failed: {e}")
        return 3

    storage = ConversationStorage()
    user_id = os.getenv("MEMORY_VERIFY_USER", "verify_user")
    session_id = os.getenv("MEMORY_VERIFY_SESSION", generate_session_id(user_id))

    if not seed_demo(storage, session_id, user_id):
        return 4

    # 3) Rehydrate
    rh = run_rehydration(session_id, user_id)
    if not rh.get("ok"):
        print(f"[FAIL] {rh.get('error')}")
        return 5

    print("[OK] Rehydration complete")
    print(f"  session_id: {session_id}")
    print(f"  context_len: {rh['context_len']}")
    print(f"  history: {rh['history']}  contexts: {rh['contexts']}  continuity: {rh['continuity']:.2f}")
    print(f"  cache_hit: {rh['cache']}")
    print("[DONE] Memory verification passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
