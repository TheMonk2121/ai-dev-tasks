import re

import dspy

# Optional observability for structured error reporting
try:
    from scripts.observability import get_logfire  # type: ignore

    _LOGFIRE = get_logfire()
except Exception:  # pragma: no cover - best-effort only
    _LOGFIRE = None

from .signatures import ExtractSpan

OPS_TAGS = {"meta_ops", "ops_health"}


def _normalize(ans: str, tag: str) -> str:
    a = ans.strip()
    if a.upper() == "NOT_ANSWERABLE":
        return "NOT_ANSWERABLE"
    # Tag-aware canonicalization helps F1 scoring without hallucination
    if tag in OPS_TAGS:
        a = a.replace("\\\\", "/")
        a = re.sub(r"\s+", " ", a)
        a = re.sub(r"^`|`$", "", a)
    return a


class ExtractiveReader(dspy.Module):
    def __init__(self, answerable_threshold: float = 0.12):
        super().__init__()
        # Force completion adapter to avoid ChatAdapter type check issues
        try:
            from dspy.adapters import CompletionAdapter

            # Ensure global DSPy is configured with completion adapter
            try:
                dspy.configure(adapter=CompletionAdapter())
            except Exception:
                pass  # May already be configured

            self.extract = dspy.Predict(ExtractSpan, adapter=CompletionAdapter())
        except Exception:
            # Fallback to default if adapter not available
            self.extract = dspy.Predict(ExtractSpan)
        self.answerable_threshold = answerable_threshold

    def forward(self, question: str, passages: list[str], tag: str = "general"):
        # Keep context surgical: 4–6 most relevant sentences + visible path/title
        joined = "\n".join(passages[:6])
        try:
            pred = self.extract(question=question, context=joined)
        except Exception as e:  # Defensive: keep evaluation running even if adapter path throws
            if _LOGFIRE is not None:
                try:
                    _LOGFIRE.warning(
                        "reader.predict.error", error=str(e), tag=tag, qlen=len(question), clen=len(joined)
                    )
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
            # If at least 50% of answer words are in context, accept it
            if len(ans_words) > 0 and len(ans_words.intersection(context_words)) / len(ans_words) < 0.5:
                ans = "NOT_ANSWERABLE"
        return {"answer": ans}
