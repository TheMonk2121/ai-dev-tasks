import sys
import time
from pathlib import Path
from typing import cast

# Add the dspy-rag-system src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from dspy_modules.retriever.feature_schema import FusionFeatures


def test_fast_enough():
    n = 2000
    t0 = time.time()

    # Create test data with explicit types
    s_bm25: float = 0.3
    s_vec: float = 0.5
    s_title: float = 0.1
    s_short: float = 0.2
    r_bm25: float = 0.1
    r_vec: float = 0.2
    len_norm: float = 0.9
    q_vec: list[float] = [0.0] * 384
    d_vec: list[float] = [0.1] * 384

    # Create objects in a loop to avoid list comprehension type inference issues
    results = []
    for _ in range(n):
        obj = FusionFeatures(
            s_bm25=s_bm25,
            s_vec=s_vec,
            s_title=s_title,
            s_short=s_short,
            r_bm25=r_bm25,
            r_vec=r_vec,
            len_norm=len_norm,
            q_vec=q_vec,
            d_vec=d_vec,
        )
        results.append(obj)

    dt = time.time() - t0
    # loose guard to catch accidental O(n^2) regressions
    assert dt < 3.0
