#!/usr/bin/env python3

"""
Compatibility wrapper exposing EnhancedRAGSystem for tests.
Delegates to the existing enhanced RAG interface via the RAG shim.
"""

from typing import Any, Dict, Optional

from dspy_modules.enhanced_rag_system import create_enhanced_rag_interface


class EnhancedRAGSystem:
    """Minimal facade used by performance tests.

    Provides ask_question() which delegates to the enhanced RAG interface's ask().
    """

    def __init__(self, db_dsn: str | None = None, model: str | None = None) -> None:
        self._iface = create_enhanced_rag_interface(db_dsn, None, model)

    def ask_question(self, question: str) -> dict[str, Any]:
        return self._iface.ask(question)
