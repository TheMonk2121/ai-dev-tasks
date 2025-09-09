import sys
import time
from pathlib import Path

# Add the dspy-rag-system src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "dspy-rag-system" / "src"))

from dspy_modules.retriever.feature_schema import FusionFeatures


def test_fast_enough():
    n = 2000
    rows = [
        dict(
            s_bm25=0.3,
            s_vec=0.5,
            s_title=0.1,
            s_short=0.2,
            r_bm25=0.1,
            r_vec=0.2,
            len_norm=0.9,
            q_vec=[0.0] * 384,
            d_vec=[0.1] * 384,
        )
        for _ in range(n)
    ]
    t0 = time.time()
    _ = [FusionFeatures(**r) for r in rows]
    dt = time.time() - t0
    # loose guard to catch accidental O(n^2) regressions
    assert dt < 3.0
