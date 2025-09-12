from __future__ import annotations

import dspy


class ExtractSpan(dspy.Signature):
    """Return the shortest exact span from context that answers the question.
    If no span exists, return exactly 'Not in context.'."""

    question: str = dspy.InputField()
    context: str = dspy.InputField()
    answer: str = dspy.OutputField()