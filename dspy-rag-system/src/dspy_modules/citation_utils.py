#!/usr/bin/env python3
"""
Citation Utilities for Enhanced RAG Scoring
==========================================

Based on ChatGPT's analysis, this module provides advanced citation scoring
with answer/question overlap, anchor cues, and better evaluation metrics.
"""

import re
from difflib import SequenceMatcher
from typing import Dict, List, Set

WORD_RE = re.compile(r"[A-Za-z0-9_]+")
FILE_TOKEN_RE = re.compile(r"\b\d{3}_[A-Za-z0-9-]+(?:\.md)?\b")


def _tokens(s: str) -> Set[str]:
    """Extract tokens from string."""
    return set(w.lower() for w in WORD_RE.findall(s or ""))


def _fuzzy(a: str, b: str) -> float:
    """Compute fuzzy similarity between strings (0..1)."""
    return SequenceMatcher(None, (a or "").lower(), (b or "").lower()).ratio()


def getattr_or_get(hit, key: str, default=None):
    """Works for dict hits OR object hits."""
    if isinstance(hit, dict):
        return hit.get(key, default)
    return getattr(hit, key, default)


def canon_filename(s: str) -> str:
    """Canonicalize filename for comparison."""
    s = (s or "").strip().lower()
    # strip dirs
    s = s.split("/")[-1]
    # ensure .md suffix is comparable
    if s and not s.endswith(".md"):
        s += ".md"
    return s


def derive_expected_from_question(question: str, alias_map=None, filename_to_docid=None):
    """Return (expected_docids:set, expected_names:set)."""
    alias_map = alias_map or {}
    names = set(m.group(0) for m in FILE_TOKEN_RE.finditer(question or ""))

    # Alias expansion (e.g., "cursor memory context" -> 100_cursor-memory-context.md)
    for phrase, fname in alias_map.items():
        if phrase.lower() in (question or "").lower():
            names.add(fname)

    names = {canon_filename(n) for n in names}
    docids = set()
    if filename_to_docid:
        for n in names:
            did = filename_to_docid.get(n)
            if did:
                docids.add(did)

    return docids, names


def anchor_terms_for_question(question: str) -> Set[str]:
    """Lightweight anchors: customize per repo flavor."""
    q = (question or "").lower()
    anchors = set()

    if "role" in q:
        anchors |= {"planner", "implementer", "researcher", "coder"}

    if "context_index" in q:
        anchors |= {
            "context_index",
            "entry",
            "priorities",
            "roadmap",
            "getting",
            "architecture",
            "navigation",
            "ai-safe",
        }

    if "memory" in q and "rehydration" in q:
        anchors |= {"memory", "context", "rehydration", "hydration", "ltst"}

    if "dspy" in q:
        anchors |= {"dspy", "framework", "integration", "optimization", "monitoring"}

    if "workflow" in q or "core" in q:
        anchors |= {"workflow", "core", "create-prd", "generate-tasks", "process-task-list"}

    return anchors


def score_hit(
    hit, question: str, answer: str, expected_docids: Set, expected_names: Set, weights: Dict[str, float]
) -> float:
    """Score a hit based on multiple criteria."""
    # Pull fields defensively
    filename = canon_filename(str(getattr_or_get(hit, "filename", "")))
    file_path = str(getattr_or_get(hit, "file_path", "") or "")
    content = str(getattr_or_get(hit, "content", "") or "")
    base = float(getattr_or_get(hit, "score", 0.0) or 0.0)

    qtok = _tokens(question)
    atok = _tokens(answer)
    ctok = _tokens(content)

    # Overlaps
    ov_q = len(qtok & ctok) / (len(qtok) + 1e-6)
    ov_a = len(atok & ctok) / (len(atok) + 1e-6)

    # Expected doc bonus
    is_expected = getattr_or_get(hit, "document_id", None) in expected_docids

    # Fuzzy filename bonus if docid mapping unknown
    fuzzy_bonus = 0.0
    for n in expected_names:
        fuzzy_bonus = max(fuzzy_bonus, _fuzzy(filename, canon_filename(n)))

    # Anchor cue boost
    anchors = anchor_terms_for_question(question)
    anchor_hits = sum(1 for a in anchors if a in ctok)
    anchor_boost = anchor_hits / max(1, len(anchors)) if anchors else 0.0

    # Combine
    score = (
        weights["base"] * base
        + weights["expect"] * (1.0 if is_expected else 0.0)
        + weights["fuzzy"] * fuzzy_bonus
        + weights["ov_q"] * ov_q
        + weights["ov_a"] * ov_a
        + weights["anchor"] * anchor_boost
    )
    return score


def select_citations(hits: List, question: str, answer: str, filename_to_docid=None, max_cites: int = 3) -> List:
    """Select citations using advanced scoring."""
    # 1) expected set
    expected_docids, expected_names = derive_expected_from_question(
        question, alias_map={}, filename_to_docid=filename_to_docid
    )

    # 2) score all candidates
    W = dict(base=1.0, expect=2.0, fuzzy=1.0, ov_q=1.0, ov_a=1.0, anchor=1.0)
    scored = []
    for h in hits:
        s = score_hit(h, question, answer, expected_docids, expected_names, W)
        scored.append((s, h))

    scored.sort(key=lambda x: x[0], reverse=True)

    # 3) doc-diversity: pick best unique docs
    picked, seen_docs = [], set()
    for s, h in scored:
        did = getattr_or_get(h, "document_id", None)
        if did in seen_docs:
            continue
        picked.append(h)
        seen_docs.add(did)
        if len(picked) >= max_cites:
            break

    # 4) fail-safe: ensure at least one expected doc if any were named
    if expected_docids and not any(getattr_or_get(h, "document_id", None) in expected_docids for h in picked):
        # find the best expected in pool and replace the weakest pick
        expected_pool = [(s, h) for (s, h) in scored if getattr_or_get(h, "document_id", None) in expected_docids]
        if expected_pool:
            best_expected = expected_pool[0][1]
            if picked:
                picked[-1] = best_expected
            else:
                picked = [best_expected]

    return picked


def evaluate_citation_quality(citations: List[str], question: str, expected_citations: List[str]) -> Dict[str, float]:
    """Evaluate citation quality with detailed metrics."""
    if not citations:
        return {"explicit_file_recall": 0.0, "anchor_coverage": 0.0, "diversity_ok": 1.0, "overall_score": 0.0}

    # Explicit file recall
    expected_files = {canon_filename(c) for c in expected_citations}
    cited_files = {canon_filename(c) for c in citations}
    explicit_file_recall = len(expected_files & cited_files) / len(expected_files) if expected_files else 1.0

    # Anchor coverage
    anchors = anchor_terms_for_question(question)
    anchor_coverage = 0.0  # Would need content analysis for full implementation

    # Diversity (no duplicates)
    unique_citations = len(set(citations))
    diversity_ok = unique_citations / len(citations) if citations else 1.0

    # Overall score
    overall_score = explicit_file_recall * 0.5 + anchor_coverage * 0.3 + diversity_ok * 0.2

    return {
        "explicit_file_recall": explicit_file_recall,
        "anchor_coverage": anchor_coverage,
        "diversity_ok": diversity_ok,
        "overall_score": overall_score,
    }
