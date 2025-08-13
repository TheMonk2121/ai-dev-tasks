#!/usr/bin/env python3
"""
Import Setup Utility for DSPy RAG System

Centralized utility to handle import path resolution and module imports.
This ensures consistent import behavior across all scripts in the project.
"""

import sys
from pathlib import Path
from typing import List, Optional


def setup_dspy_imports() -> bool:
    """
    Setup proper import paths for the DSPy RAG system.

    Returns:
        bool: True if setup was successful, False otherwise
    """
    # Get the project root directory (dspy-rag-system)
    project_root = find_project_root()
    if not project_root:
        return False

    # Add src directory to Python path
    src_dir = project_root / "src"
    if not src_dir.exists():
        print(f"❌ Error: src directory not found at {src_dir}")
        return False

    # Insert src directory at the beginning of sys.path
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    return True


def find_project_root() -> Optional[Path]:
    """
    Find the DSPy RAG system project root directory.

    Returns:
        Path: Project root directory or None if not found
    """
    # Start from current working directory
    current = Path.cwd()

    # Look for project root by checking for key files/directories
    while current != current.parent:
        # Check if this looks like the project root
        if (current / "src" / "utils" / "anchor_metadata_parser.py").exists():
            return current
        if (current / "pyproject.toml").exists() and (current / "src").exists():
            return current

        current = current.parent

    # If we get here, try to find it relative to the script location
    script_dir = Path(__file__).parent.absolute()
    if (script_dir / "src" / "utils" / "anchor_metadata_parser.py").exists():
        return script_dir

    return None


def import_dspy_module(module_name: str, from_package: str = "utils"):
    """
    Import a module from the DSPy RAG system with proper error handling.

    Args:
        module_name: Name of the module to import
        from_package: Package name (default: "utils")

    Returns:
        The imported module

    Raises:
        ImportError: If the module cannot be imported
    """
    if not setup_dspy_imports():
        raise ImportError("Failed to setup DSPy import paths")

    try:
        if from_package:
            module_path = f"{from_package}.{module_name}"
        else:
            module_path = module_name

        return __import__(module_path, fromlist=[module_name])
    except ImportError as e:
        raise ImportError(f"Failed to import {module_path}: {e}")


def get_hybrid_vector_store():
    """
    Get HybridVectorStore class with workaround for relative import issues.

    Returns:
        HybridVectorStore class or None if import fails
    """
    try:
        # Try direct import first
        import sys

        sys.path.insert(0, "src")
        from dspy_modules.vector_store import HybridVectorStore

        return HybridVectorStore
    except Exception as e:
        print(f"Warning: Could not import HybridVectorStore directly: {e}")
        return None


def get_common_imports() -> dict:
    """
    Get commonly used imports for DSPy RAG system scripts.

    Returns:
        dict: Dictionary of imported modules
    """
    if not setup_dspy_imports():
        raise ImportError("Failed to setup DSPy import paths")

    imports = {}

    try:
        from utils.anchor_metadata_parser import extract_anchor_metadata, extract_anchor_metadata_from_file

        imports.update(
            {
                "extract_anchor_metadata": extract_anchor_metadata,
                "extract_anchor_metadata_from_file": extract_anchor_metadata_from_file,
            }
        )
    except ImportError as e:
        print(f"Warning: Could not import anchor_metadata_parser: {e}")

    try:
        from utils.database_resilience import get_database_manager

        imports["get_database_manager"] = get_database_manager
    except ImportError as e:
        print(f"Warning: Could not import database_resilience: {e}")

    try:
        from utils.logger import get_logger, setup_logger

        imports.update({"setup_logger": setup_logger, "get_logger": get_logger})
    except ImportError as e:
        print(f"Warning: Could not import logger: {e}")

    # Add DSPy modules
    try:
        from dspy_modules.document_processor import DocumentProcessor

        imports["DocumentProcessor"] = DocumentProcessor
    except ImportError as e:
        print(f"Warning: Could not import DocumentProcessor: {e}")

    # Add HybridVectorStore with workaround
    HybridVectorStore = get_hybrid_vector_store()
    if HybridVectorStore:
        imports["HybridVectorStore"] = HybridVectorStore
        # Note: VectorStore is deprecated, use HybridVectorStore instead

    return imports


def validate_imports() -> List[str]:
    """
    Validate that all required imports are available.

    Returns:
        List[str]: List of missing imports
    """
    missing = []

    required_modules = [
        "utils.anchor_metadata_parser",
        "utils.database_resilience",
        "utils.logger",
        "dspy_modules.document_processor",
        # Note: dspy_modules.vector_store has relative import issues
        # but HybridVectorStore can be imported via get_common_imports()
    ]

    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)

    return missing


if __name__ == "__main__":
    # Test the import setup
    print("🧪 Testing DSPy RAG System Import Setup")

    if setup_dspy_imports():
        print("✅ Import paths setup successful")

        missing = validate_imports()
        if missing:
            print(f"❌ Missing imports: {missing}")
        else:
            print("✅ All required imports available")

            # Test common imports
            try:
                imports = get_common_imports()
                print(f"✅ Common imports loaded: {list(imports.keys())}")
            except Exception as e:
                print(f"❌ Error loading common imports: {e}")
    else:
        print("❌ Import paths setup failed")
        sys.exit(1)
