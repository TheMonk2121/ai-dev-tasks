#!/usr/bin/env python3
"""
Optimized Documentation Coherence Validation System

Enhanced version with parallel processing, only-changed mode, and caching.
Target: 50% performance improvement (0.80s → <0.40s)

Usage: python scripts/doc_coherence_validator.py [--dry-run] [--only-changed] [--workers N] [--json]
"""

import argparse
import datetime
import functools
import hashlib
import json
import multiprocessing
import os
import pickle
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union

# Import few-shot integration framework
try:
    from few_shot_integration import FewShotExampleLoader

    FEW_SHOT_AVAILABLE = True
except ImportError:
    FEW_SHOT_AVAILABLE = False
    print("⚠️  Few-shot integration not available - running in standard mode")

# Pre-compile all regex patterns at module level for performance
HEADING_INCREMENT_PATTERN = re.compile(r"^#{1,6}\s")
HEADING_STYLE_PATTERN = re.compile(r"^(#{1,6}|\={3,}|\-{3,})")
LIST_INDENT_PATTERN = re.compile(r"^\s*[-*+]\s")
TRAILING_SPACES_PATTERN = re.compile(r"\s+$")
HARD_TABS_PATTERN = re.compile(r"\t")
LINE_LENGTH_PATTERN = re.compile(r"^.{121,}$")
CROSS_REFERENCE_PATTERN = re.compile(r"<!--\s*([A-Z_]+):\s*([^>]+?)\s*-->")
FILE_REFERENCE_PATTERN = re.compile(r"`([^`]+\.md)`")
BACKLOG_REFERENCE_PATTERN = re.compile(r"B-\d+")
TLDR_ANCHOR_PATTERN = re.compile(
    r'<a\s+id="tldr"\s*>\s*</a>|<a\s+id="tldr"\s*>|\{#tldr\}', re.IGNORECASE
)
TLDR_HEADING_PATTERN = re.compile(r"^##\s+🔎\s+TL;DR\s*.*$", re.MULTILINE)
AT_A_GLANCE_HEADER_PATTERN = re.compile(
    r"^\|\s*what this file is\s*\|\s*read when\s*\|\s*do next\s*\|\s*$", re.MULTILINE
)
HTML_ANCHOR_PATTERN = re.compile(r'<a\s+id="([^"]+)"\s*>', re.IGNORECASE)
MARKDOWN_ANCHOR_PATTERN = re.compile(r"\{#([^}]+)\}", re.IGNORECASE)

# --- BEGIN: reference checker utilities ---
# Fenced code blocks we should ignore when scanning for refs
FENCE_RE = re.compile(r"```.*?```|~~~.*?~~~", re.DOTALL)

# Real markdown links to local .md files (exclude http/mailto/etc.)
MD_LINK_RE = re.compile(
    r"""\[([^\]]+)\]\(           # [label](
		(?!https?://|mailto:|ftp://|\#) # no absolute urls/anchors
		([^)#\s]+?\.md)          # group(2) = path ending in .md (no spaces)
		(\#[^)]+)?                # optional group(3) = #fragment
	\)""",
    re.VERBOSE,
)

# Backticked .md tokens (style-only; warn if broken)
BACKTICK_MD_RE = re.compile(r"`([^`]+?\.md(?:#[^`]+)?)`")


def strip_fences(text: str) -> str:
    return FENCE_RE.sub("", text)


def _normalize_ref(ref: str) -> str:
    # drop fragment for FS checks; normalize slashes
    base = ref.split("#", 1)[0].replace("\\", "/")
    # collapse redundant ./ segments
    base = re.sub(r"/\./", "/", base).lstrip("./")
    return base


def _exists_case_sensitive(p: Path) -> bool:
    """True if path exists and each component matches case on FS."""
    try:
        parts = p.resolve().parts
    except Exception:
        return False
    # Walk from root to leaf verifying case via directory listings
    cur = Path(parts[0])
    for name in parts[1:]:
        try:
            listing = {entry.name for entry in cur.iterdir()}
        except Exception:
            return False
        if name not in listing:
            return False
        cur = cur / name
    return True


@functools.lru_cache(maxsize=1)
def _repo_root_cached() -> Path:
    try:
        out = (
            subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                check=True,
                capture_output=True,
            )
            .stdout.decode()
            .strip()
        )
        return Path(out)
    except Exception:
        return Path.cwd()


@functools.lru_cache(maxsize=1)
def _load_path_aliases() -> dict[str, str]:
    """Optional alias map old->new, e.g., docs/path_aliases.json."""
    candidates = [
        _repo_root_cached() / "docs" / "path_aliases.json",
        _repo_root_cached() / "path_aliases.json",
    ]
    for p in candidates:
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                return {}
    return {}


def repo_root() -> Path:
    """Public wrapper for repo root to match external callers/tests."""
    return _repo_root_cached()


def _resolve_candidates(ref_path: str, doc_path: Path) -> tuple[list[Path], bool]:
    r = _repo_root_cached()
    # Try alias mapping first if any
    alias_map = _load_path_aliases()
    aliased = alias_map.get(ref_path, ref_path)
    alias_used = aliased != ref_path

    cands: list[Path] = []
    p = Path(aliased)
    if str(p).startswith("/"):
        # Treat as repo-absolute ("/docs/a.md" -> root/docs/a.md)
        cands.append((r / str(p).lstrip("/")).resolve())
    else:
        # doc-relative and repo-root candidates
        cands.append((doc_path.parent / p).resolve())
        cands.append((r / p).resolve())
    # Deduplicate while preserving order
    seen: set[str] = set()
    uniq: list[Path] = []
    for c in cands:
        s = str(c)
        if s not in seen:
            seen.add(s)
            uniq.append(c)
    return uniq, alias_used


def check_markdown_references(
    file_path: Path, text: str, enforce_lowercase: bool = False
) -> tuple[list[str], list[str], int]:
    """
    Returns (errors, warnings).
    - Broken [link](path.md) => error
    - Backticked `path.md` => warn (style-only), with "prefer Markdown link" hint
    Ignores fenced code blocks. Handles #fragments, repo-root/doc-relative, aliases, and slashes.
    """
    text2 = strip_fences(text)

    errors: list[str] = []
    warnings: list[str] = []
    alias_hits = 0

    # Collect unique refs to avoid duplicate noise
    link_refs: set[tuple[str, str]] = set()  # (path, raw_ref_string)
    tick_refs: set[tuple[str, str]] = set()

    for m in MD_LINK_RE.finditer(text2):
        raw = (m.group(2) or "") + (m.group(3) or "")
        link_refs.add((_normalize_ref(raw), raw))

    for m in BACKTICK_MD_RE.finditer(text2):
        raw = m.group(1)
        tick_refs.add((_normalize_ref(raw), raw))

    # Case policy: default on in CI, or via env
    lowercase_env = os.getenv("VALIDATOR_ENFORCE_LOWERCASE", "").lower() in {
        "1",
        "true",
        "yes",
    }
    enforce_case = enforce_lowercase or lowercase_env or ("--ci" in sys.argv)

    # Check links (error on miss)
    for path_norm, raw in sorted(link_refs):
        resolved = False
        cands, aliased = _resolve_candidates(path_norm, file_path)
        for cand in cands:
            if _exists_case_sensitive(cand):
                # Case policy check (applies to resolved only)
                if enforce_case and any(ch.isupper() for ch in raw):
                    errors.append(
                        f"Case policy: reference '{raw}' should be lowercase."
                    )
                if aliased:
                    alias_hits += 1
                resolved = True
                break
        if not resolved:
            errors.append(f"Link target not found: {raw} (from {file_path})")

    # Check backticked paths (style-only; warn if miss or case policy)
    for path_norm, raw in sorted(tick_refs):
        resolved = False
        cands, aliased = _resolve_candidates(path_norm, file_path)
        for cand in cands:
            if _exists_case_sensitive(cand):
                if enforce_case and any(ch.isupper() for ch in raw):
                    warnings.append(
                        f"Case policy: reference '{raw}' should be lowercase."
                    )
                warnings.append(f"Use Markdown link instead of backtick for: {raw}")
                if aliased:
                    alias_hits += 1
                resolved = True
                break
        if not resolved:
            warnings.append(
                f"Backticked file reference not found: {raw}. Prefer a real link like [label]({path_norm})."
            )

    return (errors, warnings, alias_hits)


# --- END: reference checker utilities ---
# Enhanced pragma regex with expiration and reason
PRAGMA_RE = re.compile(
    r"<!--\s*validator:allow\s+([a-z\-]+)(?:;\s*expires=([^;]+))?(?:;\s*reason=([^>]+))?\s*-->",
    re.I,
)

