#!/usr/bin/env python3
"""
Enforce chunking standards in conversation capture.
"""

import os
import sys

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utilities"))

from atlas_enhanced_chunking import AtlasEnhancedChunking
from cursor_query_storage import CursorQueryStorage


class StandardsCompliantConversationCapture:
    """Conversation capture that enforces chunking and embedding standards."""

    def __init__(self, dsn: str | None = None) -> None:
        self.dsn: str = dsn or os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")

        # Use standards-compliant components
        self.chunker: AtlasEnhancedChunking = AtlasEnhancedChunking(self.dsn)
        self.storage: CursorQueryStorage = CursorQueryStorage(self.dsn)

        # Verify standards compliance
        self._verify_standards_compliance()

    def _verify_standards_compliance(self) -> None:
        """Verify that components meet project standards."""
        assert self.chunker.embedding_dim == 384, f"Expected 384 dims, got {self.chunker.embedding_dim}"
        assert self.storage.embedding_dim == 384, f"Expected 384 dims, got {self.storage.embedding_dim}"

        # Verify chunking parameters (20-25% overlap of max chunk size)
        assert self.chunker.max_chunk_size >= 350, f"Chunk size too small: {self.chunker.max_chunk_size}"
        assert self.chunker.max_chunk_size <= 600, f"Chunk size too large: {self.chunker.max_chunk_size}"

        # Check overlap is 20-25% of max chunk size
        min_overlap = int(self.chunker.max_chunk_size * 0.20)
        max_overlap = int(self.chunker.max_chunk_size * 0.25)
        assert (
            self.chunker.overlap_size >= min_overlap
        ), f"Overlap too small: {self.chunker.overlap_size} (should be >= {min_overlap})"
        assert (
            self.chunker.overlap_size <= max_overlap
        ), f"Overlap too large: {self.chunker.overlap_size} (should be <= {max_overlap})"

        print("✅ Standards compliance verified")

    def capture_conversation_with_chunking(
        self, session_id: str, role: str, content: str, metadata: dict[str, str | bool] | None = None
    ) -> list[str]:
        """Capture conversation with proper chunking and standards compliance."""

        print(f"📝 Capturing {role} message with chunking...")

        # Chunk the conversation
        chunk_ids = self.chunker.chunk_conversation_turn(
            session_id=session_id, role=role, content=content, metadata=metadata
        )

        print(f"✅ Created {len(chunk_ids)} chunks for {role} message")
        return chunk_ids

    def get_chunking_stats(self) -> dict[str, str | int | bool]:
        """Get chunking statistics."""
        return {
            "embedding_dimensions": self.chunker.embedding_dim,
            "max_chunk_size": self.chunker.max_chunk_size,
            "overlap_size": self.chunker.overlap_size,
            "min_chunk_size": self.chunker.min_chunk_size,
            "embedding_model": "all-MiniLM-L6-v2",
            "storage_table": "conv_chunks",
            "standards_compliant": True,
        }


def main() -> int:
    """Test the standards-compliant conversation capture."""

    print("🧠 Testing Standards-Compliant Conversation Capture")
    print("=" * 60)

    # Set proper database connection
    os.environ["POSTGRES_DSN"] = "postgresql://danieljacobs@localhost:5432/ai_agency"

    try:
        # Initialize capture system
        capture = StandardsCompliantConversationCapture()

        # Test conversation
        session_id = "test_session_123"
        role = "user"
        content = "How do I implement user authentication in FastAPI? I need to create a secure login system with JWT tokens and password hashing using bcrypt. The system should also support password reset functionality with email verification."
        metadata: dict[str, str | bool] = {"test": True}

        # Capture with chunking
        chunk_ids = capture.capture_conversation_with_chunking(
            session_id=session_id, role=role, content=content, metadata=metadata
        )

        # Show stats
        stats: Any = capture.get_chunking_stats()
        print("\n📊 Chunking Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")

        print(f"\n✅ Successfully created {len(chunk_ids)} chunks")
        print("🎯 Standards-compliant chunking is working!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
