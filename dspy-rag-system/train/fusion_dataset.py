"""
Training dataset builder for fusion head.

This module builds positive/negative training pairs from gold cases
for learning optimal fusion weights.
"""

import json
import logging
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


def load_gold_cases(path: str) -> List[Dict[str, Any]]:
    """
    Load gold cases from JSONL file.

    Args:
        path: Path to gold cases JSONL file

    Returns:
        List of gold case dictionaries
    """
    cases = []
    with open(path, "r") as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))
    return cases


def gold_match(row: Dict[str, Any], gold: Dict[str, Any]) -> bool:
    """
    Check if a retrieved row matches the gold standard for a case.

    Args:
        row: Retrieved result row
        gold: Gold case dictionary

    Returns:
        True if row matches gold standard
    """
    file_path = row.get("file_path", "")
    filename = row.get("filename", "")

    # Check expected files
    expected_files = gold.get("expected_files", [])
    if expected_files:
        for expected in expected_files:
            if expected in file_path or expected in filename:
                return True

    # Check globs
    globs = gold.get("globs", [])
    if globs:
        import fnmatch

        for pattern in globs:
            if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(filename, pattern):
                return True

    return False


def make_query_parts(user_q: str, tag: str = "") -> Tuple[str, str, str]:
    """
    Extract query components using the query rewrite module.

    Args:
        user_q: Raw user query
        tag: Query tag for hint selection

    Returns:
        Tuple of (q_short, q_title, q_bm25)
    """
    try:
        from src.dspy_modules.retriever.query_rewrite import build_channel_queries

        queries = build_channel_queries(user_q, tag)
        return queries["short"], queries["title"], queries["bm25"]
    except ImportError:
        # Fallback if module not available
        logger.warning("Query rewrite module not available, using raw query")
        return user_q, user_q, user_q


def embed_query(user_q: str, model_name: str) -> List[float]:
    """
    Embed query using sentence transformers.

    Args:
        user_q: Raw user query
        model_name: Sentence transformer model name

    Returns:
        Query embedding as list of floats
    """
    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(model_name)
        embedding = model.encode(user_q)
        return embedding.tolist()
    except ImportError:
        logger.warning("Sentence transformers not available, returning empty embedding")
        return []
    except Exception as e:
        logger.warning(f"Embedding failed: {e}, returning empty embedding")
        return []


def collect_candidates(user_q: str, tag: str, k: int) -> List[Dict[str, Any]]:
    """
    Collect retrieval candidates for a query.

    Args:
        user_q: Raw user query
        tag: Query tag
        k: Number of candidates to retrieve

    Returns:
        List of candidate result dictionaries
    """
    try:
        from src.dspy_modules.retriever.pg import run_fused_query
        from src.dspy_modules.retriever.query_rewrite import build_channel_queries

        # Build query components
        queries = build_channel_queries(user_q, tag)
        q_short = queries["short"]
        q_title = queries["title"]
        q_bm25 = queries["bm25"]

        # Get embedding
        qvec = embed_query(user_q, "sentence-transformers/all-MiniLM-L6-v2")

        # Run retrieval
        candidates = run_fused_query(
            q_short=q_short,
            q_title=q_title,
            q_bm25=q_bm25,
            qvec=qvec,
            k=k,
            use_mmr=False,  # Disable MMR for training
            tag=tag,
            return_components=True,
        )

        return candidates

    except Exception as e:
        logger.error(f"Failed to collect candidates for query '{user_q}': {e}")
        return []


def build_pairs(
    cases: List[Dict[str, Any]], pairs_per_query: int, k_pool: int, model_name: str, feature_names: List[str]
) -> List[Tuple[List[float], List[float]]]:
    """
    Build positive/negative training pairs from gold cases.

    Args:
        cases: List of gold case dictionaries
        pairs_per_query: Number of pairs to generate per query
        k_pool: Number of candidates to retrieve per query
        model_name: Sentence transformer model name
        feature_names: List of feature names in order

    Returns:
        List of (positive_features, negative_features) tuples
    """
    pairs = []

    for case in cases:
        if case.get("mode") != "retrieval":
            continue  # Only use retrieval cases

        user_q = case.get("query", "")
        if not user_q:
            continue

        tag = case.get("tags", [""])[0] if case.get("tags") else ""

        # Collect candidates
        candidates = collect_candidates(user_q, tag, k_pool)
        if len(candidates) < 2:
            continue

        # Find positive matches
        positives = []
        negatives = []

        for candidate in candidates:
            if gold_match(candidate, case):
                positives.append(candidate)
            else:
                negatives.append(candidate)

        if not positives or not negatives:
            continue  # Need both positives and negatives

        # Generate pairs
        pairs_generated = 0
        for pos in positives:
            if pairs_generated >= pairs_per_query:
                break

            # Sample hard negatives (highest scoring non-positives)
            neg_candidates = sorted(negatives, key=lambda x: x.get("score", 0.0), reverse=True)

            for neg in neg_candidates[: pairs_per_query - pairs_generated]:
                # Extract features
                pos_features = extract_features(pos, feature_names)
                neg_features = extract_features(neg, feature_names)

                if pos_features and neg_features:
                    pairs.append((pos_features, neg_features))
                    pairs_generated += 1

                if pairs_generated >= pairs_per_query:
                    break

    logger.info(f"Generated {len(pairs)} training pairs from {len(cases)} cases")
    return pairs


def extract_features(row: Dict[str, Any], feature_names: List[str]) -> List[float]:
    """
    Extract features from a retrieval result row.

    Args:
        row: Retrieval result dictionary
        feature_names: List of feature names to extract

    Returns:
        List of feature values
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
            code_extensions = {
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
            is_code = any(file_path.endswith(ext) for ext in code_extensions)
            features.append(1.0 if is_code else 0.0)
        else:
            # Unknown feature, default to 0.0
            features.append(0.0)

    return features


def build_fusion_features_for_training(row: Dict[str, Any]):
    """
    Build a FusionFeatures object from a retrieval result row for training data.
    This provides schema validation and JSON-safe serialization.

    Args:
        row: Retrieval result dictionary

    Returns:
        FusionFeatures object with validated and typed data
    """
    from dspy_modules.retriever.feature_schema import FusionFeatures

    # Extract scalar features
    file_path = row.get("file_path", "")
    code_extensions = {
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
    is_code = any(file_path.endswith(ext) for ext in code_extensions)

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