# Backlog compliance validator patterns
ROW_RE = re.compile(
    r"^\|\s*(B-\d{3})\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|"
)
SCORE_RE = re.compile(r"<!--\s*score:\s*(\{.*?\})\s*-->", re.DOTALL | re.IGNORECASE)
SCORE_TOTAL_RE = re.compile(
    r"<!--\s*score_total:\s*([0-9]+(?:\.[0-9]+)?)\s*-->", re.IGNORECASE
)
DO_NEXT_RE = re.compile(r"<!--\s*do_next:\s*(.*?)\s*-->", re.IGNORECASE)
ACCEPTANCE_RE = re.compile(r"<!--\s*acceptance:\s*(.*?)\s*-->", re.IGNORECASE)
EST_HOURS_RE = re.compile(
    r"<!--\s*est_hours:\s*([0-9]+(?:\.[0-9]+)?)\s*-->", re.IGNORECASE
)
LESSONS_APPLIED_RE = re.compile(
    r"<!--\s*lessons_applied:\s*(\[.*?\])\s*-->", re.DOTALL | re.IGNORECASE
)
REFERENCE_CARDS_RE = re.compile(
    r"<!--\s*reference_cards:\s*(\[.*?\])\s*-->", re.DOTALL | re.IGNORECASE
)
PRD_LINK_RE = re.compile(r"\(?(?:PRD|prd)\s*:\s*([^) \t]+)\)?")

# Exit codes for backlog validator
OK, FAIL, ERROR = 0, 2, 1

# Required score keys for backlog validation
REQUIRED_SCORE_KEYS = {"bv", "tc", "rr", "le", "lessons", "effort", "deps"}

# Environment flags for B-100 and B-102 validation
REQUIRE_MULTI_REP = os.getenv("VALIDATOR_REQUIRE_MULTI_REP", "1") == "1"
REQUIRE_XREF = os.getenv("VALIDATOR_REQUIRE_XREF", "1") == "1"
STRICT_STALE_XREF = os.getenv("VALIDATOR_STRICT_STALE_XREF", "0") == "1"


def env_bool(name: str, default: bool = True) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


# Per-category FAIL mode flags (robust env parsing)
ARCHIVE_FAIL = env_bool("VALIDATOR_ARCHIVE_FAIL", default=False)
SHADOW_FAIL = env_bool("VALIDATOR_SHADOW_FAIL", default=False)
README_FAIL = env_bool("VALIDATOR_README_FAIL", default=False)
MULTIREP_FAIL = env_bool("VALIDATOR_MULTIREP_FAIL", default=False)
REFERENCES_FAIL = env_bool("VALIDATOR_REFERENCES_FAIL", default=True)

# Canonical keys with synonyms for validator exceptions
KEY_SYNONYMS = {
    "xref-missing": {"xref-missing", "multirep-xref", "xref"},
    "multi-rep-missing": {"multi-rep-missing", "multirep", "multi-rep"},
}

# Shadow fork detection patterns (ChatGPT's validator rule)
# Focus on our project's problematic patterns, not legitimate third-party naming
ENHANCED_PATTERNS = [
    # Match both prefix and suffix patterns: enhanced_foo.py, foo_enhanced.py, optimized_foo.py, foo_optimized.py
    re.compile(r".*[_-](enhanced|optimized)\.py$", re.IGNORECASE),
    re.compile(r".*(enhanced|optimized)[_-].*\.py$", re.IGNORECASE),
]


# Archive validation helper functions
def _canon_rel(path: str, root: str) -> str:
    """repo-relative, POSIX-style"""
    rel = os.path.relpath(os.path.abspath(path), os.path.abspath(root))
    return rel.replace(os.sep, "/")


def _blob_sha_from_bytes(data: bytes) -> str:
    """Compute git blob SHA1 without invoking git: sha1(b'blob {len}\0' + data)"""
    header = f"blob {len(data)}\0".encode()
    h = hashlib.sha1()
    h.update(header)
    h.update(data)
    return h.hexdigest()


def _blob_sha_for_path(path: str) -> str:
    with open(path, "rb") as f:
        return _blob_sha_from_bytes(f.read())


def _load_manifest(manifest_path="data/archive_manifest.json"):
    try:
        with open(manifest_path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"files": {}}


def _manifest_lookup(manifest: dict, rel_posix: str):
    # manifest["files"] is keyed by repo-relative POSIX paths
    files = manifest.get("files", {})
    return files.get(rel_posix)


# Optional debug flag
DEBUG_ARCH = os.getenv("VALIDATOR_DEBUG_ARCHIVE") == "1"


def _dbg(msg: str):
    if DEBUG_ARCH:
        print(f"[archive-debug] {msg}", file=sys.stderr)


def warn(msg: str):
    """Route warnings to stderr when --json is set to avoid corrupting JSON output."""
    # Check if we're in JSON mode by looking at sys.argv
    json_mode = "--json" in sys.argv
    stream = sys.stderr if json_mode else sys.stdout
    print(f"⚠️  WARN: {msg}", file=stream)


def _posix_rel(
    p: Union[str, os.PathLike[str]], root: Union[str, os.PathLike[str]]
) -> str:
    """Convert path to repo-relative POSIX format for consistent reporting."""
    ps = os.fspath(p)
    rs = os.fspath(root)
    if isinstance(ps, bytes):
        ps = ps.decode("utf-8", "ignore")
    if isinstance(rs, bytes):
        rs = rs.decode("utf-8", "ignore")
    rel_path = os.path.relpath(os.path.abspath(ps), os.path.abspath(rs))
    if os.sep != "/":
        rel_path = rel_path.replace(os.sep, "/")
    return rel_path


ARCHIVE_ALLOWLIST = re.compile(r"(^|/)600_archives(/|$)")

# Directories to ignore when scanning for shadow forks
IGNORED_DIR_SEGMENTS = (
    "/.venv/",
    "/venv/",
    "/.direnv/",
    "/.tox/",
    "/__pypackages__/",
    "/site-packages/",
    "/.mypy_cache/",
    "/.pytest_cache/",
    "/build/",
    "/dist/",
    "/node_modules/",
    "/.git/",
)

# Archive immutability constants
ARCHIVE_ROOT = "600_archives/"

# README governance constants
README_STALE_DAYS = int(os.getenv("VALIDATOR_README_STALE_DAYS", "120"))
README_GOVERNANCE_ENABLED = os.getenv("VALIDATOR_README_GOVERNANCE_ENABLED", "1") == "1"
STRICT_README_GOVERNANCE = os.getenv("VALIDATOR_STRICT_README_GOVERNANCE", "0") == "1"

# Docs impact gate constants
DOCS_IMPACT_ENABLED = os.getenv("VALIDATOR_DOCS_IMPACT_ENABLED", "1") == "1"
STRICT_DOCS_IMPACT = os.getenv("VALIDATOR_STRICT_DOCS_IMPACT", "0") == "1"
DOCS_IMPACT_TARGET_PREFIXES = (
    "dspy-rag-system/src/vector_store/",
    "src/vector_store/",
)
DOCS_IMPACT_REQUIRED = (
    "400_guides/400_system-overview.md",
    "500_reference-cards.md",
    "401_consensus-log.md",
    "dspy-rag-system/src/vector_store/README.md",
    "dspy-rag-system/README.md",
)

# README scoping constants
README_SCOPE_DIRS = {
    "",
    "000_core",
    "400_guides",
    "500_reference",
    "docs",
    "dspy-rag-system",
    "dashboard",
}
README_IGNORE_SEGMENTS = (
    "/.git/",
    "/.github/",
    "/.mypy_cache/",
    "/.pytest_cache/",
    "/.venv/",
    "/venv/",
    "/.tox/",
    "/build/",
    "/dist/",
    "/node_modules/",
    "/site-packages/",
    "/600_archives/",
)


# Helper functions for exception ledger and pragma handling
def _now_utc():
    """Get current UTC time."""
    return datetime.datetime.now(datetime.timezone.utc)


def _load_ledger(path):
    """Load exception ledger from JSON file."""
    if not path:
        return {}
    try:
        with open(path) as f:
            j = json.load(f)
        return j.get("exceptions", {})
    except Exception:
        return {}


def _ledger_allows(ledger, relpath, key):
    """Check if ledger allows exception for given file and key."""
    syns = KEY_SYNONYMS.get(key, {key})
    for entry in ledger.get(relpath, []):
        if entry.get("key", "").lower() in syns:
            exp = entry.get("expires")
            if not exp:
                return True
            try:
                # Robust date parsing (YYYY-MM-DD or ISO w/ Z)
                if len(exp) == 10 and exp[4] == "-" and exp[7] == "-":
                    expiry = datetime.datetime.fromisoformat(exp).replace(
                        hour=23, minute=59, second=59, tzinfo=datetime.timezone.utc
                    )
                else:
                    expiry = datetime.datetime.fromisoformat(exp.replace("Z", "+00:00"))

                # Check if near expiry (7 days)
                now = _now_utc()
                days_remaining = (expiry - now).days
                if days_remaining <= 7:
                    warn(f"Exception for {relpath} expires in {days_remaining} days")
                    entry["near_expiry"] = True

                return now <= expiry
            except Exception:
                return False
    return False


def _pragma_allows(text, key):
    """Check if pragma allows exception for given key."""
    syns = KEY_SYNONYMS.get(key, {key})
    return any(m.group(1).lower() in syns for m in PRAGMA_RE.finditer(text))


# Link detection regex for XRef validation
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _has_internal_xref(relpath, root):
    """Check if file has at least one internal cross-reference."""
    full = os.path.join(root, relpath)
    try:
        with open(full, encoding="utf-8") as f:
            txt = f.read()
    except Exception:
        return False

    for _, target in LINK_RE.findall(txt):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        # Normalize and ignore self-links
        tgt = target.split("#", 1)[0]
        if not tgt:
            continue
        norm = os.path.normpath(os.path.join(os.path.dirname(relpath), tgt))
        if norm.endswith(".md") and norm != relpath:
            return True
    return False


