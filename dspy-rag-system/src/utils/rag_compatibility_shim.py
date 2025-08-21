# src/utils/rag_compatibility_shim.py
import os
from typing import Any, Callable, Dict, List, Optional

# Primary retrieval path (dashboard expectation)
try:
    from dspy_modules.vector_store import HybridVectorStore  # type: ignore
except Exception:
    HybridVectorStore = None  # type: ignore

# Optional read-only fallback (requires an embed provider)
try:
    from dspy_modules.enhanced_vector_store import EnhancedVectorStore  # type: ignore
except Exception:
    EnhancedVectorStore = None  # type: ignore

FALLBACK_MODE = os.getenv("RAG_SHIM_FALLBACK", "none").lower()  # "none" | "enhanced"


class _RAGShim:
    def __init__(self, db_dsn: Optional[str], _legacy_url: Optional[str], model: Optional[str]):
        self.db_dsn = db_dsn
        self.model = model or "cursor-native-ai"
        self._hybrid = None
        self._enhanced = None
        self._embed_fn: Optional[Callable[[str], List[float]]] = None
        self._enhanced_dim = 384  # EnhancedVectorStore default dimension

        # Primary: HybridVectorStore (expected by dashboard)
        if HybridVectorStore and db_dsn:
            try:
                self._hybrid = HybridVectorStore(db_dsn)
                # Best-effort: discover an embedding provider for text → vector
                for cand in ("get_query_embedding", "embed", "_embed_query", "_embed"):
                    if hasattr(self._hybrid, cand):
                        fn = getattr(self._hybrid, cand)
                        if callable(fn):
                            self._embed_fn = lambda text, _fn=fn: list(_fn(text))  # type: ignore
                            break
            except Exception:
                self._hybrid = None

        # Optional: EnhancedVectorStore read-only, but only useful if we can embed
        if FALLBACK_MODE == "enhanced" and EnhancedVectorStore and db_dsn:
            try:
                self._enhanced = EnhancedVectorStore(db_dsn)  # requires query_embedding at inference time
                # If the store exposes a custom dimension, honor it
                if hasattr(self._enhanced, "dimension"):
                    self._enhanced_dim = int(getattr(self._enhanced, "dimension") or self._enhanced_dim)
            except Exception:
                self._enhanced = None

    def ask(self, question: str, use_cot: bool = False, use_react: bool = False) -> Dict[str, Any]:
        q = (question or "").strip()
        if not q:
            return {"status": "error", "error": "Empty question."}

        # PRIMARY: Use HybridVectorStore (dashboard contract)
        primary_ok, sources = self._primary_search(q)

        # FALLBACK: Enhanced store (read-only) — only if explicitly enabled AND we can embed
        degraded = not primary_ok
        if (not sources) and (FALLBACK_MODE == "enhanced") and self._enhanced and self._embed_fn:
            try:
                q_emb = self._embed_fn(q)
                # Ensure dimension matches Enhanced store expectation
                if len(q_emb) == self._enhanced_dim:
                    res = self._enhanced.similarity_search(query_embedding=q_emb, top_k=5, use_cache=True)  # type: ignore
                    sources = self._fmt(res)
                else:
                    sources = []
            except Exception:
                sources = []

        # Synthesis (minimal)
        if sources:
            answer = f'Synthesized from retrieved context for: "{q}"\n- ' + "\n- ".join(sources[:3])
        else:
            reason = "primary_unavailable" if degraded else "no_results"
            if FALLBACK_MODE == "enhanced" and self._enhanced and not self._embed_fn:
                reason = "no_embedder_for_enhanced"
            answer = f'No indexed context found for: "{q}". ' f"RAG shim returning minimal response (reason={reason})."

        return {
            "status": "success",
            "answer": answer,
            "sources": sources,
            "rewritten_query": q,
            "reasoning": "degraded" if degraded else "normal",
            "confidence": 0.6 if degraded else 0.7,
            "fast_path": len(q) < 50 and "code" not in q.lower(),
        }

    # --- helpers -------------------------------------------------------------
    def _primary_search(self, q: str):
        if not self._hybrid:
            return False, []

        # Try common shapes: hybrid_search(query=...), search(query=...), forward(operation="search", query=...)
        try_calls = [
            ("hybrid_search", {"query": q, "top_k": 5}),
            ("search", {"query": q, "top_k": 5}),
        ]

        for name, kwargs in try_calls:
            if hasattr(self._hybrid, name):
                try:
                    res = getattr(self._hybrid, name)(**kwargs)  # type: ignore
                    return True, self._fmt(res)
                except Exception:
                    break

        # DSPy-style Module.forward(operation="search", ...)
        if hasattr(self._hybrid, "forward"):
            try:
                res = self._hybrid.forward(operation="search", query=q, top_k=5)  # type: ignore
                return True, self._fmt(res)
            except Exception:
                pass

        return False, []

    def _fmt(self, res: Any) -> List[str]:
        out: List[str] = []
        if isinstance(res, dict):
            items = res.get("results") or res.get("chunks") or res.get("hits") or []
            return self._fmt(items)
        if isinstance(res, list):
            for r in res:
                if isinstance(r, dict):
                    txt = r.get("content") or r.get("text") or ""
                    doc = r.get("document_id") or r.get("id") or "unknown"
                    idx = r.get("chunk_index")
                    score = r.get("similarity_score") or r.get("score")
                    label = f"doc={doc}" + (f"#{idx}" if idx is not None else "")
                    meta = f" score={score:.3f}" if isinstance(score, (int, float)) else ""
                    out.append((label + meta + (f" | {txt[:160]}..." if txt else "")).strip())
                else:
                    out.append(str(r))
        return out[:5]


def create_rag_interface(
    db_dsn: Optional[str] = None, _legacy_url: Optional[str] = None, model: Optional[str] = None
) -> _RAGShim:
    return _RAGShim(db_dsn, _legacy_url, model)
