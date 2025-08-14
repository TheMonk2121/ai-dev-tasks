#!/usr/bin/env python3
"""
Utils Package

Utility modules for the DSPy RAG system.
"""

__version__ = "1.0.0"

# Ensure submodules are importable via 'utils.<module>' for test patching
# Importing here registers attributes on the package (used by tests mocking paths)
from . import (
    anchor_metadata_parser,  # noqa: F401
    config_manager,  # noqa: F401
    database_resilience,  # noqa: F401
    enhanced_file_validator,  # noqa: F401
    error_pattern_recognition,  # noqa: F401
    hotfix_templates,  # noqa: F401
    logger,  # noqa: F401
    memory_rehydrator,  # noqa: F401
    metadata_extractor,  # noqa: F401
    model_specific_handling,  # noqa: F401
    opentelemetry_config,  # noqa: F401
    prompt_sanitizer,  # noqa: F401
    rag_compatibility_shim,  # noqa: F401
    retry_wrapper,  # noqa: F401
    secrets_manager,  # noqa: F401
    security,  # noqa: F401
    timeout_config,  # noqa: F401
    tokenizer,  # noqa: F401
    validator,  # noqa: F401
)