def parse_expiry(s: str) -> datetime.datetime:
    """Parse expiry date with timezone handling"""
    s = s.strip()
    if len(s) == 10 and s[4] == "-" and s[7] == "-":  # YYYY-MM-DD
        return datetime.datetime.fromisoformat(s).replace(
            hour=23, minute=59, second=59, tzinfo=datetime.timezone.utc
        )
    if s.endswith("Z"):
        s = s.replace("Z", "+00:00")
    dt = datetime.datetime.fromisoformat(s)
    return dt if dt.tzinfo else dt.replace(tzinfo=datetime.timezone.utc)


def file_allows(fn, key):
    """Check if file allows specific validator violations via pragmas"""
    try:
        with open(fn, encoding="utf-8", errors="ignore") as f:
            txt = f.read()

        for match in PRAGMA_RE.finditer(txt):
            pragma_key = match.group(1).lower()
            expires = match.group(2)
            reason = match.group(3)

            if pragma_key == key:
                if expires:
                    try:
                        expiry_date = parse_expiry(expires)
                        now = datetime.datetime.now(datetime.timezone.utc)
                        if now > expiry_date:
                            print(f"EXPIRED PRAGMA: {fn} - {reason}")
                            return False
                    except ValueError as e:
                        print(f"INVALID EXPIRY: {fn} - {expires} ({e})")
                        return False

                return True
        return False
    except Exception:
        return False


def iter_readmes(root):
    """Iterate over README files in scope"""
    # Always include root README.md
    root_readme = os.path.join(root, "README.md")
    if os.path.exists(root_readme):
        yield root_readme

    for dirpath, _, filenames in os.walk(root):
        if any(seg in dirpath for seg in README_IGNORE_SEGMENTS):
            continue
        rel = os.path.relpath(dirpath, root)
        top = "" if rel == "." else rel.split(os.sep)[0]
        if top not in README_SCOPE_DIRS:
            continue
        for fn in filenames:
            if fn.lower().startswith("readme") and fn.lower().endswith(".md"):
                yield os.path.join(dirpath, fn)


def discover_files(root_path):
    """Discover files to validate"""
    root = os.path.abspath(root_path)
    files = []
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            if filename.endswith((".md", ".py", ".yml", ".yaml")):
                files.append(os.path.join(dirpath, filename))
    return files


def validate_archive_immutability_files(files):
    """Return list of violating archive files.

    Rule:
      - Any file under 600_archives/** must be present in the manifest and match its recorded blob_sha.
      - If a file is newly enrolled (manifest entry has "enrollment": true), we accept it iff current
        bytes hash to the manifest's blob_sha. We do NOT require that HEAD contains the file yet.
      - Path checks use repo-relative POSIX paths, same as archive_restore.
    """
    root = os.path.abspath(".")
    manifest = _load_manifest()
    violations = []

    for path in files:
        # Only test archive paths
        posix = _canon_rel(path, root)
        if not posix.startswith("600_archives/"):
            continue

        meta = _manifest_lookup(manifest, posix)
        if not meta:
            _dbg(f"NOT ENROLLED: {posix}")
            violations.append(path)
            continue

        expected_sha = meta.get("blob_sha")
        if not expected_sha:
            _dbg(f"NO BLOB SHA: {posix}")
            violations.append(path)
            continue

        # Compare current bytes to manifest snapshot; no HEAD/git lookup needed
        try:
            current_sha = _blob_sha_for_path(path)
        except Exception as e:
            _dbg(f"READ FAIL ({posix}): {e}")
            violations.append(path)
            continue

        if current_sha != expected_sha:
            _dbg(
                f"SHA MISMATCH ({posix}): current={current_sha} expected={expected_sha}"
            )
            violations.append(path)
        else:
            # Good: enrolled & bytes match
            _dbg(f"OK ({posix}): matches manifest")
            continue

    return violations


def validate_shadow_forks_files(files):
    """Validate shadow forks and return violating files"""
    violations = []

    # Legitimate files that should not be flagged as shadow forks
    LEGITIMATE_ENHANCED_FILES = {
        "dspy-rag-system/src/enhanced_vector_store.py",
        "dspy-rag-system/src/dspy_modules/enhanced_vector_store.py",
    }

    for path in files:
        # Convert absolute path to relative for comparison
        try:
            rel_path = os.path.relpath(path, os.getcwd())
        except Exception:
            rel_path = path
        if os.sep != "/":
            rel_path = rel_path.replace(os.sep, "/")

        # Skip legitimate enhanced files
        if rel_path in LEGITIMATE_ENHANCED_FILES:
            continue

        # Skip files in archives (handled by archive validation)
        if ARCHIVE_ROOT in path:
            continue

        for pattern in ENHANCED_PATTERNS:
            if pattern.search(path):
                if not file_allows(path, "shadow-fork"):
                    violations.append(path)
                break
    return violations


def validate_readme_governance_files(files):
    """Validate README governance and return violating files"""
    violations = []
    for path in files:
        if path.lower().endswith(".md") and "readme" in path.lower():
            # Skip files in ignored segments
            if any(segment in path for segment in README_IGNORE_SEGMENTS):
                continue

            # Check for pragma first
            if file_allows(path, "readme-governance"):
                continue

            # Enhanced README validation - check for required sections
            try:
                with open(path, encoding="utf-8") as f:
                    content = f.read().lower()

                # Check for required sections
                has_purpose = "## purpose" in content or "### purpose" in content
                has_usage = "## usage" in content or "### usage" in content
                has_owner = "## owner" in content or "### owner" in content
                has_last_reviewed = (
                    "## last reviewed" in content or "### last reviewed" in content
                )

                # If all required sections are present, consider it valid
                if has_purpose and has_usage and has_owner and has_last_reviewed:
                    continue

            except Exception:
                pass

            violations.append(path)
    return violations


def validate_multirep_xref_files(files, *, root=".", ledger=None):
    """Return files that fail the XRef requirement (no internal links and no exception)."""
    violations = []
    root = os.path.abspath(root)
    ledger = ledger or {}

    for path in files:
        if not path.endswith(".md"):
            continue

        # Skip files in ignored segments
        if any(segment in path for segment in README_IGNORE_SEGMENTS):
            continue

        # Get relative path for ledger lookup
        try:
            relpath = os.path.relpath(path, root)
        except ValueError:
            # Path is not relative to root, skip
            continue

        # Already OK if at least one outbound internal xref exists
        if _has_internal_xref(relpath, root):
            continue

        # Else allow via pragma or ledger
        try:
            with open(path, encoding="utf-8") as f:
                txt = f.read()
        except Exception:
            txt = ""

        if _pragma_allows(txt, "xref-missing") or _ledger_allows(
            ledger, relpath, "xref-missing"
        ):
            continue

        violations.append(path)

    return violations


def build_report(files, *, root=".", ledger=None):
    """Build comprehensive validator report with schema 1.1.0"""
    report = {
        "schema_version": "1.1.0",
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "categories": {},
        "impacted_files": {},
        "counters": {},
    }

    # Prefer diff-based archive rule when diff range is available (only-changed mode)
    diff_range = os.getenv("VALIDATOR_DIFF_RANGE")
    if diff_range:
        arch_msgs = validate_archive_immutable(Path(root), strict_fail=ARCHIVE_FAIL)
        # Translate message lists into file impacts (best-effort: extract quoted path)
        arch = []
        for bucket in arch_msgs.get("fail", []) + arch_msgs.get("warn", []):
            # find last quoted path
            m = re.search(r"'([^']+)'", bucket)
            if m:
                arch.append(m.group(1))
    else:
        arch = validate_archive_immutability_files(files)
    shad = validate_shadow_forks_files(files)
    read = validate_readme_governance_files(files)
    mult = validate_multirep_xref_files(files, root=root, ledger=ledger)

    # References check: broken [link](file.md) are counted as violations; backticked `.md` are warnings only
    references_violation_count = 0
    references_impacted: list[str] = []
    references_alias_hits_total = 0
    root_abs_for_refs = os.path.abspath(root)
    # For reference checks, prefer changed markdown set if available, else all markdown
    md_files_for_refs: list[str] = [p for p in files if p.endswith(".md")]
    for path in md_files_for_refs:
        try:
            text = Path(path).read_text(encoding="utf-8", errors="ignore")
        except Exception:
            # Treat unreadable files as no references checked; archive/other rules may still report
            continue
        errs, warns, alias_hits = check_markdown_references(
            Path(path), text, enforce_lowercase=("--ci" in sys.argv)
        )
        if errs:
            references_violation_count += len(errs)
            references_impacted.append(_posix_rel(path, root_abs_for_refs))
        references_alias_hits_total += alias_hits

    # Deterministic output ordering
    report["categories"] = {
        "archive": {"violations": len(arch), "fail": ARCHIVE_FAIL},
        "shadow_fork": {"violations": len(shad), "fail": SHADOW_FAIL},
        "readme": {"violations": len(read), "fail": README_FAIL},
        "multirep": {"violations": len(mult), "fail": MULTIREP_FAIL},
        "references": {
            "violations": references_violation_count,
            "fail": REFERENCES_FAIL,
        },
    }
    # Normalize paths to repo-relative POSIX for consistent reporting
    root_abs = os.path.abspath(root)
    report["impacted_files"] = {
        "archive": sorted(_posix_rel(p, root_abs) for p in arch),
        "shadow_fork": sorted(_posix_rel(p, root_abs) for p in shad),
        "readme": sorted(_posix_rel(p, root_abs) for p in read),
        "multirep": sorted(_posix_rel(p, root_abs) for p in mult),
        "references": sorted(set(references_impacted)),
    }

    # Add current counters if available, then update our counters
    try:
        with open("data/validator_counters.json") as f:
            report["counters"] = json.load(f)
    except FileNotFoundError:
        report["counters"] = {}
    # Emit alias usage note once (non-breaking; useful during migrations)
    report["counters"]["references_alias_hits"] = (
        report["counters"].get("references_alias_hits", 0) + references_alias_hits_total
    )

    return report


