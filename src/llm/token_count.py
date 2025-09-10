#!/usr/bin/env python3
"""
Lightweight token counting adapters with guarded imports.

Use make_counter(model_family, model_name) to get a .count(text) callable.
Families:
- openai_bpe → tiktoken
- llama_cpp  → llama.cpp (vocab_only)
- hf_fast    → Hugging Face tokenizers (Rust)

We intentionally avoid hard dependencies; imports are tried lazily and
raise informative errors only when used.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class TokenCounter(Protocol):
    def count(self, text: str) -> int: ...


@dataclass
class _OpenAIBPE(TokenCounter):
    model_name: str

    def __post_init__(self) -> None:
        try:
            import tiktoken  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dep
            raise RuntimeError("tiktoken is required for openai_bpe token counting") from exc
        # Prefer model-specific encoding; fallback to cl100k_base
        try:
            self._enc = tiktoken.encoding_for_model(self.model_name)
        except Exception:
            self._enc = tiktoken.get_encoding("cl100k_base")

    def count(self, text: str) -> int:
        return len(self._enc.encode(text))


@dataclass
class _LlamaCpp(TokenCounter):
    model_name: str
    model_path: str | None = None

    def __post_init__(self) -> None:
        try:
            from llama_cpp import Llama  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dep
            raise RuntimeError("llama_cpp is required for llama_cpp token counting") from exc
        # Load tokenizer only; tiny context and vocab_only=True
        if not self.model_path:
            raise RuntimeError("model_path is required for llama_cpp counter")
        self._llm = Llama(model_path=self.model_path, n_ctx=32, vocab_only=True)

    def count(self, text: str) -> int:
        return len(self._llm.tokenize(text.encode("utf-8")))


@dataclass
class _HFFast(TokenCounter):
    model_name: str

    def __post_init__(self) -> None:
        try:
            from tokenizers import Tokenizer  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dep
            raise RuntimeError("tokenizers is required for hf_fast token counting") from exc
        self._Tokenizer = Tokenizer  # save ref
        self._tok = self._Tokenizer.from_pretrained(self.model_name)

    def count(self, text: str) -> int:
        return len(self._tok.encode(text).ids)


def make_counter(model_family: str, model_name: str, *, model_path: str | None = None) -> TokenCounter:
    family = model_family.lower()
    if family == "openai_bpe":
        return _OpenAIBPE(model_name)
    if family == "llama_cpp":
        return _LlamaCpp(model_name=model_name, model_path=model_path)
    if family == "hf_fast":
        return _HFFast(model_name)
    raise ValueError(f"Unknown model_family: {model_family}")
