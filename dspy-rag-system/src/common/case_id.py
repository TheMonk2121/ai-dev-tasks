import hashlib
import os
import re
import unicodedata



def _slugify(text: str, max_len: int = 60) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return text[:max_len]


def canonical_case_id(query: str, source_path: str, variant: str | None = None) -> str:
    """Return a stable, human-readable case id based on query and source.

    The ID is a slug of the query plus a short hash of the tuple
    (query.strip(), normalized_source_path, variant or '').
    """
    norm_path = os.path.normpath(source_path or "")
    base = f"{(query or '').strip()}|{norm_path}|{variant or ''}"
    short = hashlib.sha1(base.encode("utf-8")).hexdigest()[:8]
    return f"{_slugify(query or '')}-{short}"
