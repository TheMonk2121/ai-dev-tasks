from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import Protocol

from .character_tokenizer import CharacterTokenizer, make_character_tokenizer

#!/usr/bin/env python3
"""
Script-aware tokenizer implementation for multilingual text.

This tokenizer respects Unicode script boundaries and implements the
"BPE Stays on SCRIPT" approach to improve tokenization consistency
across different writing systems.
"""





class ScriptAwareTokenizer(Protocol):
    """Protocol for script-aware tokenizers."""

    def count(self, text: str) -> int: ...
    def tokenize(self, text: str) -> list[str]: ...


@dataclass
class ScriptBoundaryTokenizer:
    """
    Tokenizer that respects Unicode script boundaries.

    This implements the "BPE Stays on SCRIPT" approach where tokenization
    boundaries are aligned with Unicode script changes, improving consistency
    across different writing systems.
    """

    normalize_unicode: bool = True
    base_tokenizer: CharacterTokenizer | None = None

    def __post_init__(self) -> None:
        """Initialize the base tokenizer if not provided."""
        if self.base_tokenizer is None:
            self.base_tokenizer = make_character_tokenizer("unicode")

    def count(self, text: str) -> int:
        """
        Count tokens while respecting script boundaries.

        Args:
            text: Input text to count

        Returns:
            Number of tokens
        """
        if not text:
            return 0

        # Apply Unicode normalization if enabled
        if self.normalize_unicode:
            text = unicodedata.normalize("NFC", text)

        # Split by script boundaries and count each segment
        script_segments = self._split_by_script(text)
        total_count = 0

        for segment in script_segments:
            if segment:  # Skip empty segments
                total_count += self.base_tokenizer.count(segment)

        return total_count

    def tokenize(self, text: str) -> list[str]:
        """
        Tokenize text while respecting script boundaries.

        Args:
            text: Input text to tokenize

        Returns:
            List of tokens
        """
        if not text:
            return []

        # Apply Unicode normalization if enabled
        if self.normalize_unicode:
            text = unicodedata.normalize("NFC", text)

        # Split by script boundaries and tokenize each segment
        script_segments = self._split_by_script(text)
        all_tokens = []

        for segment in script_segments:
            if segment:  # Skip empty segments
                segment_tokens = self.base_tokenizer.tokenize(segment)
                all_tokens.extend(segment_tokens)

        return all_tokens

    def _split_by_script(self, text: str) -> list[str]:
        """
        Split text by Unicode script boundaries.

        Args:
            text: Input text

        Returns:
            List of text segments, each containing characters from a single script
        """
        if not text:
            return []

        segments = []
        current_segment = []
        current_script = None

        for char in text:
            # Get the script of the current character
            char_script = self._get_script(char)

            # If script changed and we have a current segment, start a new one
            if current_script is not None and char_script != current_script:
                if current_segment:
                    segments.append("".join(current_segment))
                current_segment = [char]
            else:
                current_segment.append(char)

            current_script = char_script

        # Add the final segment
        if current_segment:
            segments.append("".join(current_segment))

        return segments

    def _get_script(self, char: str) -> str:
        """
        Get the Unicode script of a character.

        Args:
            char: Character to analyze

        Returns:
            Unicode script name
        """
        try:
            # Get the script property
            script = unicodedata.name(char).split()[0] if unicodedata.name(char, "").split() else "Unknown"

            # Map to common script categories
            script_mapping = {
                "LATIN": "Latin",
                "CYRILLIC": "Cyrillic",
                "GREEK": "Greek",
                "ARABIC": "Arabic",
                "HEBREW": "Hebrew",
                "HIRAGANA": "Hiragana",
                "KATAKANA": "Katakana",
                "HANGUL": "Hangul",
                "HAN": "Han",
                "THAI": "Thai",
                "DEVANAGARI": "Devanagari",
                "BENGALI": "Bengali",
                "TAMIL": "Tamil",
                "TELUGU": "Telugu",
                "GUJARATI": "Gujarati",
                "KANNADA": "Kannada",
                "MALAYALAM": "Malayalam",
                "ORIYA": "Oriya",
                "PUNJABI": "Punjabi",
                "SINHALA": "Sinhala",
                "TIBETAN": "Tibetan",
                "MONGOLIAN": "Mongolian",
                "GEORGIAN": "Georgian",
                "ARMENIAN": "Armenian",
                "ETHIOPIC": "Ethiopic",
                "CHEROKEE": "Cherokee",
                "CANADIAN": "Canadian",
                "OGHAM": "Ogham",
                "RUNIC": "Runic",
                "TAGALOG": "Tagalog",
                "HANUNOO": "Hanunoo",
                "BUHID": "Buhid",
                "TAGBANWA": "Tagbanwa",
                "KHMER": "Khmer",
                "LAO": "Lao",
                "MYANMAR": "Myanmar",
                "CHAM": "Cham",
                "BALINESE": "Balinese",
                "BATAK": "Batak",
                "BUGINESE": "Buginese",
                "JAVANESE": "Javanese",
                "SUNDANESE": "Sundanese",
                "REJANG": "Rejang",
                "LEPCHA": "Lepcha",
                "LIMBU": "Limbu",
                "NEWA": "Newa",
                "SAURASHTRA": "Saurashtra",
                "TAKRI": "Takri",
                "WARANG": "Warang",
                "ZANABAZAR": "Zanabazar",
                "SOYOMBO": "Soyombo",
                "PAU": "Pau",
                "BHAIKSUKI": "Bhaiksuki",
                "MARCHEN": "Marchen",
                "MASARAM": "Masaram",
                "GUNJALA": "Gunjala",
                "MAKASAR": "Makasar",
                "TANGSA": "Tangsa",
                "TOTO": "Toto",
                "VITHKUQI": "Vithkuqi",
                "OLD": "Old",
                "MEDEFAIDRIN": "Medefaidrin",
                "NANDINAGARI": "Nandinagari",
                "CHORASMIAN": "Chorasmian",
                "DIVES": "Dives",
                "KHITAN": "Khitan",
                "YEZIDI": "Yezidi",
            }

            # Return mapped script or fallback to first part of name
            return script_mapping.get(script, script.split("_")[0] if "_" in script else script)

        except (ValueError, IndexError):
            # Fallback for characters without names or special cases
            return "Unknown"


