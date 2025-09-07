import os
import sys

# Add project src path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from _bootstrap import ROOT, SRC  # type: ignore  # noqa: F401
sys.path.insert(0, str(SRC))

from common.case_id import canonical_case_id


def test_stable():
    a = canonical_case_id(
        "What is DSPy?",
        "400_guides/400_07_ai-frameworks-dspy.md",
    )
    b = canonical_case_id(
        " What is  DSPy? ",
        "./400_guides/../400_guides/400_07_ai-frameworks-dspy.md",
    )
    assert a == b


def test_variant_changes_id():
    a = canonical_case_id("Q", "p.md", variant=None)
    b = canonical_case_id("Q", "p.md", variant="v2")
    assert a != b