@dataclass
class BacklogItem:
    id: str
    title: str
    icon: str
    points_raw: str
    status: str
    desc: str
    line_idx: int

    score_raw: Optional[str] = None
    score_total: Optional[float] = None
    score_obj: Optional[dict] = None

    do_next: Optional[str] = None
    acceptance: Optional[str] = None
    est_hours: Optional[float] = None

    lessons_applied: Optional[str] = None
    reference_cards: Optional[str] = None
    prd_link: Optional[str] = None

    # derived
    points: Optional[float] = None
    reasons_fail: list[str] = field(default_factory=list)
    reasons_warn: list[str] = field(default_factory=list)


# --- B-100: Multi-representation validation helpers ---
def _has_summary_rep(item: BacklogItem) -> bool:
    """Check if item has summary representation (score_obj or score_total)."""
    return bool(
        (item.score_obj and isinstance(item.score_obj, dict))
        or (item.score_total is not None)
    )


def _has_refs_rep(item: BacklogItem) -> bool:
    """Check if item has cross-reference representation."""
    return bool(item.lessons_applied or item.reference_cards)


def _representation_count(item: BacklogItem) -> int:
    """Count representations: raw (1) + summary (0/1) + refs (0/1)."""
    raw = 1  # the backlog row itself (always present if parsed)
    summary = 1 if _has_summary_rep(item) else 0
    refs = 1 if _has_refs_rep(item) else 0
    return raw + summary + refs


# --- B-102: Cross-reference validation helpers ---
def _parse_json_array_literal(s: Optional[str]) -> list[str]:
    """Parse JSON array from lessons_applied or reference_cards."""
    if not s:
        return []
    try:
        return json.loads(s)
    except Exception:
        # try to coerce trailing commas or single quotes
        j = s.replace("'", '"').replace(",]", "]").replace(", ]", "]")
        try:
            return json.loads(j)
        except Exception:
            return []


def _xref_targets(item: BacklogItem) -> list[str]:
    """Extract all cross-reference targets from item."""
    x = []
    x += _parse_json_array_literal(item.lessons_applied)
    x += _parse_json_array_literal(item.reference_cards)
    # Normalize whitespace
    return [t.strip() for t in x if isinstance(t, str) and t.strip()]


def _target_exists_in_repo(target: str) -> bool:
    """
    Check if cross-reference target exists in repo.

    Supports:
    - "file#anchor" (e.g., '500_reference-cards.md#rag-lessons-from-jerry')
    - bare file paths
    - http(s) links (treated as existing)
    """
    if target.startswith("http://") or target.startswith("https://"):
        return True

    # split anchor
    file_part = target.split("#", 1)[0]
    if not file_part:
        return False

    p = Path(file_part)
    if not p.exists():
        return False

    if "#" not in target:
        return True

    # Anchor check (best-effort): ensure anchor text appears in file
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
        anchor = target.split("#", 1)[1].strip().lower()
        return (("#" + anchor) in text.lower()) or (anchor in text.lower())
    except Exception:
        return False


# =========================
# Backlog compliance validator
# =========================


def _safe_float(x: str) -> Optional[float]:
    """Safely convert string to float, handling edge cases."""
    try:
        return float(x)
    except Exception:
        m = re.search(r"[\d.]+", x or "")
        return float(m.group(0)) if m else None


def _parse_score_map(s: str) -> Optional[dict]:
    """
    Convert a JS-ish map to JSON and parse.
    Requires keys: bv, tc, rr, le, lessons, effort, deps
    """
    if not s:
        return None
    # Put quotes around unquoted keys
    j = re.sub(r"(\w+)\s*:", r'"\1":', s)
    # Ensure single quotes to double
    j = j.replace("'", '"')
    try:
        obj = json.loads(j)
        if not isinstance(obj, dict):
            return None
        return obj
    except Exception:
        return None


def _find_region(lines: list[str], start_idx: int) -> str:
    """
    Capture metadata lines until next table row or blank line break.
    """
    buff = []
    i = start_idx + 1
    while i < len(lines):
        if ROW_RE.match(lines[i]) or (lines[i].strip() == "" and buff):
            break
        buff.append(lines[i])
        i += 1
    return "\n".join(buff)


def parse_backlog(path: Path) -> list[BacklogItem]:
    """Parse backlog file and extract items with metadata."""
    lines = path.read_text(encoding="utf-8").splitlines()
    items: list[BacklogItem] = []
    i = 0
    while i < len(lines):
        m = ROW_RE.match(lines[i])
        if not m:
            i += 1
            continue

        item = BacklogItem(
            id=m.group(1).strip(),
            title=m.group(2).strip(),
            icon=m.group(3).strip(),
            points_raw=m.group(4).strip(),
            status=m.group(5).strip().lower(),
            desc=m.group(6).strip()
            + " | "
            + m.group(7).strip()
            + " | "
            + m.group(8).strip(),  # Combine last 3 columns
            line_idx=i + 1,
        )
        item.points = _safe_float(item.points_raw)

        region = _find_region(lines, i)

        # score + total
        ms = SCORE_RE.search(region)
        if ms:
            item.score_raw = ms.group(1)
            if item.score_raw:  # Add null check
                item.score_obj = _parse_score_map(item.score_raw)

        mt = SCORE_TOTAL_RE.search(region)
        if mt:
            item.score_total = _safe_float(mt.group(1))

        # working agreements
        md = DO_NEXT_RE.search(region)
        item.do_next = md.group(1).strip() if md else None
        ma = ACCEPTANCE_RE.search(region)
        item.acceptance = ma.group(1).strip() if ma else None
        me = EST_HOURS_RE.search(region)
        item.est_hours = _safe_float(me.group(1)) if me else None

        # cross refs + PRD
        ml = LESSONS_APPLIED_RE.search(region)
        item.lessons_applied = ml.group(1).strip() if ml else None
        mr = REFERENCE_CARDS_RE.search(region)
        item.reference_cards = mr.group(1).strip() if mr else None

        # scan desc + region for PRD
        mp = PRD_LINK_RE.search(item.desc) or PRD_LINK_RE.search(region)
        item.prd_link = mp.group(1) if mp else None

        items.append(item)

        # advance to next row or break at blank
        i += 1
    return items


def check_item(item: BacklogItem) -> None:
    """Apply validation rules to a backlog item."""
    # --- FAIL: score must exist and parse
    if item.score_obj is None:
        item.reasons_fail.append("MISSING_SCORE_OR_BAD_FORMAT")
    else:
        missing = REQUIRED_SCORE_KEYS - set(item.score_obj.keys())
        if missing:
            item.reasons_fail.append(f"SCORE_MISSING_KEYS:{','.join(sorted(missing))}")
        else:
            # type checks
            try:
                for k in ["bv", "tc", "rr", "le", "lessons", "effort"]:
                    _ = int(item.score_obj[k])
                if not isinstance(item.score_obj["deps"], list):
                    item.reasons_fail.append("SCORE_DEPS_NOT_LIST")
            except Exception:
                item.reasons_fail.append("SCORE_VALUES_INVALID")

    # --- FAIL: lessons factor required
    if not (item.score_obj and "lessons" in item.score_obj):
        item.reasons_fail.append("MISSING_LESSONS_FACTOR")

    # --- FAIL: PRD skip rule
    # PRD required unless (points < 5 AND score_total >= 3.0)
    if item.points is not None and item.score_total is not None:
        skip = (item.points < 5) and (item.score_total >= 3.0)
        if not skip and not item.prd_link:
            item.reasons_fail.append("PRD_REQUIRED_MISSING_LINK")
    else:
        # If we can't compute the rule, mark format invalid
        item.reasons_fail.append("MISSING_POINTS_OR_SCORE_TOTAL")

    # --- WARN: TODO requires working agreements
    if item.status in {"todo", "to-do"}:
        if item.do_next is None:
            item.reasons_warn.append("MISSING_DO_NEXT")
        if item.acceptance is None:
            item.reasons_warn.append("MISSING_ACCEPTANCE")
        if item.est_hours is None:
            item.reasons_warn.append("MISSING_EST_HOURS")

    # --- WARN: Cross-reference pointers encouraged
    if item.score_obj is not None:
        if item.lessons_applied is None:
            item.reasons_warn.append("MISSING_LESSONS_APPLIED_POINTER")
        if item.reference_cards is None:
            item.reasons_warn.append("MISSING_REFERENCE_CARDS_POINTER")

    # --- WARN: DONE items should be moved out of active table (heuristic)
    if item.status in {"done", "✅ done", "complete", "completed"}:
        item.reasons_warn.append("DONE_ITEM_IN_ACTIVE_TABLE")

    # --- B-100: Multi-representation requirement (raw + summary and/or refs)
    if REQUIRE_MULTI_REP:
        if _representation_count(item) < 2:
            item.reasons_fail.append("INSUFFICIENT_REPRESENTATIONS(<2)")
        else:
            # nudge if exactly 2 (encourage best practice 3), but not a fail
            if _representation_count(item) == 2:
                item.reasons_warn.append("CONSIDER_ADDING_THIRD_REPRESENTATION")

    # --- B-102: Cross-reference enforcement (at least one)
    if REQUIRE_XREF:
        if not _has_refs_rep(item):
            item.reasons_fail.append(
                "MISSING_CROSS_REFERENCE(lessons_applied_or_reference_cards)"
            )
        else:
            # stale link detection (best-effort)
            targets = _xref_targets(item)
            stale = []
            for t in targets:
                if not _target_exists_in_repo(t):
                    stale.append(t)
            if stale:
                msg = "STALE_CROSS_REFERENCE:" + ",".join(stale)
                if STRICT_STALE_XREF:
                    item.reasons_fail.append(msg)
                else:
                    item.reasons_warn.append(msg)


