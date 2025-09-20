from __future__ import annotations
import sys
from pathlib import Path
from ragchecker_pipeline_governance import RAGCheckerPipelineGovernance
import os
#!/usr/bin/env python3
"""
Simple test of RAG Pipeline Governance system
"""

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

def test_governance():
    """Test the governance system with a simple configuration"""

    # Initialize governance
    governance = RAGCheckerPipelineGovernance()

    # Test with a complete pipeline configuration
    test_config = {
        "ingest": {"parameters": {"batch_size": 100, "encoding": "utf-8"}},
        "chunk": {"parameters": {"chunk_size": 512, "overlap": 50}},
        "retrieve": {"parameters": {"top_k": 5, "similarity_threshold": 0.7}},
        "rerank": {"parameters": {"rerank_top_k": 3, "model": "cross-encoder"}},
        "generate": {"parameters": {"temperature": 0.7, "max_tokens": 1000}},
        "validate": {"parameters": {"min_length": 10, "max_length": 5000}},
    }

    print("🔍 Testing pipeline validation...")
    validation = governance.validate_ragchecker_pipeline(test_config)
    print(f"Validation result: {validation}")

    print("\n🔧 Testing pipeline optimization...")
    optimized = governance.optimize_ragchecker_pipeline(test_config)
    print(f"Optimization successful: {optimized is not None}")

    print("\n🧪 Testing pipeline evaluation...")
    test_queries = ["What is the current project status?", "How do I create a PRD?"]
    evaluation = governance.evaluate_pipeline_performance(test_config, test_queries)
    print(f"Evaluation successful: {'error' not in evaluation}")

    if "error" not in evaluation:
        print(f"Average metrics: {result
        print(f"Success rate: {result

    print("\n📊 Testing governance report...")
    report = governance.export_governance_report()
    print(f"Total pipelines managed: {result
    print(f"Known good patterns: {result

    print("\n✅ Governance system test completed!")

if __name__ == "__main__":
    test_governance()
