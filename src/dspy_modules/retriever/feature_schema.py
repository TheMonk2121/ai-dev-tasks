from __future__ import annotations

from typing import Union

import numpy as np
from pydantic import BaseModel, ConfigDict, field_serializer

from utils.pyd_ndarray import ArrayF32WithShape
import json
from typing import Any, Dict, List, Optional, Union

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

    model_config = ConfigDict(strict=True, extra="forbid", arbitrary_types_allowed=True)

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
    # Use numpy arrays here to avoid union issues with custom validator instances
    # (Vector384 is an instance of ArrayF32WithShape and does not support `| None`).
    q_vec: np.ndarray | None = None
    d_vec: np.ndarray | None = None

    @field_serializer("q_vec", when_used="json")
    def _ser_q_vec(self, v: np.ndarray | None) -> list[float] | None:
        return v.tolist() if v is not None else None

    @field_serializer("d_vec", when_used="json")
    def _ser_d_vec(self, v: np.ndarray | None) -> list[float] | None:
        return v.tolist() if v is not None else None
