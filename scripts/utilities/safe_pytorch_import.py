from __future__ import annotations
import inspect
import sys
from typing import Any
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Safe PyTorch Import Wrapper

This module provides a workaround for the Python 3.12 + PyTorch 2.8.0
inspect module compatibility issue by patching the problematic inspect
functions before PyTorch imports.
"""

def patch_inspect_for_pytorch():
    """Patch inspect module functions to handle PyTorch custom ops safely."""
    # Store original functions BEFORE patching
    original_functions = {
        "getframeinfo": inspect.getframeinfo,
        "findsource": inspect.findsource,
        "getmodule": inspect.getmodule,
        "getabsfile": inspect.getabsfile,
        "getsourcefile": inspect.getsourcefile,
    }

    def safe_getframeinfo(frame: Any, context: int = 1) -> Any:
        """Safe wrapper for inspect.getframeinfo that handles PyTorch custom ops."""
        try:
            return original_functions["getframeinfo"](frame, context)
        except AttributeError as e:
            if "'function' object has no attribute 'endswith'" in str(e):
                # This is the specific PyTorch 2.8.0 + Python 3.12 issue
                # Create a minimal frame info object using the current frame as fallback
                try:
                    current_frame = inspect.currentframe()
                    if current_frame:
                        return inspect.FrameInfo(
                            frame=current_frame,
                            filename="<pytorch_custom_op>",
                            lineno=0,
                            function="<custom_op>",
                            code_context=None,
                            index=0,
                        )
                except Exception:
                    pass

                # If all else fails, return a simple tuple-like object
                class MockFrameInfo:
                    def __init__(self):
                        self.filename = "<pytorch_custom_op>"
                        self.lineno = 0
                        self.function = "<custom_op>"
                        self.code_context = None
                        self.index = 0

                return MockFrameInfo()
            raise

    def safe_findsource(obj: Any) -> tuple[list[str], int]:
        """Safe wrapper for inspect.findsource that handles PyTorch custom ops."""
        try:
            return original_functions["findsource"](obj)
        except (OSError, TypeError, AttributeError):
            # Return minimal source for PyTorch custom ops
            return (["# PyTorch custom operation"], 0)

    def safe_getmodule(obj: Any, file: str | None = None) -> Any | None:
        """Safe wrapper for inspect.getmodule that handles PyTorch custom ops."""
        try:
            return original_functions["getmodule"](obj, file)
        except (TypeError, AttributeError):
            # Return None for problematic objects
            return None

    def safe_getabsfile(obj: Any) -> str:
        """Safe wrapper for inspect.getabsfile that handles PyTorch custom ops."""
        try:
            return original_functions["getabsfile"](obj)
        except (TypeError, AttributeError):
            return "<pytorch_custom_op>"

    def safe_getsourcefile(obj: Any) -> str | None:
        """Safe wrapper for inspect.getsourcefile that handles PyTorch custom ops."""
        try:
            return original_functions["getsourcefile"](obj)
        except (TypeError, AttributeError):
            return None

    # Apply patches
    inspect.getframeinfo = safe_getframeinfo
    inspect.findsource = safe_findsource
    inspect.getmodule = safe_getmodule
    inspect.getabsfile = safe_getabsfile
    inspect.getsourcefile = safe_getsourcefile

    return original_functions

def restore_inspect(original_functions: dict):
    """Restore original inspect functions."""
    inspect.getframeinfo = original_functions["getframeinfo"]
    inspect.findsource = original_functions["findsource"]
    inspect.getmodule = original_functions["getmodule"]
    inspect.getabsfile = original_functions["getabsfile"]
    inspect.getsourcefile = original_functions["getsourcefile"]

# Auto-patch when imported
_original_functions = patch_inspect_for_pytorch()

# Export the restoration function for cleanup if needed
__all__ = ["patch_inspect_for_pytorch", "restore_inspect", "_original_functions"]
