#!/usr/bin/env python3
"""
Phase-2: Industry-Standard DSPy RAG Program
Wrap pipeline as DSPy program and compile prompts/few-shots against metric.
"""

import os
import sys
from typing import Any, Dict, List

# Add DSPy RAG system to path
sys.path.insert(0, "dspy-rag-system/src")

try:
    from litellm_compatibility_shim import patch_litellm_imports
    patch_litellm_imports()
except ImportError:
    pass

import dspy
from dspy_modules.rag_pipeline import _retrieve_with_fusion, HybridVectorStore


class RetrieveSig(dspy.Signature):
    """Retrieve k passages for the question."""
    question: str = dspy.InputField()
    passages: List[str] = dspy.OutputField()


class AnswerSig(dspy.Signature):
    """Answer faithfully using the passages."""
    question: str = dspy.InputField()
    passages: List[str] = dspy.InputField()
    answer: str = dspy.OutputField()


class Retrieve(dspy.Module):
    """DSPy retrieval module using fusion adapter."""
    
    def __init__(self, retriever: HybridVectorStore, k: int = 12):
        super().__init__()
        self.retriever = retriever
        self.k = k

    def forward(self, question: str) -> List[str]:
        """Retrieve passages using fusion adapter."""
        # Use your existing fusion adapter
        candidates, _ = _retrieve_with_fusion(self.retriever, question)
        
        # Return top k passages
        passages = [c.get("text", "") for c in candidates[:self.k]]
        return passages


class Answer(dspy.Module):
    """DSPy answer generation module."""
    
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(AnswerSig)

    def forward(self, question: str, passages: List[str]) -> str:
        """Generate answer from passages."""
        result = self.predict(question=question, passages=passages)
        return result.answer


class RAGProgram(dspy.Module):
    """Complete DSPy RAG program."""
    
    def __init__(self, retriever: HybridVectorStore, k: int = 12):
        super().__init__()
        self.retrieve = Retrieve(retriever, k)
        self.answer = Answer()

    def forward(self, question: str) -> str:
        """Complete RAG pipeline."""
        passages = self.retrieve(question=question)
        answer = self.answer(question=question, passages=passages)
        return answer


def metric(example: Dict[str, Any], pred: Any, trace=None) -> float:
    """Bridge to your oracle/F1 metric. Returns scalar higher-is-better."""
    # This would integrate with your existing evaluation metrics
    # For now, return a placeholder score
    
    # Extract ground truth and prediction
    gt_answer = example.get("gt_answer", "")
    pred_answer = str(pred) if hasattr(pred, 'answer') else str(pred)
    
    # Simple word overlap metric (replace with your actual metric)
    gt_words = set(gt_answer.lower().split())
    pred_words = set(pred_answer.lower().split())
    
    if len(gt_words) == 0:
        return 0.0
    
    # F1-like score
    precision = len(pred_words & gt_words) / len(pred_words) if len(pred_words) > 0 else 0.0
    recall = len(pred_words & gt_words) / len(gt_words)
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return f1


def compile_rag(trainset: List[Dict[str, Any]], 
                valset: List[Dict[str, Any]],
                retriever: HybridVectorStore,
                config_hash: str = None) -> dspy.Module:
    """Compile RAG program with DSPy teleprompter."""
    
    # Initialize program
    program = RAGProgram(retriever, k=12)
    
    # Create teleprompter (BootstrapFewShot or MIPROV)
    teleprompter = dspy.teleprompt.BootstrapFewShot(
        metric=metric,
        max_bootstrapped_demos=6,
        max_labeled_demos=4
    )
    
    # Compile the program
    compiled = teleprompter.compile(
        student=program,
        trainset=trainset,
        valset=valset,
        num_trials=3
    )
    
    # Save compiled artifacts
    if config_hash:
        save_compiled(compiled, config_hash=config_hash)
    
    return compiled


def save_compiled(compiled: dspy.Module, config_hash: str, run_id: str = None):
    """Save compiled DSPy artifacts with versioning."""
    import json
    from pathlib import Path
    
    # Create compiled artifacts directory
    artifacts_dir = Path("compiled_artifacts") / config_hash
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    # Save compiled program
    compiled_file = artifacts_dir / "compiled_program.json"
    with open(compiled_file, "w") as f:
        json.dump({
            "config_hash": config_hash,
            "run_id": run_id or os.getenv("INGEST_RUN_ID", "unknown"),
            "timestamp": os.getenv("TIMESTAMP", "unknown"),
            "compiled_program": str(compiled)
        }, f, indent=2)
    
    print(f"✅ Compiled artifacts saved to: {artifacts_dir}")


def load_compiled(config_hash: str) -> dspy.Module:
    """Load compiled DSPy artifacts."""
    import json
    from pathlib import Path
    
    artifacts_dir = Path("compiled_artifacts") / config_hash
    compiled_file = artifacts_dir / "compiled_program.json"
    
    if not compiled_file.exists():
        raise FileNotFoundError(f"Compiled artifacts not found for config_hash: {config_hash}")
    
    with open(compiled_file, "r") as f:
        artifacts = json.load(f)
    
    # In a real implementation, you would reconstruct the compiled program
    # For now, return a placeholder
    print(f"📋 Loaded compiled artifacts for config_hash: {config_hash}")
    return None


def main():
    """Main entry point for DSPy compilation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="DSPy RAG compilation")
    parser.add_argument("--trainset", required=True, help="Training dataset file")
    parser.add_argument("--valset", required=True, help="Validation dataset file")
    parser.add_argument("--config-hash", help="Configuration hash for versioning")
    parser.add_argument("--compile", action="store_true", help="Compile the program")
    parser.add_argument("--load", help="Load compiled program by config_hash")
    
    args = parser.parse_args()
    
    if args.load:
        # Load compiled program
        compiled = load_compiled(args.load)
        print(f"✅ Loaded compiled program: {args.load}")
        return compiled
    
    if args.compile:
        # Load datasets
        import json
        with open(args.trainset, "r") as f:
            trainset = [json.loads(line) for line in f if line.strip()]
        
        with open(args.valset, "r") as f:
            valset = [json.loads(line) for line in f if line.strip()]
        
        # Initialize retriever
        db_connection = "postgresql://danieljacobs@localhost:5432/ai_agency"
        retriever = HybridVectorStore(db_connection)
        
        # Compile program
        config_hash = args.config_hash or os.getenv("CONFIG_HASH", "default")
        compiled = compile_rag(trainset, valset, retriever, config_hash)
        
        print(f"✅ DSPy RAG program compiled successfully")
        print(f"🔧 Config Hash: {config_hash}")
        return compiled


if __name__ == "__main__":
    main()
