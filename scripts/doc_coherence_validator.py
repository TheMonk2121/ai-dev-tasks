#!/usr/bin/env python3
"""
Optimized Documentation Coherence Validation System

Enhanced version with parallel processing, only-changed mode, and caching.
Target: 50% performance improvement (0.80s → <0.40s)

Usage: python scripts/optimized_doc_coherence_validator.py [--dry-run] [--only-changed] [--workers N] [--json]
"""

import argparse
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
from typing import Dict, List, Optional, Set, Tuple

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
BACKLOG_REFERENCE_PATTERN = re.compile(r"B‑\d+")
TLDR_ANCHOR_PATTERN = re.compile(r'<a\s+id="tldr"\s*>\s*</a>|<a\s+id="tldr"\s*>|\{#tldr\}', re.IGNORECASE)
TLDR_HEADING_PATTERN = re.compile(r"^##\s+🔎\s+TL;DR\s*.*$", re.MULTILINE)
AT_A_GLANCE_HEADER_PATTERN = re.compile(
    r"^\|\s*what this file is\s*\|\s*read when\s*\|\s*do next\s*\|\s*$", re.MULTILINE
)
HTML_ANCHOR_PATTERN = re.compile(r'<a\s+id="([^"]+)"\s*>', re.IGNORECASE)
MARKDOWN_ANCHOR_PATTERN = re.compile(r"\{#([^}]+)\}", re.IGNORECASE)

# Backlog compliance validator patterns
ROW_RE = re.compile(
    r"^\|\s*(B‑\d{3})\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|"
)
SCORE_RE = re.compile(r"<!--\s*score:\s*(\{.*?\})\s*-->", re.DOTALL | re.IGNORECASE)
SCORE_TOTAL_RE = re.compile(r"<!--\s*score_total:\s*([0-9]+(?:\.[0-9]+)?)\s*-->", re.IGNORECASE)
DO_NEXT_RE = re.compile(r"<!--\s*do_next:\s*(.*?)\s*-->", re.IGNORECASE)
ACCEPTANCE_RE = re.compile(r"<!--\s*acceptance:\s*(.*?)\s*-->", re.IGNORECASE)
EST_HOURS_RE = re.compile(r"<!--\s*est_hours:\s*([0-9]+(?:\.[0-9]+)?)\s*-->", re.IGNORECASE)
LESSONS_APPLIED_RE = re.compile(r"<!--\s*lessons_applied:\s*(\[.*?\])\s*-->", re.DOTALL | re.IGNORECASE)
REFERENCE_CARDS_RE = re.compile(r"<!--\s*reference_cards:\s*(\[.*?\])\s*-->", re.DOTALL | re.IGNORECASE)
PRD_LINK_RE = re.compile(r"\(?(?:PRD|prd)\s*:\s*([^) \t]+)\)?")

# Exit codes for backlog validator
OK, FAIL, ERROR = 0, 2, 1

# Required score keys for backlog validation
REQUIRED_SCORE_KEYS = {"bv", "tc", "rr", "le", "lessons", "effort", "deps"}

# Environment flags for B-100 and B-102 validation
REQUIRE_MULTI_REP = os.getenv("VALIDATOR_REQUIRE_MULTI_REP", "1") == "1"
REQUIRE_XREF = os.getenv("VALIDATOR_REQUIRE_XREF", "1") == "1"
STRICT_STALE_XREF = os.getenv("VALIDATOR_STRICT_STALE_XREF", "0") == "1"


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
    score_obj: Optional[Dict] = None

    do_next: Optional[str] = None
    acceptance: Optional[str] = None
    est_hours: Optional[float] = None

    lessons_applied: Optional[str] = None
    reference_cards: Optional[str] = None
    prd_link: Optional[str] = None

    # derived
    points: Optional[float] = None
    reasons_fail: List[str] = field(default_factory=list)
    reasons_warn: List[str] = field(default_factory=list)


