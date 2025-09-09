#!/usr/bin/env python3
import sys
from typing import Any

sys.path.append("src")

from dspy_modules.mcp_document_processor import MCPDocumentProcessor
from dspy_modules.mcp_module import MCPDocumentModule
from dspy_modules.mcp_signatures import MCPDocumentSignature


class TestMCPDocumentSignatureModule:
    def test_signature_fields(self):
        sig = MCPDocumentSignature(
            document_source="dummy",
            chunks=[],
            metadata={},
        )
        # Ensure signature exposes expected fields
        assert hasattr(sig, "document_source")
        assert hasattr(sig, "chunks")
        assert hasattr(sig, "metadata")

    def test_module_basic_adaptation(self, monkeypatch):
        module = MCPDocumentModule()

        # Monkeypatch the class-level __call__ to avoid actual server work
        def fake_forward(self, document_source: str, **kwargs) -> dict[str, Any]:  # type: ignore[no-redef]
            return {
                "chunks": [
                    {"text": "chunk one"},
                    {"text": "chunk two"},
                ],
                "metadata": {
                    "content_type": "text/plain",
                    "server_type": "file_system",
                },
            }

        monkeypatch.setattr(MCPDocumentProcessor, "__call__", fake_forward, raising=True)

        out = module("/some/file.txt")
        assert isinstance(out, dict)
        assert out["chunks"] == ["chunk one", "chunk two"]
        assert out["metadata"]["server_type"] == "file_system"