def find_shadow_fork_variants(root: Path) -> list[tuple[str, str]]:
    """
    Returns list of (path, rule_code) tuples for files that look like shadow forks.
    rule_code is 'SHADOW_FORK_FILE'.
    """
    offenders = []
    for p in root.rglob("*.py"):
        s = str(p.as_posix())
        if ARCHIVE_ALLOWLIST.search(s):
            continue
        # ignore virtual environments and build/cache paths
        if any(seg in s for seg in IGNORED_DIR_SEGMENTS):
            continue

        # Use repo-relative path for pattern matching
        try:
            rel = p.relative_to(root).as_posix()
        except ValueError:
            # File is outside repo root, skip
            continue

        for pat in ENHANCED_PATTERNS:
            if pat.match(rel) and not file_allows(p, "shadow-fork"):
                offenders.append((s, "SHADOW_FORK_FILE"))
                break
    return offenders


def validate_shadow_forks(root: Path, strict_fail: bool) -> dict:
    """
    strict_fail controls FAIL vs WARN (flip after migration window).
    Returns {'fail': [...], 'warn': [...]} message lists.
    """
    results = {"fail": [], "warn": []}
    offenders = find_shadow_fork_variants(root)
    if not offenders:
        return results

    for path, rule in offenders:
        msg = (
            f"{rule}: Disallowed duplicate variant filename '{path}'. "
            f"Refactor in-place or merge into canonical module; archive duplicates under 600_archives/."
        )
        if strict_fail:
            results["fail"].append(msg)
        else:
            results["warn"].append(msg)
    return results


def _git_changed_with_status(diff_range: Optional[str]) -> list[tuple[str, str]]:
    """
    Returns a list of (status, path) where status in {'A','M','R','D','C','T'}.
    Falls back to porcelain for local runs. Includes untracked as 'A'.
    """
    try:
        if diff_range:
            out = subprocess.check_output(
                ["git", "diff", "--name-status", diff_range],
                text=True,
                stderr=subprocess.DEVNULL,
            )
            pairs = []
            for line in out.splitlines():
                if not line.strip():
                    continue
                parts = line.split("\t")
                status = parts[0]
                if status.startswith("R") and len(parts) == 3:
                    # rename: old, new
                    pairs.append(("R", parts[2]))
                elif len(parts) >= 2:
                    pairs.append((status[0], parts[1]))
            # include untracked
            untracked = subprocess.check_output(
                ["git", "ls-files", "--others", "--exclude-standard"],
                text=True,
                stderr=subprocess.DEVNULL,
            ).splitlines()
            pairs.extend([("A", p) for p in untracked])
            return pairs
        else:
            # local fallback: porcelain
            out = subprocess.check_output(
                ["git", "status", "--porcelain"], text=True, stderr=subprocess.DEVNULL
            )
            pairs = []
            for line in out.splitlines():
                if not line.strip():
                    continue
                status = line[:2].strip() or "M"
                path = line[3:]
                # Porcelain codes: ?? = untracked (treat as A)
                if status == "??":
                    pairs.append(("A", path))
                else:
                    pairs.append((status[0], path))
            return pairs
    except Exception:
        # no git context; safest is empty (no enforcement)
        return []


def validate_readme_governance(root: Path, strict_fail: bool) -> dict:
    """
    Enforce README governance rules:
    - Only standard names (README.md, README-dev.md)
    - Max 2 README files per directory
    - Required sections present
    - No near-duplicates
    - Not stale for touched directories
    - No bracketed placeholders that look like link refs
    """
    results = {"fail": [], "warn": []}

    # Find all README files (exclude third-party directories)
    readme_files = []
    for p in root.rglob("README*"):
        if p.is_file():
            # Skip third-party and archives directories
            path_str = str(p)
            if any(
                exclude in path_str
                for exclude in [
                    "/.venv/",
                    "/venv/",
                    "/node_modules/",
                    "/site-packages/",
                    "/.git/",
                    "/.pytest_cache/",
                    "/.ruff_cache/",
                    "/__pycache__/",
                    "/600_archives/",
                ]
            ):
                continue
            readme_files.append(p)

    # Check for nonstandard names
    for readme_file in readme_files:
        if readme_file.name not in ["README.md", "README-dev.md"]:
            msg = f"README_GOVERNANCE: Nonstandard README name '{readme_file.name}' in {readme_file.parent}. Use only README.md or README-dev.md."
            if strict_fail:
                results["fail"].append(msg)
            else:
                results["warn"].append(msg)

    # Check directory limits (max 2 README files per directory)
    dir_readme_counts = {}
    for readme_file in readme_files:
        if readme_file.name in ["README.md", "README-dev.md"]:
            dir_path = str(readme_file.parent)
            dir_readme_counts[dir_path] = dir_readme_counts.get(dir_path, 0) + 1

    for dir_path, count in dir_readme_counts.items():
        if count > 2:
            msg = f"README_GOVERNANCE: Directory '{dir_path}' has {count} README files (max 2 allowed)."
            if strict_fail:
                results["fail"].append(msg)
            else:
                results["warn"].append(msg)

    # Check required sections for README.md files and placeholder patterns
    placeholder_line = re.compile(r"^\s*\[[A-Za-z][^\]]+\]\s*$")
    placeholder_list_item = re.compile(r"^\s*-\s*\[[A-Za-z][^\]]+\]\s*$")
    for readme_file in readme_files:
        if readme_file.name == "README.md" or readme_file.name == "README-dev.md":
            try:
                content = readme_file.read_text(encoding="utf-8", errors="ignore")

                # Placeholder detection
                for line in content.splitlines():
                    if placeholder_line.match(line) or placeholder_list_item.match(
                        line
                    ):
                        msg = f"README_GOVERNANCE: Bracketed placeholder detected in '{readme_file}'. Replace with plain text (no square brackets)."
                        if strict_fail:
                            results["fail"].append(msg)
                        else:
                            results["warn"].append(msg)

                # Check for required sections (case-insensitive)
                required_sections = [
                    "purpose",
                    "usage",
                    "integration",
                    "owner",
                    "last reviewed",
                ]
                content_lower = content.lower()

                missing_sections = []
                for section in required_sections:
                    if section not in content_lower:
                        missing_sections.append(section)

                if missing_sections:
                    msg = f"README_GOVERNANCE: {readme_file} missing required sections: {', '.join(missing_sections)}"
                    if strict_fail:
                        results["fail"].append(msg)
                    else:
                        results["warn"].append(msg)

                # Check minimum length (80 words unless pointer stub)
                word_count = len(content.split())
                has_repo_links = (
                    "400_guides/" in content
                    or "500_reference-cards.md" in content
                    or "401_consensus-log.md" in content
                )

                if word_count < 80 and not has_repo_links:
                    msg = f"README_GOVERNANCE: {readme_file} too short ({word_count} words). Minimum 80 words unless pointer stub."
                    results["warn"].append(msg)

            except Exception as e:
                msg = (
                    f"README_GOVERNANCE: Could not validate README '{readme_file}': {e}"
                )
                results["warn"].append(msg)

    # Check for root README.md
    root_readme = root / "README.md"
    if not root_readme.exists():
        msg = "README_GOVERNANCE: Root README.md missing. Root must have README.md."
        if strict_fail:
            results["fail"].append(msg)
        else:
            results["warn"].append(msg)
    elif root_readme.stat().st_size == 0:
        msg = "README_GOVERNANCE: Root README.md is empty."
        if strict_fail:
            results["fail"].append(msg)
        else:
            results["warn"].append(msg)

    return results