@dataclass
class MultilingualTokenizer:
    """
    Advanced multilingual tokenizer with script awareness and language detection.

    This tokenizer combines script-aware tokenization with language-specific
    handling for optimal multilingual text processing.
    """

    normalize_unicode: bool = True
    script_aware: bool = True
    base_tokenizer: CharacterTokenizer | None = None

    def __post_init__(self) -> None:
        """Initialize the base tokenizer if not provided."""
        if self.base_tokenizer is None:
            self.base_tokenizer = make_character_tokenizer("unicode")

    def count(self, text: str) -> int:
        """
        Count tokens with multilingual awareness.

        Args:
            text: Input text to count

        Returns:
            Number of tokens
        """
        if not text:
            return 0

        # Apply Unicode normalization if enabled
        if self.normalize_unicode:
            text = unicodedata.normalize("NFC", text)

        if self.script_aware:
            # Use script-aware tokenization
            script_tokenizer = ScriptBoundaryTokenizer(
                normalize_unicode=False, base_tokenizer=self.base_tokenizer  # Already normalized
            )
            return script_tokenizer.count(text)
        else:
            # Use base tokenizer directly
            return self.base_tokenizer.count(text)

    def tokenize(self, text: str) -> list[str]:
        """
        Tokenize text with multilingual awareness.

        Args:
            text: Input text to tokenize

        Returns:
            List of tokens
        """
        if not text:
            return []

        # Apply Unicode normalization if enabled
        if self.normalize_unicode:
            text = unicodedata.normalize("NFC", text)

        if self.script_aware:
            # Use script-aware tokenization
            script_tokenizer = ScriptBoundaryTokenizer(
                normalize_unicode=False, base_tokenizer=self.base_tokenizer  # Already normalized
            )
            return script_tokenizer.tokenize(text)
        else:
            # Use base tokenizer directly
            return self.base_tokenizer.tokenize(text)


def make_script_aware_tokenizer(
    base_tokenizer_type: str = "unicode",
    normalize_unicode: bool = True,
    include_whitespace: bool = True,
    include_control_chars: bool = False,
) -> ScriptBoundaryTokenizer:
    """
    Create a script-aware tokenizer.

    Args:
        base_tokenizer_type: Type of base tokenizer ("unicode" or "grapheme")
        normalize_unicode: Whether to apply Unicode normalization
        include_whitespace: Whether to include whitespace characters
        include_control_chars: Whether to include control characters

    Returns:
        Script-aware tokenizer instance
    """
    base_tokenizer = make_character_tokenizer(
        base_tokenizer_type,
        normalize_unicode=normalize_unicode,
        include_whitespace=include_whitespace,
        include_control_chars=include_control_chars,
    )

    return ScriptBoundaryTokenizer(normalize_unicode=normalize_unicode, base_tokenizer=base_tokenizer)


def make_multilingual_tokenizer(
    base_tokenizer_type: str = "unicode",
    normalize_unicode: bool = True,
    script_aware: bool = True,
    include_whitespace: bool = True,
    include_control_chars: bool = False,
) -> MultilingualTokenizer:
    """
    Create a multilingual tokenizer with script awareness.

    Args:
        base_tokenizer_type: Type of base tokenizer ("unicode" or "grapheme")
        normalize_unicode: Whether to apply Unicode normalization
        script_aware: Whether to use script-aware tokenization
        include_whitespace: Whether to include whitespace characters
        include_control_chars: Whether to include control characters

    Returns:
        Multilingual tokenizer instance
    """
    base_tokenizer = make_character_tokenizer(
        base_tokenizer_type,
        normalize_unicode=normalize_unicode,
        include_whitespace=include_whitespace,
        include_control_chars=include_control_chars,
    )

    return MultilingualTokenizer(
        normalize_unicode=normalize_unicode, script_aware=script_aware, base_tokenizer=base_tokenizer
    )


# Convenience functions for common configurations
def script_aware_character_tokenizer() -> ScriptBoundaryTokenizer:
    """Create a script-aware character tokenizer."""
    return make_script_aware_tokenizer("unicode")


def script_aware_grapheme_tokenizer() -> ScriptBoundaryTokenizer:
    """Create a script-aware grapheme tokenizer."""
    return make_script_aware_tokenizer("grapheme")


def multilingual_character_tokenizer() -> MultilingualTokenizer:
    """Create a multilingual character tokenizer."""
    return make_multilingual_tokenizer("unicode")


def multilingual_grapheme_tokenizer() -> MultilingualTokenizer:
    """Create a multilingual grapheme tokenizer."""
    return make_multilingual_tokenizer("grapheme")
