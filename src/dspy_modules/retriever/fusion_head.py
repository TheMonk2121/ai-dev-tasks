"""
Runtime loader and scorer for the learned fusion head.

This module provides utilities to load a trained fusion head and apply it
to retrieval results at runtime.
"""

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

# Code file extensions for boolean feature
CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".cs",
    ".go",
    ".rs",
    ".php",
    ".rb",
    ".swift",
    ".kt",
    ".scala",
    ".r",
    ".m",
    ".mm",
    ".sh",
    ".bash",
    ".zsh",
    ".fish",
}


def load_feature_spec(path: str) -> list[str]:
    """
    Load feature specification from JSON file.

    Args:
        path: Path to JSON file containing list of feature names

    Returns:
        List of feature names in order

    Raises:
        FileNotFoundError: If spec file doesn't exist
        ValueError: If spec file is invalid
    """
    try:
        with open(path) as f:
            spec = json.load(f)

        if not isinstance(spec, list):
            raise ValueError(f"Feature spec must be a list, got {type(spec)}")

        if not all(isinstance(name, str) for name in spec):
            raise ValueError("All feature names must be strings")

        return spec
    except FileNotFoundError:
        logger.error(f"Feature spec file not found: {path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in feature spec file {path}: {e}")
        raise


def build_features_from_row(row: dict[str, Any], feature_names: list[str]) -> list[float]:
    """
    Extract features from a retrieval result row.

    Args:
        row: Dictionary containing retrieval result data
        feature_names: List of feature names to extract

    Returns:
        List of feature values in the same order as feature_names
    """
    features = []

    for name in feature_names:
        if name == "s_bm25":
            features.append(float(row.get("s_bm25", 0.0)))
        elif name == "s_vec":
            features.append(float(row.get("s_vec", 0.0)))
        elif name == "s_title":
            features.append(float(row.get("s_title", 0.0)))
        elif name == "s_short":
            features.append(float(row.get("s_short", 0.0)))
        elif name == "s_path":
            features.append(float(row.get("s_path", 0.0)))
        elif name == "prior_scaled":
            features.append(float(row.get("prior_scaled", 0.0)))
        elif name == "is_code":
            # Boolean feature: 1.0 if file is code, 0.0 otherwise
            file_path = row.get("file_path", "")
            is_code = any(file_path.endswith(ext) for ext in CODE_EXTENSIONS)
            features.append(1.0 if is_code else 0.0)
        else:
            # Unknown feature, default to 0.0
            logger.warning(f"Unknown feature name: {name}, defaulting to 0.0")
            features.append(0.0)

    return features


def build_fusion_features_from_row(row: dict[str, Any]):
    """
    Build a FusionFeatures object from a retrieval result row.
    This provides schema validation and JSON-safe serialization.

    Args:
        row: Dictionary containing retrieval result data

    Returns:
        FusionFeatures object with validated and typed data
    """
    from dspy_modules.retriever.feature_schema import FusionFeatures

    # Extract scalar features
    file_path = row.get("file_path", "")
    is_code = any(file_path.endswith(ext) for ext in CODE_EXTENSIONS)

    # Build feature object with validation
    return FusionFeatures(
        s_bm25=float(row.get("s_bm25", 0.0)),
        s_vec=float(row.get("s_vec", 0.0)),
        s_title=float(row.get("s_title", 0.0)),
        s_short=float(row.get("s_short", 0.0)),
        r_bm25=float(row.get("r_bm25", 0.0)),
        r_vec=float(row.get("r_vec", 0.0)),
        len_norm=float(row.get("len_norm", 1.0)),
        is_code=is_code,
        tag_bias_hint=float(row.get("tag_bias_hint", 0.0)),
        # Optional: include dense vectors if available
        q_vec=row.get("q_vec"),  # Will be validated as Vector384 if provided
        d_vec=row.get("d_vec"),  # Will be validated as Vector384 if provided
    )


def load_head(checkpoint_path: str, in_dim: int, hidden: int = 0, device: str = "cpu") -> Any:
    """
    Load a trained fusion head from checkpoint.

    Args:
        checkpoint_path: Path to PyTorch checkpoint file
        in_dim: Expected input dimension
        hidden: Hidden layer size (must match training)
        device: Device to load model on

    Returns:
        Loaded PyTorch model in eval mode

    Raises:
        ImportError: If PyTorch is not available
        FileNotFoundError: If checkpoint doesn't exist
        RuntimeError: If model loading fails
    """
    try:
        import torch
        from train.fusion_head import FusionHead
    except ImportError as e:
        logger.error(f"PyTorch not available for fusion head: {e}")
        raise ImportError("PyTorch required for fusion head but not installed")

    if not os.path.exists(checkpoint_path):
        raise FileNotFoundError(f"Fusion head checkpoint not found: {checkpoint_path}")

    try:
        # Create model with same architecture as training
        model = FusionHead(in_dim=in_dim, hidden=hidden)

        # Load state dict
        checkpoint = torch.load(checkpoint_path, map_location=device)
        model.load_state_dict(checkpoint)

        # Set to eval mode and move to device
        model.eval()
        model.to(device)

        logger.info(f"Loaded fusion head from {checkpoint_path} (in_dim={in_dim}, hidden={hidden})")
        return model

    except Exception as e:
        logger.error(f"Failed to load fusion head from {checkpoint_path}: {e}")
        raise RuntimeError(f"Model loading failed: {e}")


def score_rows(
    rows: list[dict[str, Any]], feature_names: list[str], head: Any, device: str = "cpu"
) -> list[dict[str, Any]]:
    """
    Score a batch of retrieval results using the fusion head.

    Args:
        rows: List of retrieval result dictionaries
        feature_names: List of feature names to extract
        head: Loaded PyTorch model
        device: Device to run inference on

    Returns:
        List of rows with added 'score_learned' field
    """
    if not rows:
        return rows

    try:
        import torch
    except ImportError:
        logger.error("PyTorch not available for fusion head scoring")
        return rows

    try:
        # Build feature matrix
        features = []
        for row in rows:
            feature_vector = build_features_from_row(row, feature_names)
            features.append(feature_vector)

        # Convert to tensor
        feature_tensor = torch.tensor(features, dtype=torch.float32, device=device)

        # Run inference
        with torch.no_grad():
            scores = head(feature_tensor)
            scores_list = scores.cpu().tolist()

        # Add scores to rows
        result_rows = []
        for i, row in enumerate(rows):
            new_row = row.copy()
            new_row["score_learned"] = float(scores_list[i])
            result_rows.append(new_row)

        logger.debug(f"Scored {len(rows)} rows with fusion head")
        return result_rows

    except Exception as e:
        logger.error(f"Fusion head scoring failed: {e}")
        # Return original rows without learned scores
        return rows
