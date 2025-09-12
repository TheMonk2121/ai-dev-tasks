from __future__ import annotations
from enum import Enum
import os
#!/usr/bin/env python3

class AgentType(Enum):
    """Enumeration of available agent types for Cursor AI framework.

    Defined in a stable module so identity remains consistent across reloads.
    """

    NATIVE_AI = "native_ai"
    RESEARCH = "research"
    CODER = "coder"
    DOCUMENTATION = "documentation"
