from __future__ import annotations
import unicodedata
from dataclasses import dataclass
from typing import Protocol
from .character_tokenizer import CharacterTokenizer, make_character_tokenizer
from .script_aware_tokenizer import ScriptAwareTokenizer, make_multilingual_tokenizer, make_script_aware_tokenizer
            import tiktoken  # type: ignore[import-untyped]
            from llama_cpp import Llama  # type: ignore[import-untyped]
            from tokenizers import Tokenizer  # type: ignore[import-untyped]
import os
from typing import Any, Dict, List, Optional, Union
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

Unicode Normalization:
- All tokenizers now apply NFC normalization to improve monotonicity
- This addresses the common issue where count(a + b) < count(b) due to
  Unicode character sequence compression in tokenizers.
"""





class TokenCounter(Protocol):
    def count(self, text: str) -> int: ...


def _normalize_unicode(text: str) -> str:
    """
    Normalize Unicode text to NFC form to improve tokenizer monotonicity.

    This addresses the common issue where count(a + b) < count(b) due to
    Unicode character sequence compression in tokenizers. NFC normalization
    ensures consistent character representation across different Unicode
    encodings and reduces tokenization inconsistencies.

    Args:
        text: Input text to normalize

    Returns:
        NFC-normalized text
    """
    return unicodedata.normalize("NFC", text)


@dataclass
class _OpenAIBPE(TokenCounter):
    model_name: str

    def __post_init__(self) -> None:
        try:
        except Exception as exc:  # pragma: no cover - optional dep
            raise RuntimeError("tiktoken is required for openai_bpe token counting") from exc
        # Prefer model-specific encoding; fallback to cl100k_base
        try:
            self._enc = tiktoken.encoding_for_model(self.model_name)
        except Exception:
            self._enc = tiktoken.get_encoding("cl100k_base")

    def count(self, text: str) -> int:
        # Apply Unicode normalization to improve monotonicity
        normalized_text = _normalize_unicode(text)
        return len(self._enc.encode(normalized_text))


@dataclass
class _LlamaCpp(TokenCounter):
    model_name: str
    model_path: str | None = None

    def __post_init__(self) -> None:
        try:
        except Exception as exc:  # pragma: no cover - optional dep
            raise RuntimeError("llama_cpp is required for llama_cpp token counting") from exc
        # Load tokenizer only; tiny context and vocab_only=True
        if not self.model_path:
            raise RuntimeError("model_path is required for llama_cpp counter")
        self._llm = Llama(model_path=self.model_path, n_ctx=32, vocab_only=True)

    def count(self, text: str) -> int:
        # Apply Unicode normalization to improve monotonicity
        normalized_text = _normalize_unicode(text)
        return len(self._llm.tokenize(normalized_text.encode("utf-8")))


@dataclass
class _HFFast(TokenCounter):
    model_name: str

    def __post_init__(self) -> None:
        try:
        except Exception as exc:  # pragma: no cover - optional dep
            raise RuntimeError("tokenizers is required for hf_fast token counting") from exc
        self._Tokenizer = Tokenizer  # save ref
        self._tok = self._Tokenizer.from_pretrained(self.model_name)

    def count(self, text: str) -> int:
        # Apply Unicode normalization to improve monotonicity
        normalized_text = _normalize_unicode(text)
        return len(self._tok.encode(normalized_text).ids)


def make_counter(model_family: str, model_name: str, *, model_path: str | None = None) -> TokenCounter:
    family = model_family.lower()
    if family == "openai_bpe":
        return _OpenAIBPE(model_name)
    if family == "llama_cpp":
        return _LlamaCpp(model_name=model_name, model_path=model_path)
    if family == "hf_fast":
        return _HFFast(model_name)
    if family == "character":
        # Character-level tokenizer for guaranteed monotonicity
        return make_character_tokenizer("unicode")
    if family == "grapheme":
        # Grapheme cluster tokenizer for linguistic accuracy
        return make_character_tokenizer("grapheme")
    if family == "script_aware":
        # Script-aware tokenizer for multilingual text
        return make_script_aware_tokenizer("unicode")
    if family == "multilingual":
        # Multilingual tokenizer with script awareness
        return make_multilingual_tokenizer("unicode")
    raise ValueError(f"Unknown model_family: {model_family}")


def make_character_counter(
    tokenizer_type: str = "unicode",
    normalize_unicode: bool = True,
    include_whitespace: bool = True,
    include_control_chars: bool = False,
) -> CharacterTokenizer:
    """
    Create a character-level tokenizer with specific configuration.

    Args:
        tokenizer_type: Type of tokenizer ("unicode" or "grapheme")
        normalize_unicode: Whether to apply Unicode normalization
        include_whitespace: Whether to include whitespace characters
        include_control_chars: Whether to include control characters

    Returns:
        Character-level tokenizer instance
    """
    return make_character_tokenizer(
        tokenizer_type=tokenizer_type,
        normalize_unicode=normalize_unicode,
        include_whitespace=include_whitespace,
        include_control_chars=include_control_chars,
    )
