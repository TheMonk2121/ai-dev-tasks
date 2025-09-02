"""
Lightweight Intent Router

Rule-based intent detection to adjust fusion/rerank/selection policies.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class RoutingDecision:
    intent: str
    rerank_alpha: float
    fusion_profile: str
    final_top_n: int


class IntentRouter:
    def __init__(self, config: Dict[str, Any]):
        self.enabled: bool = bool(config.get("enabled", True))
        self.policies: List[Dict[str, Any]] = list(config.get("policies", []))

    def route(self, query: str) -> Optional[RoutingDecision]:
        if not self.enabled or not self.policies:
            return None

        for policy in self.policies:
            name = str(policy.get("name", "unknown"))
            when_any = policy.get("when_any", [])

            if self._matches_any(query, when_any):
                action = policy.get("action", {})
                return RoutingDecision(
                    intent=name,
                    rerank_alpha=float(action.get("rerank_alpha", 0.7)),
                    fusion_profile=str(action.get("fusion_profile", "balanced")),
                    final_top_n=int(action.get("final_top_n", 8)),
                )

        return None

    def _matches_any(self, query: str, rules: List[Dict[str, Any]]) -> bool:
        q = query
        for rule in rules:
            if "contains" in rule:
                needles = rule["contains"]
                if any(n in q for n in needles):
                    return True
            if "regex" in rule:
                pattern = rule["regex"]
                try:
                    if re.search(pattern, q):
                        return True
                except re.error:
                    continue
        return False