def validate_archive_immutable(root: Path, strict_fail: bool) -> dict:
    """
    Enforce: Existing files under 600_archives/ cannot be modified/renamed/deleted.
    Allowed: new files added under 600_archives/, notes under 600_archives/NOTES/.
    """
    results = {"fail": [], "warn": []}
    diff_range = os.getenv("VALIDATOR_DIFF_RANGE")
    changed = _git_changed_with_status(diff_range)
    if not changed:
        # Non-fatal: we couldn't compute changes; emit a gentle WARN so CI can surface it
        results["warn"].append(
            "ARCHIVE_IMMUTABLE: Unable to detect changed files (no git context)."
        )
        return results

    for status, path in changed:
        # normalize posix
        rel = Path(path).as_posix()
        if not rel.startswith(ARCHIVE_ROOT):
            continue
        # Allow new additions (A) anywhere under 600_archives/
        if status == "A":
            continue
        # Disallow any changes to existing archives (M,R,D,etc.), except notes folder
        if rel.startswith("600_archives/NOTES/"):
            # NOTES are additive files; modifications are allowed since they are living append-only notes
            # If you want NOTES to be immutable too, drop this branch.
            continue

        msg = (
            f"ARCHIVE_IMMUTABLE: Disallowed change '{status}' to archived file '{rel}'. "
            f"Archives are immutable. Add a new amendment file in 600_archives/NOTES/ instead."
        )
        if strict_fail:
            results["fail"].append(msg)
        else:
            results["warn"].append(msg)

    return results


def validate_backlog(path: str = "000_core/000_backlog.md") -> tuple[int, str, dict]:
    """
    Validate backlog file for compliance with Phase 0 requirements.

    Returns (exit_code, human_report, json_summary)
    exit_code: 0 OK, 2 FAIL, 1 ERROR
    """
    try:
        p = Path(path)
        if not p.exists():
            return (
                ERROR,
                f"ERROR: Backlog file not found: {path}",
                {"error": "FILE_NOT_FOUND", "path": path},
            )

        items = parse_backlog(p)
        if not items:
            return (
                ERROR,
                "ERROR: No backlog rows parsed. Check table format.",
                {"error": "NO_ROWS"},
            )

        fail_count, warn_count, pass_count = 0, 0, 0
        report_lines: list[str] = []
        json_items: list[dict] = []

        report_lines.append("Backlog Compliance Report")
        report_lines.append("=" * 25)
        report_lines.append("")

        for it in items:
            check_item(it)

            status = "PASS"
            if it.reasons_fail:
                status = "FAIL"
                fail_count += 1
            elif it.reasons_warn:
                status = "WARN"
                warn_count += 1
            else:
                pass_count += 1

            report_lines.append(f"Item {it.id} — {status}")
            if it.reasons_fail:
                for r in it.reasons_fail:
                    report_lines.append(f"  FAIL: {r}")
            if it.reasons_warn:
                for r in it.reasons_warn:
                    report_lines.append(f"  WARN: {r}")
            report_lines.append("")

            json_items.append(
                {
                    "id": it.id,
                    "status": status,
                    "reasons": it.reasons_fail + it.reasons_warn,
                    "line": it.line_idx,
                }
            )

        report_lines.append(
            f"Summary: {fail_count} FAIL, {warn_count} WARN, {pass_count} PASS"
        )

        exit_code = FAIL if fail_count > 0 else OK
        summary = {
            "summary": {"fail": fail_count, "warn": warn_count, "pass": pass_count},
            "items": json_items,
        }
        return exit_code, "\n".join(report_lines), summary

    except Exception as e:
        return ERROR, f"ERROR: {e}", {"error": "EXCEPTION", "message": str(e)}


