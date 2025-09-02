"""
Heuristic Reranker (Lightweight, Dependency-Free)

Reorders fused candidates using simple, robust signals:
- Query term overlap ratio
- Exact phrase presence bonus
- Code-block presence bonus for technical queries

final_score = alpha * rerank_score + (1 - alpha) * normalized_fused_score
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

DocId = str
Score = float
Document = str


def _normalize_scores(candidates: List[Tuple[DocId, Score]]) -> Dict[DocId, float]:
    if not candidates:
        return {}
    scores = [s for _id, s in candidates]
    s_min, s_max = min(scores), max(scores)
    if s_max <= s_min:
        return {doc_id: 0.5 for doc_id, _ in candidates}
    return {doc_id: (score - s_min) / (s_max - s_min) for doc_id, score in candidates}


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9_]+", text.lower())


def _is_technical_query(query: str) -> bool:
    tech_markers = ["def ", "class ", "import ", "SELECT ", "INSERT ", "{", "}", "`", "::", "->"]
    q = query
    return any(m in q or m.lower() in q.lower() for m in tech_markers)


def _score_rerank(query: str, doc_text: str) -> float:
    if not doc_text:
        return 0.0
    q_tokens = _tokenize(query)
    if not q_tokens:
        return 0.0
    d_tokens = set(_tokenize(doc_text))

    # Term overlap ratio
    overlap = sum(1 for t in q_tokens if t in d_tokens) / max(len(q_tokens), 1)

    # Exact phrase presence
    phrase_bonus = 0.2 if query.strip().lower() in doc_text.lower() else 0.0

    # Code block or code-ish content
    code_like = ("```" in doc_text) or ("`" in doc_text) or ("def " in doc_text) or ("class " in doc_text)
    code_bonus = 0.1 if code_like and _is_technical_query(query) else 0.0

    return overlap + phrase_bonus + code_bonus


def heuristic_rerank(
    query: str,
    candidates: List[Tuple[DocId, Score]],
    documents: Dict[DocId, Document],
    *,
    alpha: float = 0.7,
    top_m: Optional[int] = None,
) -> List[Tuple[DocId, Score]]:
    """Rerank fused candidates with simple heuristics.

    Args:
        query: user question
        candidates: list of (doc_id, fused_score)
        documents: doc_id -> document text
        alpha: weight of rerank score vs fused score
        top_m: optional cap on returned results
    """
    alpha = max(0.0, min(1.0, alpha))

    norm = _normalize_scores(candidates)
    scored: List[Tuple[DocId, Score]] = []
    for doc_id, fused_score in candidates:
        doc_text = documents.get(doc_id, "")
        rerank_score = _score_rerank(query, doc_text)
        final = alpha * rerank_score + (1.0 - alpha) * norm.get(doc_id, 0.5)
        scored.append((doc_id, final))

    scored.sort(key=lambda kv: kv[1], reverse=True)
    if top_m is not None and top_m >= 0:
        scored = scored[:top_m]
    return scored
