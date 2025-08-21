#!/usr/bin/env python3
from enum import Enum


class AgentType(Enum):
    """Enumeration of available agent types for Cursor AI framework.

    Defined in a stable module so identity remains consistent across reloads.
    """

    NATIVE_AI = "native_ai"
    RESEARCH = "research"
    CODER = "coder"
    DOCUMENTATION = "documentation"
