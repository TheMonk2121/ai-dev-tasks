#!/usr/bin/env python3
"""
Load evaluation cases from a JSON file.
"""
import json
import os
from dataclasses import dataclass
from typing import List


@dataclass
class Case:
    id: str
    query: str
    tag: str
    qvec: list


def load_eval_cases(name: str) -> List[Case]:
    """Load evaluation cases from file specified by CASES_FILE or evals/{name}_cases.json"""
    path = os.getenv("CASES_FILE", f"evals/{name}_cases.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    out: List[Case] = []
    for row in data:
        out.append(
            Case(
                id=row.get("case_id") or row.get("id"),
                query=row["query"],
                tag=row.get("tag", ""),
                qvec=row.get("qvec", []),
            )
        )
    return out

