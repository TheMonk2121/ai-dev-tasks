from __future__ import annotations

import math
from typing import Any, Optional

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis.extra import numpy as hnp
from pydantic import BaseModel, ValidationError

from src.utils.pyd_ndarray import ArrayF32WithShape

from ._regression_capture import record_case

# Test array types
Vec8 = ArrayF32WithShape(8)
Vec384 = ArrayF32WithShape(384)
Vec2D = ArrayF32WithShape((10, 20))


class ArrayTestModel(BaseModel):
    v8: Any  # Vec8 - type checker can't infer the dynamic type
    v384: Any | None = None  # Vec384 | None - type checker can't infer the dynamic type
    v2d: Any | None = None  # Vec2D | None - type checker can't infer the dynamic type


@pytest.mark.prop
class TestPydanticArrayTypes:
    """Property-based tests for Pydantic array types with shape validation."""

    @given(hnp.arrays(dtype=hnp.floating_dtypes(sizes=(16, 32, 64)), shape=8))
    @settings(max_examples=20, deadline=200)
    def test_vec8_accepts_correct_shape_and_coerces_dtype(self, arr: np.ndarray) -> None:  # type: ignore[misc]
        """Test that Vec8 accepts arrays with shape (8,) and coerces to float32."""
        try:
            model = ArrayTestModel(v8=arr)

            # Check shape is preserved
            assert model.v8.shape == (8,)  # type: ignore[attr-defined]

            # Check dtype is coerced to float32
            assert model.v8.dtype == np.float32  # type: ignore[attr-defined]

            # Check values are preserved (within floating point precision)
            np.testing.assert_array_almost_equal(model.v8, arr.astype(np.float32), decimal=5)  # type: ignore[arg-type]

        except Exception as e:
            record_case(
                "vec8_shape_dtype_coercion_failed",
                {
                    "input_shape": arr.shape,
                    "input_dtype": str(arr.dtype),
                    "error": str(e),
                    "input_values": arr.tolist()[:10],  # First 10 values for debugging
                },
            )
            raise

    @given(hnp.arrays(dtype=hnp.floating_dtypes(sizes=(16, 32, 64)), shape=7))
    @settings(max_examples=10, deadline=200)
    def test_vec8_rejects_wrong_shape(self, arr: np.ndarray) -> None:  # type: ignore[misc]
        """Test that Vec8 rejects arrays with wrong shape."""
        with pytest.raises(ValidationError) as exc_info:
            ArrayTestModel(v8=arr)

        # Verify the error message mentions shape
        error_msg = str(exc_info.value)
        assert "shape" in error_msg.lower() or "Expected shape" in error_msg

    @given(hnp.arrays(dtype=hnp.floating_dtypes(sizes=(16, 32, 64)), shape=8))
    @settings(max_examples=10, deadline=200)
    def test_vec8_json_serialization_produces_list_of_floats(self, arr: np.ndarray) -> None:  # type: ignore[misc]
        """Test that JSON serialization produces a list of floats with correct length."""
        model = ArrayTestModel(v8=arr)
        json_data: Any = model.model_dump()

        # Check that v8 is serialized as a list
        assert isinstance(json_data["v8"], list)
        assert len(json_data["v8"]) == 8  # type: ignore[arg-type]

        # Check that all elements are floats
        for val in json_data["v8"]:  # type: ignore[misc]
            assert isinstance(val, (int, float))
            assert not math.isnan(val)
            assert not math.isinf(val)

    @given(hnp.arrays(dtype=hnp.floating_dtypes(sizes=(16, 32, 64)), shape=384))
    @settings(max_examples=10, deadline=200)
    def test_vec384_accepts_correct_shape(self, arr: np.ndarray) -> None:  # type: ignore[misc]
        """Test that Vec384 accepts arrays with shape (384,) and coerces to float32."""
        try:
            model = ArrayTestModel(v8=np.zeros(8), v384=arr)

            # Check shape is preserved
            assert model.v384 is not None
            assert model.v384.shape == (384,)  # type: ignore[attr-defined]

            # Check dtype is coerced to float32
            assert model.v384.dtype == np.float32  # type: ignore[attr-defined]

        except Exception as e:
            record_case(
                "vec384_shape_dtype_coercion_failed",
                {"input_shape": arr.shape, "input_dtype": str(arr.dtype), "error": str(e)},
            )
            raise

    @given(hnp.arrays(dtype=hnp.floating_dtypes(sizes=(16, 32, 64)), shape=(10, 20)))
    @settings(max_examples=10, deadline=200)
    def test_vec2d_accepts_correct_2d_shape(self, arr: np.ndarray) -> None:  # type: ignore[misc]
        """Test that Vec2D accepts arrays with shape (10, 20) and coerces to float32."""
        try:
            model = ArrayTestModel(v8=np.zeros(8), v2d=arr)

            # Check shape is preserved
            assert model.v2d is not None
            assert model.v2d.shape == (10, 20)  # type: ignore[attr-defined]

            # Check dtype is coerced to float32
            assert model.v2d.dtype == np.float32  # type: ignore[attr-defined]

        except Exception as e:
            record_case(
                "vec2d_shape_dtype_coercion_failed",
                {"input_shape": arr.shape, "input_dtype": str(arr.dtype), "error": str(e)},
            )
            raise

    @given(hnp.arrays(dtype=hnp.floating_dtypes(sizes=(16, 32, 64)), shape=8))
    @settings(max_examples=10, deadline=200)
    def test_array_handles_special_values(self, arr: np.ndarray) -> None:  # type: ignore[misc]
        """Test that arrays with special values (inf, nan) are handled correctly."""
        # Add some special values
        arr[0] = np.inf
        arr[1] = -np.inf
        arr[2] = np.nan

        try:
            model = ArrayTestModel(v8=arr)

            # Check that the array is still valid
            assert model.v8.shape == (8,)  # type: ignore[attr-defined]
            assert model.v8.dtype == np.float32  # type: ignore[attr-defined]

            # Check that special values are preserved
            assert np.isinf(model.v8[0])  # type: ignore[index]
            assert np.isinf(model.v8[1])  # type: ignore[index]
            assert np.isnan(model.v8[2])  # type: ignore[index]

        except Exception as e:
            record_case(
                "array_special_values_failed",
                {
                    "input_shape": arr.shape,
                    "input_dtype": str(arr.dtype),
                    "error": str(e),
                    "special_values": [arr[0], arr[1], arr[2]],
                },
            )
            raise

    @given(hnp.arrays(dtype=hnp.floating_dtypes(sizes=(16, 32, 64)), shape=8))
    @settings(max_examples=10, deadline=200)
    def test_array_json_roundtrip_preserves_values(self, arr: np.ndarray) -> None:  # type: ignore[misc]
        """Test that JSON serialization and deserialization preserves values."""
        model = ArrayTestModel(v8=arr)

        # Serialize to JSON
        json_str: Any = model.model_dump_json()

        # Deserialize from JSON
        parsed_model: Any = ArrayTestModel.model_validate_json(json_str)

        # Check that values are preserved
        np.testing.assert_array_almost_equal(model.v8, parsed_model.v8, decimal=5)  # type: ignore[arg-type]

    @given(hnp.arrays(dtype=hnp.floating_dtypes(sizes=(16, 32, 64)), shape=8))
    @settings(max_examples=10, deadline=200)
    def test_array_validation_rejects_non_ndarray(self, arr: np.ndarray) -> None:  # type: ignore[misc]
        """Test that validation rejects non-numpy array inputs."""
        # Test with list
        with pytest.raises(ValidationError):
            ArrayTestModel(v8=arr.tolist())

        # Test with tuple
        with pytest.raises(ValidationError):
            ArrayTestModel(v8=tuple(arr.tolist()))

        # Test with dict
        with pytest.raises(ValidationError):
            ArrayTestModel(v8={"data": arr.tolist()})
