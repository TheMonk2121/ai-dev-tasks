from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum


class Profile(str, Enum):
    GOLD = "gold"
    REAL = "real"
    MOCK = "mock"


@dataclass
class ProfileRunner:
    name: str
    description: str
    run: Callable[[list[str]], int]


__all__ = ["Profile", "ProfileRunner"]


