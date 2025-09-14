#!/usr/bin/env python3
"""
Enforce chunking and embedding standards across the repository.
"""

import os
import re


def fix_embedding_dimensions() -> list[str]:
    """Fix embedding dimensions from 1024 to 384."""

    files_to_fix = [
        "scripts/utilities/cursor_query_storage.py",
        "scripts/utilities/atlas_graph_storage.py",
        "scripts/utilities/atlas_enhanced_chunking.py",
        "scripts/utilities/atlas_unified_graph_system.py",
    ]

    fixed_files = []

    for file_path in files_to_fix:
        if os.path.exists(file_path):
            with open(file_path) as f:
                content = f.read()

            # Fix embedding dimensions
            original_content = content
            content = re.sub(r"embedding_dim = 1024", "embedding_dim = 384", content)
            content = re.sub(r"vector\(1024\)", "vector(384)", content)

            if content != original_content:
                with open(file_path, "w") as f:
                    _ = f.write(content)
                fixed_files.append(file_path)
                print(f"✅ Fixed embedding dimensions in {file_path}")

    return fixed_files


def fix_embedding_models() -> list[str]:
    """Fix embedding models from BAAI/bge-large-en-v1.5 to all-MiniLM-L6-v2."""

    files_to_fix = [
        "scripts/utilities/cursor_query_storage.py",
        "scripts/utilities/atlas_graph_storage.py",
        "scripts/utilities/atlas_enhanced_chunking.py",
        "scripts/utilities/atlas_unified_graph_system.py",
    ]

    fixed_files = []

    for file_path in files_to_fix:
        if os.path.exists(file_path):
            with open(file_path) as f:
                content = f.read()

            # Fix embedding model
            original_content = content
            content = re.sub(
                r'SentenceTransformer\("BAAI/bge-large-en-v1\.5"\)', 'SentenceTransformer("all-MiniLM-L6-v2")', content
            )

            if content != original_content:
                with open(file_path, "w") as f:
                    _ = f.write(content)
                fixed_files.append(file_path)
                print(f"✅ Fixed embedding model in {file_path}")

    return fixed_files


def create_standards_enforcement_script() -> str:
    """Create a script to enforce chunking standards in conversation capture."""

    script_content = '''#!/usr/bin/env python3
"""
Enforce chunking standards in conversation capture.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utilities"))

from atlas_enhanced_chunking import AtlasEnhancedChunking
from cursor_query_storage import CursorQueryStorage

class StandardsCompliantConversationCapture:
    """Conversation capture that enforces chunking and embedding standards."""
    
    def __init__(self, dsn: str = None):
        self.dsn = dsn or os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
        
        # Use standards-compliant components
        self.chunker = AtlasEnhancedChunking(self.dsn)
        self.storage = CursorQueryStorage(self.dsn)
        
        # Verify standards compliance
        self._verify_standards_compliance()
    
    def _verify_standards_compliance(self):
        """Verify that components meet project standards."""
        assert self.chunker.embedding_dim == 384, f"Expected 384 dims, got {self.chunker.embedding_dim}"
        assert self.storage.embedding_dim == 384, f"Expected 384 dims, got {self.storage.embedding_dim}"
        
        # Verify chunking parameters
        assert self.chunker.max_chunk_size >= 350, f"Chunk size too small: {self.chunker.max_chunk_size}"
        assert self.chunker.max_chunk_size <= 600, f"Chunk size too large: {self.chunker.max_chunk_size}"
        assert self.chunker.overlap_size >= 20, f"Overlap too small: {self.chunker.overlap_size}"
        assert self.chunker.overlap_size <= 25, f"Overlap too large: {self.chunker.overlap_size}"
        
        print("✅ Standards compliance verified")
    
    def capture_conversation_with_chunking(self, session_id: str, role: str, content: str, metadata: Dict[str, Any] = None) -> List[str]:
        """Capture conversation with proper chunking and standards compliance."""
        
        print(f"📝 Capturing {role} message with chunking...")
        
        # Chunk the conversation
        chunk_ids = self.chunker.chunk_conversation_turn(
            session_id=session_id,
            role=role,
            content=content,
            metadata=metadata
        )
        
        print(f"✅ Created {len(chunk_ids)} chunks for {role} message")
        return chunk_ids
    
    def get_chunking_stats(self) -> Dict[str, Any]:
        """Get chunking statistics."""
        return {
            "embedding_dimensions": self.chunker.embedding_dim,
            "max_chunk_size": self.chunker.max_chunk_size,
            "overlap_size": self.chunker.overlap_size,
            "min_chunk_size": self.chunker.min_chunk_size,
            "embedding_model": "all-MiniLM-L6-v2",
            "storage_table": "conv_chunks",
            "standards_compliant": True
        }

def main():
    """Test the standards-compliant conversation capture."""
    
    print("🧠 Testing Standards-Compliant Conversation Capture")
    print("=" * 60)
    
    try:
        # Initialize capture system
        capture = StandardsCompliantConversationCapture()
        
        # Test conversation
        test_conversation = {
            "session_id": "test_session_123",
            "role": "user",
            "content": "How do I implement user authentication in FastAPI? I need to create a secure login system with JWT tokens and password hashing using bcrypt. The system should also support password reset functionality with email verification.",
            "metadata": {"test": True}
        }
        
        # Capture with chunking
        chunk_ids = capture.capture_conversation_with_chunking(**test_conversation)
        
        # Show stats
        stats = capture.get_chunking_stats()
        print(f"\\n📊 Chunking Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print(f"\\n✅ Successfully created {len(chunk_ids)} chunks")
        print("🎯 Standards-compliant chunking is working!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''

    script_path = "scripts/test_standards_compliant_chunking.py"
    with open(script_path, "w") as f:
        _ = f.write(script_content)

    return script_path


def main():
    """Main enforcement function."""

    print("🔧 Enforcing Chunking & Embedding Standards")
    print("=" * 50)

    # Fix embedding dimensions
    print("\\n1. Fixing embedding dimensions...")
    fixed_dims = fix_embedding_dimensions()
    print(f"   Fixed {len(fixed_dims)} files")

    # Fix embedding models
    print("\\n2. Fixing embedding models...")
    fixed_models = fix_embedding_models()
    print(f"   Fixed {len(fixed_models)} files")

    # Create standards enforcement script
    print("\\n3. Creating standards enforcement script...")
    script_path = create_standards_enforcement_script()
    print(f"   Created {script_path}")

    print("\\n✅ Standards enforcement complete!")
    print("\\n📋 Next Steps:")
    print("   1. Update cursor_atlas_integration.py to use chunking")
    print("   2. Migrate from atlas_node to conv_chunks for conversations")
    print("   3. Test the standards-compliant chunking system")
    print(f"   4. Run: uv run python {script_path}")


if __name__ == "__main__":
    main()
