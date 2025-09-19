from __future__ import annotations

import json
import os
from typing import Any

import numpy as np
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic_core import CoreSchema, core_schema
from pydantic_core.core_schema import no_info_plain_validator_function

#!/usr/bin/env python3
"""
Pydantic-compatible numpy array types with shape validation.
"""


class ArrayF32WithShape:
    """
    A Pydantic type for numpy arrays with specific shape constraints.

    Usage:
        Vector384 = ArrayF32WithShape(384)  # 1D array with 384 elements
        Vector2D = ArrayF32WithShape((10, 20))  # 2D array with shape (10, 20)
    """

    def __init__(self, shape: int | tuple[int, ...]) -> None:
        self.shape: tuple[int, ...] = shape if isinstance(shape, tuple) else (shape,)

    def __get_pydantic_core_schema__(self, source_type: type, handler: GetCoreSchemaHandler) -> CoreSchema:
        def validate_array(value: object) -> np.ndarray:
            if not isinstance(value, np.ndarray):
                raise ValueError("Expected numpy array")

            if value.dtype != np.float32:
                # Convert to float32 if possible
                try:
                    value: Any = value.astype(np.float32)
                except (ValueError, TypeError) as e:
                    raise ValueError(f"Cannot convert to float32: {e}")

            if value.shape != self.shape:
                raise ValueError(f"Expected shape {self.shape}, got {value.shape}")

            return value

        return core_schema.no_info_plain_validator_function(
            validate_array,
            serialization=core_schema.wrap_serializer_function_ser_schema(
                lambda x, handler: x.tolist() if isinstance(x, np.ndarray) else x
            ),
        )

    def __get_pydantic_json_schema__(self, core_schema: CoreSchema, handler: GetJsonSchemaHandler) -> dict:
        return {
            "type": "array",
            "items": {"type": "number"},
            "minItems": np.prod(self.shape),
            "maxItems": np.prod(self.shape),
        }


# Convenience aliases for common embedding dimensions
Vector384 = ArrayF32WithShape(384)  # all-MiniLM-L6-v2
Vector768 = ArrayF32WithShape(768)  # all-mpnet-base-v2, all-distilroberta-v1
Vector1024 = ArrayF32WithShape(1024)  # intfloat/e5-large-v2
Vector1536 = ArrayF32WithShape(1536)  # text-embedding-ada-002