class DocCoherenceValidator:
    def __init__(
        self,
        dry_run: bool = True,
        only_changed: bool = False,
        max_workers: Optional[int] = None,
        cache_ttl: int = 300,
        emit_json: Optional[str] = None,
        safe_fix: bool = False,
        rules_path: Optional[str] = "config/validator_rules.json",
        strict_anchors: bool = False,
        tab_width: int = 4,
        wrap_long_lines: bool = False,
        enable_few_shot: bool = True,
        base_commit: Optional[str] = None,
        head_commit: Optional[str] = None,
    ):
        self.dry_run = dry_run
        self.only_changed = only_changed
        self.max_workers = max_workers or min(8, multiprocessing.cpu_count() + 2)
        self.cache_ttl = cache_ttl
        self.emit_json_path = emit_json
        self.safe_fix = safe_fix
        self.rules = self._load_rules(rules_path)
        self.strict_anchors = strict_anchors
        self.tab_width = max(1, tab_width)
        self.wrap_long_lines = wrap_long_lines
        self.enable_few_shot = enable_few_shot and FEW_SHOT_AVAILABLE
        self.base_commit = base_commit or os.getenv("DIFF_BASE_SHA")
        self.head_commit = head_commit or os.getenv("GITHUB_SHA", "HEAD")

        # Initialize few-shot integration if available
        self.few_shot_loader = None
        self.few_shot_patterns = []
        if self.enable_few_shot:
            try:
                self.few_shot_loader = FewShotExampleLoader()
                examples = self.few_shot_loader.load_examples_by_category(
                    "documentation_coherence"
                )
                self.few_shot_patterns = self.few_shot_loader.extract_patterns(examples)
                print(
                    f"✅ Loaded {len(self.few_shot_patterns)} few-shot patterns for documentation coherence"
                )
            except Exception as e:
                print(f"⚠️  Failed to load few-shot patterns: {e}")
                self.enable_few_shot = False

        # Cache directory
        self.cache_dir = Path(".cache/doc_validator")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Exclude patterns - normalize to POSIX and split into dir prefixes vs exact files
        self.exclude_patterns = [
            "venv/",
            "node_modules/",
            "docs/legacy/",
            "__pycache__/",
            ".git/",
            "600_archives/",
            # File-level exclusions:
            "999_repo-maintenance.md",
            "REPO_MAINTENANCE_SUMMARY.md",
            "DOCUMENTATION_UPDATE_SUMMARY.md",
            "RESEARCH_INTEGRATION_QUICK_START.md",
            "RESEARCH_DISPERSAL_SUMMARY.md",
            "CURSOR_NATIVE_AI_STRATEGY.md",
            "MODEL_COMPATIBILITY_ANALYSIS.md",
            "cursor_native_ai_assessment.md",
            "LM_STUDIO_SETUP.md",
            "workflow_improvement_research.md",
        ]

        # Normalize to POSIX and split into dir prefixes vs exact files
        self._skip_dir_prefixes = []
        self._skip_files_exact = set()
        for pat in self.exclude_patterns:
            posix = pat.replace("\\", "/").lstrip("./")
            if posix.endswith("/"):
                self._skip_dir_prefixes.append(posix)
            else:
                self._skip_files_exact.add(posix)

        # Priority file patterns
        self.priority_files = {
            "memory_context": ["100_memory/100_cursor-memory-context.md"],
            "backlog": ["000_core/000_backlog.md"],
            "system_overview": ["400_guides/400_system-overview.md"],
            "project_overview": ["400_guides/400_project-overview.md"],
        }

        self.changes_made = []
        self.errors = []
        self.warnings = []
        self.validation_results = {}

    def _load_rules(self, rules_path: Optional[str]) -> dict:
        """Load validation rules from JSON file."""
        if rules_path and Path(rules_path).exists():
            try:
                with open(rules_path) as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _is_git_repo(self) -> bool:
        """Check if current directory is a git repository."""
        try:
            r = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
            )
            return r.returncode == 0 and r.stdout.strip() == "true"
        except Exception:
            return False

    def _git(self, *args: str, timeout: int = 10) -> subprocess.CompletedProcess:
        """Run git command with timeout."""
        return subprocess.run(
            ["git", *args], capture_output=True, text=True, timeout=timeout, check=False
        )

    def get_cache_key(self, file_path: Path) -> str:
        """Generate cache key for a file using mtime and size."""
        try:
            st = file_path.stat()
            base = f"{file_path.as_posix()}|{st.st_mtime_ns}|{st.st_size}"
        except FileNotFoundError:
            base = f"{file_path.as_posix()}|missing"
        return hashlib.blake2s(base.encode("utf-8"), digest_size=16).hexdigest()

    def load_cached_result(self, file_path: Path) -> Optional[dict]:
        """Load cached validation result if available and valid."""
        cache_key = self.get_cache_key(file_path)
        cache_file = self.cache_dir / f"{cache_key}.pkl"

        if cache_file.exists():
            try:
                with open(cache_file, "rb") as f:
                    cached_data = pickle.load(f)

                # Check if cache is still valid
                if time.time() - cached_data.get("timestamp", 0) < self.cache_ttl:
                    return cached_data.get("result")
            except Exception:
                pass

        return None

    def save_cached_result(self, file_path: Path, result: dict):
        """Save validation result to cache."""
        cache_key = self.get_cache_key(file_path)
        cache_file = self.cache_dir / f"{cache_key}.pkl"

        try:
            with open(cache_file, "wb") as f:
                pickle.dump({"result": result, "timestamp": time.time()}, f)
        except Exception:
            pass

    def _should_validate_file(self, file_path: Path) -> bool:
        """Check if file should be validated (not excluded)."""
        rel = file_path.as_posix().lstrip("./")
        if not rel.endswith(".md"):
            return False
        if any(rel.startswith(prefix) for prefix in self._skip_dir_prefixes):
            return False
        return rel not in self._skip_files_exact

    def _list_tracked_markdown_with_git(self) -> list[Path]:
        """Get tracked markdown files using git ls-files."""
        try:
            r = self._git("ls-files", "*.md", timeout=8)
            if r.returncode == 0:
                files = [Path(p.strip()) for p in r.stdout.splitlines() if p.strip()]
                return [f for f in files if self._should_validate_file(f)]
        except Exception:
            pass
        return []

    def _walk_markdown_files(self) -> list[Path]:
        """Walk directory tree for markdown files with pruning."""
        files: list[Path] = []
        for root, dirs, filenames in os.walk(".", topdown=True):
            root_posix = root.replace("\\", "/").lstrip("./")

            # Prune directories aggressively
            if any(
                root_posix.startswith(prefix.rstrip("/"))
                for prefix in self._skip_dir_prefixes
            ):
                dirs[:] = []  # don't descend
                continue

            # Also prune children about to be visited
            dirs[:] = [
                d
                for d in dirs
                if not any(
                    (root_posix + "/" + d).startswith(prefix.rstrip("/"))
                    for prefix in self._skip_dir_prefixes
                )
            ]

            for name in filenames:
                if not name.endswith(".md"):
                    continue
                p = Path(root) / name
                if self._should_validate_file(p):
                    files.append(p)
        return files

    def get_changed_markdown_files(self) -> set[Path]:
        """Get only changed Markdown files using git with robust fallbacks."""
        if not self.only_changed:
            return set()

        if not self._is_git_repo():
            return set()

        # Prefer explicit base/head if available (CI/local parity)
        candidates: set[str] = set()
        if self.base_commit and self.head_commit:
            try:
                r = subprocess.run(
                    [
                        "git",
                        "diff",
                        "--name-only",
                        "-z",
                        "--diff-filter=ACMR",
                        self.base_commit,
                        self.head_commit,
                    ],
                    check=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=False,
                )
                if r.returncode == 0 and r.stdout:
                    for part in r.stdout.split(b"\x00"):
                        if part:
                            candidates.add(part.decode("utf-8", "replace"))
            except Exception:
                candidates = set()

        # Fallback to HEAD~1 and porcelain if needed
        if not candidates:
            commands = [
                ["diff", "--name-only", "HEAD~1"],
                ["diff", "--name-only", "HEAD"],
                ["diff", "--name-only", "--cached"],
            ]
            for cmd in commands:
                try:
                    r = self._git(*cmd, timeout=10)
                    if r.returncode == 0:
                        for line in r.stdout.splitlines():
                            line = line.strip()
                            if line:
                                candidates.add(line)
                except Exception:
                    pass

            try:
                r = self._git("status", "--porcelain", timeout=10)
                if r.returncode == 0:
                    for line in r.stdout.splitlines():
                        parts = line.strip().split(maxsplit=1)
                        if len(parts) == 2:
                            candidates.add(parts[1])
            except Exception:
                pass

        out: set[Path] = set()
        for c in candidates:
            if c.endswith(".md"):
                p = Path(c)
                if self._should_validate_file(p) and p.exists():
                    out.add(p)
        return out

    def _get_markdown_files(self) -> list[Path]:
        """Get all Markdown files to validate."""
        if self.only_changed:
            changed = self.get_changed_markdown_files()
            return sorted(changed, key=lambda p: p.as_posix())

        if self._is_git_repo():
            files = self._list_tracked_markdown_with_git()
            if files:
                return files

        # Fallback: walk the tree with pruning
        return self._walk_markdown_files()

    def _check_headings(self, line: str) -> Optional[int]:
        """Return heading level (1..6) if line is a Markdown ATX heading like '# Title', else None."""
        if not line or line[0] != "#":
            return None
        # Count leading '#' up to 6 and require a following space
        i = 0
        n = len(line)
        while i < n and i < 6 and line[i] == "#":
            i += 1
        if 1 <= i <= 6 and i < n and line[i] == " ":
            return i
        return None

    def validate_single_file(self, file_path: Path) -> dict:
        """Validate a single file using single-pass scanning."""
        # Check cache first
        cached_result = self.load_cached_result(file_path)
        if cached_result is not None:
            return cached_result

        try:
            text = file_path.read_text(encoding="utf-8", errors="strict")
        except UnicodeDecodeError:
            text = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            return {
                "file": str(file_path),
                "errors": [f"Could not read file: {e}"],
                "warnings": [],
                "valid": False,
            }

        errors = []
        warnings = []
        fixes = []

        lines = text.splitlines()  # preserves no trailing '\n'
        had_trailing_newline = text.endswith("\n")

        # Single pass over lines
        heading_levels = []
        any_tabs = False
        fixed_tabs = 0
        fixed_trailing = 0
        fixed_headings = 0
        fixed_long_lines = 0
        last_heading_level: Optional[int] = None
        in_code_block = False
        code_block_marker = ""

        out_lines: list[str] = []
        for i, line in enumerate(lines, 1):
            # Track code block state
            if line.startswith("```"):
                if not in_code_block:
                    in_code_block = True
                    code_block_marker = line
                elif line == code_block_marker:
                    in_code_block = False
                    code_block_marker = ""

            # --- checks ---
            if len(line) > (self.rules.get("line_length_limit", 120)):
                warnings.append(f"Line {i}: Line too long (>120 chars)")

            if "\t" in line:
                any_tabs = True

            # Trailing whitespace
            trimmed = line.rstrip(" \t")
            if trimmed != line:
                warnings.append(f"Line {i}: Trailing whitespace")
                if self.safe_fix:
                    fixed_trailing += 1

            # Heading levels (with optional auto-fix for skipped levels)
            level = self._check_headings(trimmed)
            effective_level = level
            if (
                level is not None
                and last_heading_level is not None
                and level > last_heading_level + 1
                and self.safe_fix
            ):
                # Reduce heading level to only +1 deeper than previous
                target_level = min(6, last_heading_level + 1)
                # Extract heading text after hashes and one space
                heading_text = (
                    trimmed[level + 1 :].lstrip() if len(trimmed) > level + 1 else ""
                )
                trimmed = ("#" * target_level) + " " + heading_text
                effective_level = target_level
                fixed_headings += 1
                # If not fixing, the post-pass will record the error
            if effective_level is not None:
                heading_levels.append((i, effective_level))
                last_heading_level = effective_level

            # --- fixes (optional) ---
            out_line = trimmed
            # Wrap long lines (but not in code blocks)
            if (
                self.wrap_long_lines
                and len(out_line) > 120
                and not in_code_block
                and not out_line.startswith("```")
            ):
                # Simple word-wrap at 120 chars, breaking at spaces
                words = out_line.split()
                wrapped_lines = []
                current_line = ""
                for word in words:
                    if len(current_line + " " + word) <= 120:
                        current_line += (" " + word) if current_line else word
                    else:
                        if current_line:
                            wrapped_lines.append(current_line)
                        current_line = word
                if current_line:
                    wrapped_lines.append(current_line)
                # Replace the current line with wrapped lines
                if len(wrapped_lines) > 1:
                    out_lines.extend(wrapped_lines)
                    fixed_long_lines += 1
                    continue  # Skip adding the original line

            if self.safe_fix and "\t" in out_line:
                out_line = out_line.replace("\t", " " * self.tab_width)
                fixed_tabs += 1

            out_lines.append(out_line)

        # Post-pass checks
        for idx in range(1, len(heading_levels)):
            prev_level = heading_levels[idx - 1][1]
            curr_level = heading_levels[idx][1]
            if curr_level > prev_level + 1:
                errors.append(f"Line {heading_levels[idx][0]}: Heading level skipped")

        if any_tabs:
            if self.safe_fix and fixed_tabs > 0:
                fixes.append(f"Replaced tabs with spaces on {fixed_tabs} line(s)")
            else:
                warnings.append("Contains hard tabs")

        if self.safe_fix and fixed_headings > 0:
            fixes.append(f"Fixed heading level skips on {fixed_headings} line(s)")

        if self.wrap_long_lines and fixed_long_lines > 0:
            fixes.append(f"Wrapped long lines on {fixed_long_lines} line(s)")

        # TL;DR checks
        require_tldr = self.rules.get("require_tldr", True)
        if require_tldr and not (
            TLDR_HEADING_PATTERN.search(text) or TLDR_ANCHOR_PATTERN.search(text)
        ):
            warnings.append("Missing TL;DR section")

        # At-a-glance table
        require_glance = self.rules.get("require_at_a_glance", True)
        if require_glance and not AT_A_GLANCE_HEADER_PATTERN.search(text):
            warnings.append("Missing at-a-glance table")

        # Cross-references
        for ref_type, ref_target in CROSS_REFERENCE_PATTERN.findall(text):
            if ref_type == "MODULE_REFERENCE":
                # Strip whitespace from reference target
                ref_target = ref_target.strip()
                # Check both relative to file dir and repo root
                p1 = (file_path.parent / ref_target).resolve()
                p2 = Path(ref_target).resolve()
                if not p1.exists() and not p2.exists():
                    errors.append(f"Module reference not found: {ref_target}")

        # Note: legacy backtick checks removed; handled by check_markdown_references()

        # Backlog references: reserved for future validation (removed no-op loop)

        # Strict anchor mode: detect duplicate ids
        if self.strict_anchors:
            ids = [m.group(1) for m in HTML_ANCHOR_PATTERN.finditer(text)]
            ids += [m.group(1) for m in MARKDOWN_ANCHOR_PATTERN.finditer(text)]
            if len(ids) != len(set(ids)):
                errors.append("Duplicate anchor IDs detected")

        # Apply safe fixes if requested
        if self.safe_fix or self.wrap_long_lines:
            if fixed_trailing > 0:
                fixes.append(f"Trimmed trailing whitespace on {fixed_trailing} line(s)")
            new_text = "\n".join(out_lines) + ("\n" if had_trailing_newline else "")
            if new_text != text and not self.dry_run:
                try:
                    file_path.write_text(new_text, encoding="utf-8")
                    self.changes_made.append(str(file_path))
                except Exception as e:
                    warnings.append(f"Failed to write safe fixes: {e}")

        # Apply few-shot enhanced validation if enabled
        few_shot_results = {}
        if self.enable_few_shot and self.few_shot_patterns and self.few_shot_loader:
            try:
                few_shot_results = self.few_shot_loader.apply_patterns_to_content(
                    text, self.few_shot_patterns
                )

                # Add few-shot suggestions to warnings
                for suggestion in few_shot_results.get("validation_suggestions", []):
                    if suggestion not in warnings:
                        warnings.append(f"Few-shot suggestion: {suggestion}")

                # Add pattern confidence information
                if few_shot_results.get("matched_patterns"):
                    pattern_info = []
                    for pattern in few_shot_results["matched_patterns"]:
                        pattern_info.append(
                            f"{pattern['pattern']} (confidence: {pattern['confidence']:.2f})"
                        )
                    warnings.append(f"Matched patterns: {', '.join(pattern_info)}")

            except Exception as e:
                warnings.append(f"Few-shot validation error: {e}")

        # Reference checking (hardened): errors for broken links, warnings for backticked .md
        ref_errors, ref_warnings, _alias_hits = check_markdown_references(
            file_path, text, enforce_lowercase=("--ci" in sys.argv)
        )
        errors.extend(ref_errors)
        warnings.extend(ref_warnings)

        # Result
        result = {
            "file": str(file_path),
            "errors": errors,
            "warnings": warnings,
            "fixes": fixes,
            "valid": len(errors) == 0,
            "few_shot_results": few_shot_results if self.enable_few_shot else None,
        }

        # Cache the result
        self.save_cached_result(file_path, result)

        return result

    def validate_files_parallel(self, files: list[Path]) -> dict[Path, dict]:
        """Validate multiple files in parallel."""
        results: dict[Path, dict] = {}

        if not files:
            return results

        print(f"Validating {len(files)} files with {self.max_workers} workers...")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self.validate_single_file, file_path): file_path
                for file_path in files
            }

            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    results[file_path] = future.result()
                except Exception as e:
                    results[file_path] = {
                        "file": str(file_path),
                        "errors": [f"Validation error: {e}"],
                        "warnings": [],
                        "fixes": [],
                        "valid": False,
                    }

        return results

    def run_validation(self) -> dict:
        """Run the complete validation process."""
        start_time = time.time()

        print("Starting optimized documentation validation...")

        # Get files to validate
        markdown_files = self._get_markdown_files()

        if not markdown_files:
            return {
                "execution_time": 0.0,
                "files_checked": 0,
                "errors": [],
                "warnings": [],
                "all_valid": True,
            }

        # Validate files in parallel
        validation_results = self.validate_files_parallel(markdown_files)

        # Collect results
        all_errors = []
        all_warnings = []
        valid_files = 0

        for result in validation_results.values():
            if result["valid"]:
                valid_files += 1
            all_errors.extend(
                [f"{result['file']}: {error}" for error in result["errors"]]
            )
            all_warnings.extend(
                [f"{result['file']}: {warning}" for warning in result["warnings"]]
            )

        execution_time = time.time() - start_time

        return {
            "execution_time": execution_time,
            "files_checked": len(markdown_files),
            "valid_files": valid_files,
            "invalid_files": len(markdown_files) - valid_files,
            "errors": all_errors,
            "warnings": all_warnings,
            "changes_made": self.changes_made,
            "all_valid": len(all_errors) == 0,
        }


