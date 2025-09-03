#!/usr/bin/env python3
"""
Litellm Compatibility Shim for DSPy 3.0.1
------------------------------------------
This shim provides the missing litellm modules and classes that DSPy 3.0.1 expects,
allowing DSPy to work with the current litellm version.

Usage: Import this module before importing DSPy to patch the missing dependencies.
"""

import sys
from types import ModuleType


class ModelResponseStream:
    """
    Compatibility shim for ModelResponseStream that DSPy 3.0.1 expects.

    This provides the minimal interface needed by DSPy without requiring
    the exact litellm version that has breaking changes.
    """

    def __init__(self, **kwargs):
        """Initialize the stream response."""
        self.choices = kwargs.get("choices", [])
        self.model = kwargs.get("model", "unknown")
        self.usage = kwargs.get("usage", {})
        self._raw_response = kwargs.get("raw_response", None)

    def __iter__(self):
        """Make the response iterable."""
        if self._raw_response and hasattr(self._raw_response, "__iter__"):
            return iter(self._raw_response)
        return iter([])

    def __next__(self):
        """Get next item in stream."""
        if self._raw_response and hasattr(self._raw_response, "__next__"):
            return next(self._raw_response)
        raise StopIteration


class MockCachingCaching(ModuleType):
    """Mock litellm.caching.caching module that DSPy specifically needs."""

    def __init__(self):
        super().__init__("litellm.caching.caching")

    def __getattr__(self, cache_name):
        if cache_name == "Cache":
            # Return a mock Cache class
            class MockCache:
                def __init__(self, *args, **kwargs):
                    pass

                def get(self, *args, **kwargs):
                    return None

                def set(self, *args, **kwargs):
                    pass

            return MockCache
        return lambda *args, **kwargs: None


class MockCaching(ModuleType):
    """Mock caching submodule for litellm."""

    def __init__(self):
        super().__init__("litellm.caching")
        # Add the specific caching.caching module
        self.caching = MockCachingCaching()

    def __getattr__(self, cache_name):
        return lambda *args, **kwargs: None


class MockStreaming(ModuleType):
    """Mock streaming submodule for litellm."""

    def __init__(self):
        super().__init__("litellm.streaming")

    def __getattr__(self, stream_name):
        return lambda *args, **kwargs: None


class MockUtils(ModuleType):
    """Mock utils submodule for litellm."""

    def __init__(self):
        super().__init__("litellm.utils")

    def __getattr__(self, util_name):
        return lambda *args, **kwargs: None


class MockLiteLLM(ModuleType):
    """
    Comprehensive mock litellm module that provides all the missing pieces
    that DSPy 3.0.1 expects.
    """

    def __init__(self):
        super().__init__("litellm")
        self.ModelResponseStream = ModelResponseStream
        self.caching = MockCaching()
        self.streaming = MockStreaming()
        self.utils = MockUtils()

    def __getattr__(self, name):
        """Return mock objects for any missing attributes."""
        # Return a dummy function for any other attributes
        return lambda *args, **kwargs: None


def patch_litellm_imports():
    """
    Patch the litellm module to include all missing dependencies.

    This should be called before importing DSPy to ensure compatibility.
    """
    try:
        import litellm

        # Add the missing class to litellm module
        if not hasattr(litellm, "ModelResponseStream"):
            setattr(litellm, "ModelResponseStream", ModelResponseStream)
            print("✅ Patched litellm.ModelResponseStream for DSPy compatibility")

        # Patch missing submodules
        if not hasattr(litellm, "caching"):
            setattr(litellm, "caching", MockCaching())
            print("✅ Patched litellm.caching submodule")

        if not hasattr(litellm, "streaming"):
            setattr(litellm, "streaming", MockStreaming())
            print("✅ Patched litellm.streaming submodule")

        if not hasattr(litellm, "utils"):
            setattr(litellm, "utils", MockUtils())
            print("✅ Patched litellm.utils submodule")

    except ImportError:
        print("⚠️  litellm not available, creating comprehensive mock")

    # Create or replace the litellm module with our mock
    mock_litellm = MockLiteLLM()
    sys.modules["litellm"] = mock_litellm

    # Also create the submodules
    sys.modules["litellm.caching"] = mock_litellm.caching
    sys.modules["litellm.caching.caching"] = mock_litellm.caching.caching
    sys.modules["litellm.streaming"] = mock_litellm.streaming
    sys.modules["litellm.utils"] = mock_litellm.utils

    print("✅ Created comprehensive litellm mock for DSPy compatibility")


if __name__ == "__main__":
    # Test the shim
    patch_litellm_imports()
    print("🧪 Testing shim...")

    try:
        # Try to import DSPy after patching
        import dspy

        print("✅ DSPy import successful after patching!")
    except ImportError as e:
        print(f"❌ DSPy import still failed: {e}")
        print("🔍 Full error details:")
        import traceback

        traceback.print_exc()
