from __future__ import annotations

import os
from typing import Annotated

import numpy as np
from numpy.typing import NDArray
from pydantic import AfterValidator, BeforeValidator

# Env-controlled strictness (CI vs dev)
STRICT = os.getenv("EVAL_STRICT_ARRAYS", "1") == "1"


def _to_array(v, dtype=np.float32):
    if isinstance(v, np.ndarray):
        return v.astype(dtype, copy=False)
    # accept lists/tuples; cast once
    return np.asarray(v, dtype=dtype)


def _check_finite(a: NDArray[np.floating]) -> NDArray[np.floating]:
    if STRICT and (not np.isfinite(a).all()):
        raise ValueError("array contains non-finite values")
    return a


def _check_shape(expected: tuple[int, ...] | None = None):
    def _validate(a: NDArray[np.floating]) -> NDArray[np.floating]:
        if expected and a.shape != expected:
            raise ValueError(f"expected shape {expected}, got {a.shape}")
        return a

    return _validate


# Reusable annotated aliases
ArrayF32 = Annotated[
    NDArray[np.float32],
    BeforeValidator(_to_array),
    AfterValidator(_check_finite),
]


def ArrayF32WithShape(*shape: int):
    return Annotated[
        NDArray[np.float32],
        BeforeValidator(_to_array),
        AfterValidator(_check_finite),
        AfterValidator(_check_shape(shape if shape else None)),
    ]


# Example usage pattern for models with array fields:
# class MyModel(BaseModel):
#     model_config = ConfigDict(strict=True, extra="forbid", ser_json_inf_nan=False)
#     vector: ArrayF32
#
#     @field_serializer("vector", when_used="json")
#     def _ser_vector(self, v: np.ndarray):
#         return v.tolist()
