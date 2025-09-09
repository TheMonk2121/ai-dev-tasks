#!/usr/bin/env python3
"""
Utility script for persisting training features to JSONL using FusionFeatures schema.
This ensures all training data is validated and JSON-safe.
"""

import json
from typing import Any, Dict, List

from feature_io import write_feature

from dspy_modules.retriever.feature_schema import FusionFeatures


def persist_features_to_jsonl(features: List[Dict[str, Any]], output_path: str, validate: bool = True) -> int:
    """
    Persist a list of feature dictionaries to JSONL using FusionFeatures schema.

    Args:
        features: List of feature dictionaries
        output_path: Path to output JSONL file
        validate: Whether to validate features against schema

    Returns:
        Number of features successfully written
    """
    written_count = 0

    with open(output_path, "w") as f:
        for feature_dict in features:
            try:
                if validate:
                    # Validate using FusionFeatures schema
                    fusion_feature = FusionFeatures(**feature_dict)
                    json_line = write_feature(fusion_feature)
                else:
                    # Direct JSON serialization (faster but no validation)
                    json_line = json.dumps(feature_dict)

                f.write(json_line + "\n")
                written_count += 1

            except Exception as e:
                print(f"Warning: Skipping invalid feature: {e}")
                continue

    print(f"Successfully wrote {written_count} features to {output_path}")
    return written_count


def load_features_from_jsonl(input_path: str) -> List[FusionFeatures]:
    """
    Load features from JSONL file with schema validation.

    Args:
        input_path: Path to input JSONL file

    Returns:
        List of validated FusionFeatures objects
    """
    from feature_io import read_feature

    features = []
    with open(input_path, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                feature = read_feature(line)
                features.append(feature)
            except Exception as e:
                print(f"Warning: Skipping invalid feature on line {line_num}: {e}")
                continue

    print(f"Successfully loaded {len(features)} features from {input_path}")
    return features


def main():
    """Example usage of the persistence utilities."""
    import argparse

    parser = argparse.ArgumentParser(description="Persist training features to JSONL")
    parser.add_argument("--input", required=True, help="Input features JSON file")
    parser.add_argument("--output", required=True, help="Output JSONL file")
    parser.add_argument("--validate", action="store_true", help="Validate features against schema")

    args = parser.parse_args()

    # Load features from JSON
    with open(args.input, "r") as f:
        features = json.load(f)

    # Persist to JSONL with validation
    count = persist_features_to_jsonl(features, args.output, validate=args.validate)
    print(f"Processed {count} features")


if __name__ == "__main__":
    main()