def main():
    parser = argparse.ArgumentParser(
        description="Optimized documentation coherence validator"
    )
    parser.add_argument("--check", choices=["backlog"], help="Specific validation mode")
    parser.add_argument(
        "--path", default="000_core/000_backlog.md", help="Path to file for validation"
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format"
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Return OK even if FAIL found (migration mode)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument(
        "--only-changed", action="store_true", help="Only validate changed files"
    )
    parser.add_argument("--workers", type=int, help="Number of worker threads")
    parser.add_argument(
        "--cache-ttl", type=int, default=300, help="Cache TTL in seconds"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--ci", action="store_true", help="CI mode - always run all checks"
    )
    parser.add_argument("--emit-json", help="Save results to JSON file")
    parser.add_argument(
        "--safe-fix",
        action="store_true",
        help="Apply safe fixes (tabs->spaces, trim trailing)",
    )
    parser.add_argument(
        "--tab-width", type=int, default=4, help="Spaces per tab when --safe-fix"
    )
    parser.add_argument(
        "--strict-anchors", action="store_true", help="Fail on duplicate anchor ids"
    )
    parser.add_argument(
        "--wrap-long-lines",
        action="store_true",
        help="Wrap lines longer than 120 chars",
    )
    parser.add_argument(
        "--no-few-shot",
        action="store_true",
        help="Disable few-shot enhanced validation",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Root directory for validation (default: current directory)",
    )
    parser.add_argument(
        "--exceptions", default=None, help="JSON ledger with validator exceptions"
    )
    parser.add_argument(
        "--base",
        default=os.getenv("DIFF_BASE_SHA"),
        help="Base commit SHA for diff context",
    )
    parser.add_argument(
        "--head",
        default=os.getenv("GITHUB_SHA", "HEAD"),
        help="Head commit SHA for diff context (defaults to GITHUB_SHA or HEAD)",
    )

    args = parser.parse_args()

    # Handle backlog validation mode
    if args.check == "backlog":
        code, text_report, json_summary = validate_backlog(args.path)
        if args.format == "json":
            print(json.dumps(json_summary, indent=2))
        else:
            print(text_report)

        if args.warn_only and code == FAIL:
            sys.exit(OK)
        sys.exit(code)

    # CI mode always runs all checks
    if args.ci:
        args.json = True

    # Load exception ledger if provided
    ledger = _load_ledger(args.exceptions)

    # Helper: return changed markdown files between base and head using robust parsing
    def _git_diff_changed_md(
        base_sha: Optional[str], head_sha: Optional[str]
    ) -> list[str]:
        if not base_sha or not head_sha:
            return []
        try:
            # Use null-delimited output; include Add/Copy/Modify/Rename (exclude deletes)
            cp = subprocess.run(
                [
                    "git",
                    "diff",
                    "--name-only",
                    "-z",
                    "--diff-filter=ACMR",
                    base_sha,
                    head_sha,
                ],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=False,
            )
            if cp.returncode != 0 or not cp.stdout:
                return []
            parts = cp.stdout.split(b"\x00")
            paths = [p.decode("utf-8", "replace") for p in parts if p]
            return [p for p in paths if p.endswith(".md")]
        except Exception:
            return []

    def _git_status_md() -> list[str]:
        # Fallback for local unstaged/staged changes when diff base isn't available
        try:
            cp = subprocess.run(
                ["git", "status", "--porcelain", "-z"],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
            if cp.returncode != 0 or not cp.stdout:
                return []
            b = cp.stdout
            out: list[str] = []
            i = 0
            n = len(b)
            while i < n:
                if i + 3 > n:
                    break
                status = b[i : i + 2]
                i += 3  # skip XY and space
                j = b.find(b"\x00", i)
                if j == -1:
                    break
                path1 = b[i:j].decode("utf-8", "replace")
                i = j + 1
                # Handle rename/copy which include a second path
                if status[:1] in (b"R", b"C"):
                    j = b.find(b"\x00", i)
                    if j == -1:
                        break
                    path2 = b[i:j].decode("utf-8", "replace")
                    i = j + 1
                    out.append(path2)
                else:
                    out.append(path1)
            return [p for p in out if p.endswith(".md")]
        except Exception:
            return []

    # Discover files to validate
    files: list[str]
    if args.only_changed:
        base_sha = args.base or os.getenv("DIFF_BASE_SHA")
        head_sha = args.head or os.getenv("GITHUB_SHA") or "HEAD"
        changed_md = _git_diff_changed_md(base_sha, head_sha)
        if not changed_md:
            changed_md = _git_status_md()
        if not changed_md:
            print("Validator: no changed Markdown files detected; exiting cleanly.")
            sys.exit(0)
        # Provide diff range to archive validator module via env (used elsewhere in this script)
        if base_sha and head_sha:
            os.environ["VALIDATOR_DIFF_RANGE"] = f"{base_sha}..{head_sha}"
        files = changed_md
    else:
        files = discover_files(args.root)

    # Build comprehensive report
    report = build_report(files, root=args.root, ledger=ledger)

    if args.json or args.emit_json:
        output = json.dumps(report, indent=2, sort_keys=True)  # Deterministic order
        if args.emit_json:
            with open(args.emit_json, "w") as f:
                f.write(output)
        else:
            print(output)
    else:
        print("\nValidation completed")
        print(f"Files checked: {len(files)}")
        for cat, info in report["categories"].items():
            fail_flag = "✅" if info.get("fail") else "❌"
            print(f"{cat}: {info.get('violations', 0)} violations {fail_flag}")

    # Determine exit code based on FAIL mode violations
    exit_code = 0
    for info in report["categories"].values():
        if info["fail"] and info["violations"] > 0:
            exit_code = 2
            break

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
