import os
import re
from typing import Any

import dspy

# Optional observability for structured error reporting
try:
    from scripts.observability import get_logfire  # type: ignore

    logfire = get_logfire()
except Exception:  # pragma: no cover - best-effort only
    logfire = None

from .signatures import ExtractSpan

OPS_TAGS = {"meta_ops", "ops_health"}


def _normalize(ans: str, tag: str) -> str:
    normalized: Any = ans.strip()
    if normalized.upper() == "NOT_ANSWERABLE":
        return "NOT_ANSWERABLE"
    # Tag-aware canonicalization helps F1 scoring without hallucination
    if tag in OPS_TAGS:
        normalized = normalized.replace("\\\\", "/")
        normalized = re.sub(r"\s+", " ", normalized)
        normalized = re.sub(r"^`|`$", "", normalized)
    return normalized


class ExtractiveReader(dspy.Module):
    def __init__(self, answerable_threshold: float = 0.12):
        super().__init__()
        # Force completion adapter to avoid ChatAdapter type check issues
        self.extract: Any = dspy.Predict(ExtractSpan)  # Default fallback

        try:
            # Try to import CompletionAdapter - may not be available in all DSPy versions
            import importlib

            adapters_module = importlib.import_module("dspy.adapters")
            CompletionAdapter = getattr(adapters_module, "CompletionAdapter", None)

            if CompletionAdapter is not None:
                # Ensure global DSPy is configured with completion adapter
                try:
                    dspy.configure(adapter=CompletionAdapter())
                except Exception:
                    pass  # May already be configured

                self.extract = dspy.Predict(ExtractSpan, adapter=CompletionAdapter())
        except Exception:
            pass  # Keep default fallback
        self.answerable_threshold: Any = answerable_threshold

    def forward(self, question: str, passages: list[str], tag: str = "") -> Any:
        # Keep context surgical: 4–6 most relevant sentences + visible path/title
        joined = "\n".join(passages[:6])
        try:
            pred: Any = self.extract(question=question, context=joined)
        except Exception as e:  # Defensive: keep evaluation running even if adapter path throws
            if logfire is not None:
                try:
                    logfire.warning("reader.predict.error", error=str(e), tag=tag, qlen=len(question), clen=len(joined))
                except Exception:
                    pass
            # Minimal safe fallback
            return {"answer": "NOT_ANSWERABLE"}
        # Calibrated "not answerable" gate via heuristic confidence hook if available
        ans = pred.answer or ""
        ans = _normalize(ans, tag)
        # Optional: if your scorer exposes confidence, gate it here.
        # For now, simple policy: if no overlap with context tokens, declare NOT_ANSWERABLE
        if ans and ans != "NOT_ANSWERABLE":
            # More lenient check: look for key terms from the answer in the context
            ans_words = set(re.findall(r"[A-Za-z0-9_/.-]+", ans.lower()))
            context_words = set(re.findall(r"[A-Za-z0-9_/.-]+", joined.lower()))
            overlap_ratio = (len(ans_words.intersection(context_words)) / len(ans_words)) if ans_words else 0.0
            try:
                min_overlap = float(os.getenv("READER_MIN_OVERLAP_RATIO", "0.3"))
            except ValueError:
                min_overlap = 0.3
            if overlap_ratio < max(0.0, min_overlap):
                ans = "NOT_ANSWERABLE"
        return {"answer": ans}
