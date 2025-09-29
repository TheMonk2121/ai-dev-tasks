from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from utils.pyd_ndarray import ArrayF32WithShape

# Common embedding dimension aliases for your project
Vector384 = ArrayF32WithShape(384)  # all-MiniLM-L6-v2 (your default)
Vector768 = ArrayF32WithShape(768)  # all-mpnet-base-v2, all-distilroberta-v1
Vector1024 = ArrayF32WithShape(1024)  # intfloat/e5-large-v2
Vector1536 = ArrayF32WithShape(1536)  # text-embedding-ada-002


class FusionFeatures(BaseModel):
    """
    Canonical feature row for retrieval fusion & training.
    Arrays are strongly typed and JSON-serializable.
    """

    model_config: ConfigDict = ConfigDict(strict=True, extra="forbid", arbitrary_types_allowed=True)

    # scalar signals
    s_bm25: float
    s_vec: float
    s_title: float
    s_short: float
    r_bm25: float
    r_vec: float
    len_norm: float
    is_code: bool = False
    tag_bias_hint: float = 0.0

    # optional dense vectors (if you persist them in features)
    # enforce known dims when you know them, else use ArrayF32
    q_vec: ArrayF32WithShape | None = None
    d_vec: ArrayF32WithShape | None = None
