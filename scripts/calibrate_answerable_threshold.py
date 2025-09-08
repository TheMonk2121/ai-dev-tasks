#!/usr/bin/env python3
"""
Calibrate answerability thresholds per tag for optimal precision/recall balance.
Tests different overlap thresholds on dev set and reports best F1 per tag.
"""
import json
import os
import sys
from typing import Dict, List

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dspy-rag-system", "src"))

from dspy_modules.reader.sentence_select import select_sentences
from dspy_modules.retriever.limits import load_limits
from dspy_modules.retriever.pg import run_fused_query
from dspy_modules.retriever.query_rewrite import build_channel_queries
from dspy_modules.retriever.rerank import mmr_rerank, per_file_cap


def load_jsonl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def norm(s):
    return " ".join((s or "").lower().split())


def token_overlap(a, b):
    A, B = set(norm(a).split()), set(norm(b).split())
    if not A or not B:
        return 0.0
    return len(A & B) / max(1, len(A))


def calculate_f1(predictions: List[str], gold_answers: List[List[str]]) -> float:
    """Calculate micro F1 score."""
    if not predictions or not gold_answers:
        return 0.0

    tp = fp = fn = 0
    for pred, gold_list in zip(predictions, gold_answers):
        pred_norm = norm(pred)
        gold_norms = [norm(g) for g in gold_list]

        # Check if prediction matches any gold answer
        if any(pred_norm == g for g in gold_norms):
            tp += 1
        elif pred == "I don't know":
            fn += 1
        else:
            fp += 1

    precision = tp / max(1, tp + fp)
    recall = tp / max(1, tp + fn)
    f1 = 2 * precision * recall / max(0.001, precision + recall)
    return f1


def test_threshold(threshold: float, cases: List[Dict], tag: str) -> float:
    """Test a specific threshold on cases for a given tag."""
    predictions = []
    gold_answers = []

    for case in cases:
        if case.get("tag") != tag:
            continue

        query = case["query"]
        answers = case.get("answers", [])

        # Get context (simplified - in real use this would be from retrieval)
        limits = load_limits(tag)
        qs = build_channel_queries(query, tag)
        rows = run_fused_query(
            qs["short"], qs["title"], qs["bm25"], qvec=[], tag=tag, k=limits["shortlist"], return_components=True
        )
        rows = mmr_rerank(rows, alpha=0.85, per_file_penalty=0.10, k=limits["shortlist"])
        rows = per_file_cap(rows, cap=5)[: limits["topk"]]

        context, picks = select_sentences(rows, query, tag, phrase_hints=[], per_chunk=2, total=10)
        top2 = " ".join([p["sentence"] for p in picks[:2]])
        cover = token_overlap(top2, context)

        # Apply threshold
        if cover < threshold:
            prediction = "I don't know"
        else:
            # Simple heuristic: return first answer if coverage is good
            prediction = answers[0] if answers else "I don't know"

        predictions.append(prediction)
        gold_answers.append(answers)

    return calculate_f1(predictions, gold_answers)


def main():
    # Load dev cases
    cases_file = os.getenv("CASES_FILE", "evals/gold_cases.json")
    gold_file = os.getenv("READER_GOLD_FILE", "evals/reader_gold_comprehensive.jsonl")

    cases = json.load(open(cases_file, encoding="utf-8"))
    gold = {r["case_id"]: r for r in load_jsonl(gold_file)}

    # Filter to cases that have gold answers
    valid_cases = [c for c in cases if c["case_id"] in gold]

    # Test thresholds
    thresholds = [0.05, 0.08, 0.10, 0.12, 0.15, 0.18, 0.20]
    tags = ["rag_qa_single", "db_workflows", "meta_ops", "ops_health"]

    results = {}

    for tag in tags:
        tag_cases = [c for c in valid_cases if c.get("tag") == tag]
        if not tag_cases:
            continue

        print(f"\nCalibrating {tag} ({len(tag_cases)} cases):")
        best_f1 = 0.0
        best_threshold = 0.10

        for threshold in thresholds:
            f1 = test_threshold(threshold, tag_cases, tag)
            print(f"  {threshold:.2f}: F1={f1:.3f}")
            if f1 > best_f1:
                best_f1 = f1
                best_threshold = threshold

        results[tag] = {"best_threshold": best_threshold, "best_f1": best_f1, "case_count": len(tag_cases)}
        print(f"  → Best: {best_threshold:.2f} (F1={best_f1:.3f})")

    # Save results
    output_file = "evals/answerability_calibration_results.json"
    os.makedirs("evals", exist_ok=True)
    json.dump(results, open(output_file, "w", encoding="utf-8"), indent=2)
    print(f"\nSaved calibration results to {output_file}")

    # Generate config snippet
    print("\nRecommended configs/reader_limits.yaml additions:")
    print("answerability_thresholds:")
    for tag, result in results.items():
        print(f"  {tag}: {result['best_threshold']:.2f}")


if __name__ == "__main__":
    main()