# --- B-100: Multi-representation validation helpers ---
def _has_summary_rep(item: BacklogItem) -> bool:
    """Check if item has summary representation (score_obj or score_total)."""
    if item.score_obj and isinstance(item.score_obj, dict):
        return True
    if item.score_total is not None:
        return True
    return False


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
def _parse_json_array_literal(s: Optional[str]) -> List[str]:
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


def _xref_targets(item: BacklogItem) -> List[str]:
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


def _parse_score_map(s: str) -> Optional[Dict]:
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


def _find_region(lines: List[str], start_idx: int) -> str:
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


def parse_backlog(path: Path) -> List[BacklogItem]:
    """Parse backlog file and extract items with metadata."""
    lines = path.read_text(encoding="utf-8").splitlines()
    items: List[BacklogItem] = []
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
            desc=m.group(6).strip() + " | " + m.group(7).strip() + " | " + m.group(8).strip(),  # Combine last 3 columns
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
            item.reasons_fail.append("MISSING_CROSS_REFERENCE(lessons_applied_or_reference_cards)")
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


def validate_backlog(path: str = "000_core/000_backlog.md") -> Tuple[int, str, dict]:
    """
    Validate backlog file for compliance with Phase 0 requirements.

    Returns (exit_code, human_report, json_summary)
    exit_code: 0 OK, 2 FAIL, 1 ERROR
    """
    try:
        p = Path(path)
        if not p.exists():
            return ERROR, f"ERROR: Backlog file not found: {path}", {"error": "FILE_NOT_FOUND", "path": path}

        items = parse_backlog(p)
        if not items:
            return ERROR, "ERROR: No backlog rows parsed. Check table format.", {"error": "NO_ROWS"}

        fail_count, warn_count, pass_count = 0, 0, 0
        report_lines: List[str] = []
        json_items: List[Dict] = []

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
                {"id": it.id, "status": status, "reasons": it.reasons_fail + it.reasons_warn, "line": it.line_idx}
            )

        report_lines.append(f"Summary: {fail_count} FAIL, {warn_count} WARN, {pass_count} PASS")

        exit_code = FAIL if fail_count > 0 else OK
        summary = {"summary": {"fail": fail_count, "warn": warn_count, "pass": pass_count}, "items": json_items}
        return exit_code, "\n".join(report_lines), summary

    except Exception as e:
        return ERROR, f"ERROR: {e}", {"error": "EXCEPTION", "message": str(e)}


