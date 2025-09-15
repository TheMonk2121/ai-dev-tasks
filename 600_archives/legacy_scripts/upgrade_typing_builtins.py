from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any

"""
Refactor deprecated typing aliases (List, Dict, Tuple, Set, FrozenSet)
to built-in generics (list, dict, tuple, set, frozenset) in the `scripts/`
directory. Also cleans up imports from typing to remove those names.

Target Python: 3.12 (PEP 585 generics are available).
"""


# Typing aliases that should become built-in generics (PEP 585)
DEPRECATED = {
    "List": "list",
    "Dict": "dict",
    "Tuple": "tuple",
    "Set": "set",
    "FrozenSet": "frozenset",
    "Type": "type",
}

# Names to remove from `from typing import ...` that we rewrite separately
REMOVE_ONLY = {"Optional", "Union"}


def replace_builtins(text: str) -> str:
    # Replace attribute-style usage: typing.List[..., typing.Dict[...]
    for old, new in DEPRECATED.items():
        text = re.sub(rf"\btyping\.{old}\[", f"{new}[", text)

    # Replace bare usage: List[...], Dict[...]
    for old, new in DEPRECATED.items():
        text = re.sub(rf"(?<!\.)\b{old}\[", f"{new}[", text)

    return text


def clean_typing_imports(text: str) -> str:
    # Handle both single-line and parenthesized multi-line imports from typing
    pattern = re.compile(r"(^from\s+typing\s+import\s+(?P<body>[^\n]+)$)", re.MULTILINE)

    def _filter_import_list(import_list: str) -> str:
        # Remove inline comments and split by commas
        # Preserve aliases (e.g., Name as Alias)
        parts = [p.strip() for p in import_list.split(",")]
        kept = []
        for part in parts:
            # strip trailing comments
            part_nocomment = part.split("#", 1)[0].strip()
            if not part_nocomment:
                continue
            name = part_nocomment.split(" ")[0]
            base = name.split(".")[-1]
            if base in DEPRECATED or base in REMOVE_ONLY:
                continue
            kept.append(part_nocomment)
        return ", ".join(kept)

    def repl(m: re.Match) -> str:
        body = m.group("body")
        # If parenthesized multiline, capture content inside parens
        if body.rstrip().endswith("("):
            # Find the matching closing paren from this position
            start = m.end()
            # Search forward for closing paren at column start (simplify: consume until a line starting with ")")
            return m.group(0)  # Skip complex cases; handled below
        filtered = _filter_import_list(body)
        if not filtered:
            return ""  # remove the entire import line
        return f"from typing import {filtered}"

    text = pattern.sub(repl, text)

    # Handle simple parenthesized multi-line imports
    paren_pat = re.compile(
        r"from\s+typing\s+import\s*\((?P<body>.*?)\)\s*\n",
        re.DOTALL,
    )

    def repl_paren(m: re.Match) -> str:
        body = m.group("body")
        names = []
        for line in body.splitlines():
            frag = line.strip().rstrip(",")
            frag = frag.split("#", 1)[0].strip()
            if not frag:
                continue
            base = frag.split(" ")[0].split(".")[-1]
            if base in DEPRECATED:
                continue
            names.append(frag)
        if not names:
            return ""  # remove whole import
        return "from typing import " + ", ".join(names) + "\n"

    text = paren_pat.sub(repl_paren, text)
    return text


def _find_matching_bracket(s: str, start: int) -> int:
    # start points at the opening '['
    depth = 0
    i = start
    while i < len(s):
        c = s[i]
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def _split_top_level_commas(s: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    depth_br = depth_par = depth_brace = 0
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "[":
            depth_br += 1
        elif ch == "]":
            depth_br -= 1
        elif ch == "(":
            depth_par += 1
        elif ch == ")":
            depth_par -= 1
        elif ch == "{":
            depth_brace += 1
        elif ch == "}":
            depth_brace -= 1
        if ch == "," and depth_br == depth_par == depth_brace == 0:
            parts.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
        i += 1
    if buf:
        parts.append("".join(buf).strip())
    return parts


def replace_optional_union(text: str) -> str:
    # Replace Optional[...] -> ... | None, handling nested brackets
    i = 0
    out: list[str] = []
    while i < len(text):
        if text.startswith("typing.Optional[", i) or text.startswith("Optional[", i):
            j = text.find("[", i)
            end = _find_matching_bracket(text, j)
            if end == -1:
                out.append(text[i])
                i += 1
                continue
            inner = text[j + 1 : end].strip()
            out.append(f"{inner} | None")
            i = end + 1
            continue
        if text.startswith("typing.Union[", i) or text.startswith("Union[", i):
            j = text.find("[", i)
            end = _find_matching_bracket(text, j)
            if end == -1:
                out.append(text[i])
                i += 1
                continue
            inner = text[j + 1 : end].strip()
            members = _split_top_level_commas(inner)
            out.append(" | ".join(members))
            i = end + 1
            continue
        out.append(text[i])
        i += 1
    text = "".join(out)

    # Clean typing imports of Optional/Union names
    text = clean_typing_imports(text)
    return text


def replace_isinstance_tuple(text: str) -> str:
    # Replace isinstance(x, (A, B, C)) -> isinstance(x, A | B | C)
    pattern = re.compile(r"isinstance\s*\(\s*([^,]+?)\s*,\s*\(([^()]+)\)\s*\)")

    def repl(m: re.Match) -> str:
        obj = m.group(1).strip()
        types = m.group(2)
        members = [t.strip() for t in types.split(",") if t.strip()]
        return f"isinstance({obj}, {' | '.join(members)})"

    return pattern.sub(repl, text)


def process_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    text = original
    text = replace_builtins(text)
    text = clean_typing_imports(text)
    text = replace_optional_union(text)
    text = replace_isinstance_tuple(text)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    # Accept one or more directories; default to scripts/
    args = sys.argv[1:]
    if not args:
        roots = [Path(__file__).resolve().parents[1]]  # scripts/
    else:
        roots = [Path(p).resolve() for p in args]

    changed = 0
    for root in roots:
        for py in root.rglob("*.py"):
            if py.resolve() == Path(__file__).resolve():
                continue
            try:
                if process_file(py):
                    changed += 1
            except Exception as e:
                print(f"Skipping {py}: {e}")
    print(f"Updated files: {changed}")


if __name__ == "__main__":
    main()
