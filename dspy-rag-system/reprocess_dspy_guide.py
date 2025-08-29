#!/usr/bin/env python3
"""
Re-process the DSPy guide specifically to fix the zero-chunk issue.
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from dspy_modules.document_processor import DocumentIngestionPipeline


def reprocess_dspy_guide():
    """Re-process the DSPy guide to ensure it has chunks."""

    print("=== RE-PROCESSING DSPY GUIDE ===")

    # Initialize the pipeline
    pipeline = DocumentIngestionPipeline()

    # Process the DSPy guide specifically
    file_path = "../400_guides/400_07_ai-frameworks-dspy.md"

    if os.path.exists(file_path):
        print(f"Processing: {file_path}")

        try:
            result = pipeline.forward(file_path)
            print(f"✅ Processing result: {result}")

            # Verify the result
            if result and result.get("status") == "success":
                print("✅ Successfully processed DSPy guide")
                print(f'   - Chunks created: {result.get("chunks_created", 0)}')
                print(f'   - Document ID: {result.get("document_id", "unknown")}')
            else:
                print(f"❌ Processing failed: {result}")

        except Exception as e:
            print(f"❌ Processing failed: {e}")
    else:
        print(f"❌ File not found: {file_path}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Looking for: {os.path.abspath(file_path)}")


if __name__ == "__main__":
    reprocess_dspy_guide()