class OptimizedDocCoherenceValidator:
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

        # Initialize few-shot integration if available
        self.few_shot_loader = None
        self.few_shot_patterns = []
        if self.enable_few_shot:
            try:
                self.few_shot_loader = FewShotExampleLoader()
                examples = self.few_shot_loader.load_examples_by_category("documentation_coherence")
                self.few_shot_patterns = self.few_shot_loader.extract_patterns(examples)
                print(f"✅ Loaded {len(self.few_shot_patterns)} few-shot patterns for documentation coherence")
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

    def _load_rules(self, rules_path: Optional[str]) -> Dict:
        """Load validation rules from JSON file."""
        if rules_path and Path(rules_path).exists():
            try:
                with open(rules_path, "r") as f:
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
        return subprocess.run(["git", *args], capture_output=True, text=True, timeout=timeout, check=False)

    def get_cache_key(self, file_path: Path) -> str:
        """Generate cache key for a file using mtime and size."""
        try:
            st = file_path.stat()
            base = f"{file_path.as_posix()}|{st.st_mtime_ns}|{st.st_size}"
        except FileNotFoundError:
            base = f"{file_path.as_posix()}|missing"
        return hashlib.blake2s(base.encode("utf-8"), digest_size=16).hexdigest()

    def load_cached_result(self, file_path: Path) -> Optional[Dict]:
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

    def save_cached_result(self, file_path: Path, result: Dict):
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
        if rel in self._skip_files_exact:
            return False
        return True

    def _list_tracked_markdown_with_git(self) -> List[Path]:
        """Get tracked markdown files using git ls-files."""
        try:
            r = self._git("ls-files", "*.md", timeout=8)
            if r.returncode == 0:
                files = [Path(p.strip()) for p in r.stdout.splitlines() if p.strip()]
                return [f for f in files if self._should_validate_file(f)]
        except Exception:
            pass
        return []

    def _walk_markdown_files(self) -> List[Path]:
        """Walk directory tree for markdown files with pruning."""
        files: List[Path] = []
        for root, dirs, filenames in os.walk(".", topdown=True):
            root_posix = root.replace("\\", "/").lstrip("./")

            # Prune directories aggressively
            if any(root_posix.startswith(prefix.rstrip("/")) for prefix in self._skip_dir_prefixes):
                dirs[:] = []  # don't descend
                continue

            # Also prune children about to be visited
            dirs[:] = [
                d
                for d in dirs
                if not any((root_posix + "/" + d).startswith(prefix.rstrip("/")) for prefix in self._skip_dir_prefixes)
            ]

            for name in filenames:
                if not name.endswith(".md"):
                    continue
                p = Path(root) / name
                if self._should_validate_file(p):
                    files.append(p)
        return files

    def get_changed_markdown_files(self) -> Set[Path]:
        """Get only changed Markdown files using git with robust fallbacks."""
        if not self.only_changed:
            return set()

        candidates: Set[str] = set()
        if not self._is_git_repo():
            return set()

        # Prefer diff against last commit, with fallbacks to staged/unstaged
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

        # Also look at the working tree
        try:
            r = self._git("status", "--porcelain", timeout=10)
            if r.returncode == 0:
                for line in r.stdout.splitlines():
                    # Format: "XY path"
                    parts = line.strip().split(maxsplit=1)
                    if len(parts) == 2:
                        candidates.add(parts[1])
        except Exception:
            pass

        out: Set[Path] = set()
        for c in candidates:
            if c.endswith(".md"):
                p = Path(c)
                if self._should_validate_file(p) and p.exists():
                    out.add(p)
        return out

    def _get_markdown_files(self) -> List[Path]:
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

    def validate_single_file(self, file_path: Path) -> Dict:
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
            return {"file": str(file_path), "errors": [f"Could not read file: {e}"], "warnings": [], "valid": False}

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

        out_lines: List[str] = []
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
            if level is not None and last_heading_level is not None and level > last_heading_level + 1:
                if self.safe_fix:
                    # Reduce heading level to only +1 deeper than previous
                    target_level = min(6, last_heading_level + 1)
                    # Extract heading text after hashes and one space
                    heading_text = trimmed[level + 1 :].lstrip() if len(trimmed) > level + 1 else ""
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
            if self.wrap_long_lines and len(out_line) > 120 and not in_code_block and not out_line.startswith("```"):
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
        if require_tldr and not (TLDR_HEADING_PATTERN.search(text) or TLDR_ANCHOR_PATTERN.search(text)):
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

        # Backtick file references (`foo.md`)
        for file_ref in FILE_REFERENCE_PATTERN.findall(text):
            p1 = file_path.parent / file_ref
            p2 = Path(file_ref)
            if not p1.exists() and not p2.exists():
                warnings.append(f"File reference not found: {file_ref}")

        # Backlog references (maintain existing functionality)
        backlog_refs = BACKLOG_REFERENCE_PATTERN.findall(text)
        for backlog_ref in backlog_refs:
            # Could add validation against actual backlog here
            pass

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
                few_shot_results = self.few_shot_loader.apply_patterns_to_content(text, self.few_shot_patterns)

                # Add few-shot suggestions to warnings
                for suggestion in few_shot_results.get("validation_suggestions", []):
                    if suggestion not in warnings:
                        warnings.append(f"Few-shot suggestion: {suggestion}")

                # Add pattern confidence information
                if few_shot_results.get("matched_patterns"):
                    pattern_info = []
                    for pattern in few_shot_results["matched_patterns"]:
                        pattern_info.append(f"{pattern['pattern']} (confidence: {pattern['confidence']:.2f})")
                    warnings.append(f"Matched patterns: {', '.join(pattern_info)}")

            except Exception as e:
                warnings.append(f"Few-shot validation error: {e}")

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

    def validate_files_parallel(self, files: List[Path]) -> Dict[Path, Dict]:
        """Validate multiple files in parallel."""
        results = {}

        if not files:
            return results

        print(f"Validating {len(files)} files with {self.max_workers} workers...")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {executor.submit(self.validate_single_file, file_path): file_path for file_path in files}

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

    def run_validation(self) -> Dict:
        """Run the complete validation process."""
        start_time = time.time()

        print("Starting optimized documentation validation...")

        # Get files to validate
        markdown_files = self._get_markdown_files()

        if not markdown_files:
            return {"execution_time": 0.0, "files_checked": 0, "errors": [], "warnings": [], "all_valid": True}

        # Validate files in parallel
        validation_results = self.validate_files_parallel(markdown_files)

        # Collect results
        all_errors = []
        all_warnings = []
        valid_files = 0

        for file_path, result in validation_results.items():
            if result["valid"]:
                valid_files += 1
            all_errors.extend([f"{result['file']}: {error}" for error in result["errors"]])
            all_warnings.extend([f"{result['file']}: {warning}" for warning in result["warnings"]])

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
    parser = argparse.ArgumentParser(description="Optimized documentation coherence validator")
    parser.add_argument("--check", choices=["backlog"], help="Specific validation mode")
    parser.add_argument("--path", default="000_core/000_backlog.md", help="Path to file for validation")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--warn-only", action="store_true", help="Return OK even if FAIL found (migration mode)")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument("--only-changed", action="store_true", help="Only validate changed files")
    parser.add_argument("--workers", type=int, help="Number of worker threads")
    parser.add_argument("--cache-ttl", type=int, default=300, help="Cache TTL in seconds")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--emit-json", help="Save results to JSON file")
    parser.add_argument("--safe-fix", action="store_true", help="Apply safe fixes (tabs->spaces, trim trailing)")
    parser.add_argument("--tab-width", type=int, default=4, help="Spaces per tab when --safe-fix")
    parser.add_argument("--strict-anchors", action="store_true", help="Fail on duplicate anchor ids")
    parser.add_argument("--wrap-long-lines", action="store_true", help="Wrap lines longer than 120 chars")
    parser.add_argument("--no-few-shot", action="store_true", help="Disable few-shot enhanced validation")

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

    # Handle regular documentation validation
    validator = OptimizedDocCoherenceValidator(
        dry_run=args.dry_run,
        only_changed=args.only_changed,
        max_workers=args.workers,
        cache_ttl=args.cache_ttl,
        emit_json=args.emit_json,
        safe_fix=args.safe_fix,
        strict_anchors=args.strict_anchors,
        tab_width=args.tab_width,
        wrap_long_lines=args.wrap_long_lines,
        enable_few_shot=not args.no_few_shot,
    )

    results = validator.run_validation()

    if args.json or args.emit_json:
        output = json.dumps(results, indent=2)
        if args.emit_json:
            with open(args.emit_json, "w") as f:
                f.write(output)
        else:
            print(output)
    else:
        print(f"\nValidation completed in {results['execution_time']:.2f}s")
        print(f"Files checked: {results['files_checked']}")
        print(f"Valid files: {results['valid_files']}")
        print(f"Invalid files: {results['invalid_files']}")
        print(f"Errors: {len(results['errors'])}")
        print(f"Warnings: {len(results['warnings'])}")
        if results["changes_made"]:
            print(f"Files auto-fixed: {len(results['changes_made'])}")

        if results["errors"]:
            print("\nErrors:")
            for error in results["errors"][:10]:  # Show first 10 errors
                print(f"  ❌ {error}")
            if len(results["errors"]) > 10:
                print(f"  ... and {len(results['errors']) - 10} more errors")

        if results["warnings"]:
            print("\nWarnings:")
            for warning in results["warnings"][:10]:  # Show first 10 warnings
                print(f"  ⚠️ {warning}")
            if len(results["warnings"]) > 10:
                print(f"  ... and {len(results['warnings']) - 10} more warnings")


if __name__ == "__main__":
    main()
