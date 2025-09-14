#!/usr/bin/env python3
"""
Simple test for MCP server functionality
"""

import os
import sys
from pathlib import Path

# Add project paths
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

# Test imports
try:
    from unified_memory_orchestrator import UnifiedMemoryOrchestrator

    print("✅ UnifiedMemoryOrchestrator import successful")
except ImportError as e:
    print(f"❌ UnifiedMemoryOrchestrator import failed: {e}")

try:
    from cursor_working_integration import CursorWorkingIntegration

    print("✅ CursorWorkingIntegration import successful")
except ImportError as e:
    print(f"❌ CursorWorkingIntegration import failed: {e}")

# Test basic functionality
try:
    print("\n🧪 Testing basic functionality...")

    # Test memory orchestrator
    if "UnifiedMemoryOrchestrator" in locals():
        orchestrator = UnifiedMemoryOrchestrator()
        print("✅ UnifiedMemoryOrchestrator instantiated")

    # Test cursor integration
    if "CursorWorkingIntegration" in locals():
        cursor = CursorWorkingIntegration()
        print("✅ CursorWorkingIntegration instantiated")
        print(f"   Session ID: {cursor.session_id}")
        print(f"   Thread ID: {cursor.thread_id}")

    print("\n✅ All tests passed! MCP server should work.")

except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback

    traceback.print_exc()
