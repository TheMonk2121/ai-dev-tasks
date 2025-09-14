from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import Any, Optional, Protocol, Union

#!/usr/bin/env python3
"""
Character-level tokenizer implementation for guaranteed monotonicity.

This tokenizer operates at the Unicode character level, ensuring that
count(a + b) = count(a) + count(b) always holds, providing mathematical
guarantees for monotonicity properties.
"""




class CharacterTokenizer(Protocol):
    """Protocol for character-level tokenizers."""

    def count(self, text: str) -> int: ...
    def tokenize(self, text: str) -> list[str]: ...


@dataclass
class UnicodeCharacterTokenizer:
    """
    Character-level tokenizer that treats each Unicode character as a token.

    This provides guaranteed monotonicity: count(a + b) = count(a) + count(b)
    for any strings a and b. The trade-off is higher token counts but
    mathematical guarantees.
    """

    normalize_unicode: bool = True
    include_whitespace: bool = True
    include_control_chars: bool = False

    def count(self, text: str) -> int:
        """
        Count the number of characters in the text.

        Args:
            text: Input text to count

        Returns:
            Number of characters (tokens)
        """
        if not text:
            return 0

        # Apply Unicode normalization if enabled
        if self.normalize_unicode:
            text = unicodedata.normalize("NFC", text)

        # Filter characters based on configuration
        filtered_chars = self._filter_characters(text)

        return len(filtered_chars)

    def tokenize(self, text: str) -> list[str]:
        """
        Tokenize text into individual characters.

        Args:
            text: Input text to tokenize

        Returns:
            List of character tokens
        """
        if not text:
            return []

        # Apply Unicode normalization if enabled
        if self.normalize_unicode:
            text = unicodedata.normalize("NFC", text)

        # Filter characters based on configuration
        filtered_chars = self._filter_characters(text)

        return list(filtered_chars)

    def _filter_characters(self, text: str) -> str:
        """
        Filter characters based on configuration.

        Args:
            text: Input text

        Returns:
            Filtered text
        """
        if not self.include_whitespace:
            # Remove whitespace characters
            text = "".join(c for c in text if not c.isspace())

        if not self.include_control_chars:
            # Remove control characters (but keep printable characters)
            text = "".join(c for c in text if unicodedata.category(c)[0] != "C" or c.isspace())

        return text


@dataclass
class GraphemeClusterTokenizer:
    """
    Grapheme cluster tokenizer that respects Unicode grapheme boundaries.

    This is more linguistically appropriate than character-level tokenization
    as it groups combining characters with their base characters.
    """

    normalize_unicode: bool = True

    def count(self, text: str) -> int:
        """
        Count the number of grapheme clusters in the text.

        Args:
            text: Input text to count

        Returns:
            Number of grapheme clusters (tokens)
        """
        if not text:
            return 0

        # Apply Unicode normalization if enabled
        if self.normalize_unicode:
            text = unicodedata.normalize("NFC", text)

        # Count grapheme clusters
        return len(self._grapheme_clusters(text))

    def tokenize(self, text: str) -> list[str]:
        """
        Tokenize text into grapheme clusters.

        Args:
            text: Input text to tokenize

        Returns:
            List of grapheme cluster tokens
        """
        if not text:
            return []

        # Apply Unicode normalization if enabled
        if self.normalize_unicode:
            text = unicodedata.normalize("NFC", text)

        return self._grapheme_clusters(text)

    def _grapheme_clusters(self, text: str) -> list[str]:
        """
        Split text into grapheme clusters.

        This is a simplified implementation. For production use,
        consider using the `regex` library with the r'\\X' pattern
        or a proper Unicode segmentation library.

        Args:
            text: Input text

        Returns:
            List of grapheme clusters
        """
        clusters = []
        current_cluster = []

        for char in text:
            # Check if this is a combining character
            category = unicodedata.category(char)
            is_combining = category.startswith("M")  # Mark category (combining)

            if is_combining and current_cluster:
                # Add to current cluster
                current_cluster.append(char)
            else:
                # Start new cluster
                if current_cluster:
                    clusters.append("".join(current_cluster))
                current_cluster = [char]

        # Add final cluster
        if current_cluster:
            clusters.append("".join(current_cluster))

        return clusters


def make_character_tokenizer(
    tokenizer_type: str = "unicode",
    normalize_unicode: bool = True,
    include_whitespace: bool = True,
    include_control_chars: bool = False,
) -> CharacterTokenizer:
    """
    Create a character-level tokenizer.

    Args:
        tokenizer_type: Type of tokenizer ("unicode" or "grapheme")
        normalize_unicode: Whether to apply Unicode normalization
        include_whitespace: Whether to include whitespace characters
        include_control_chars: Whether to include control characters

    Returns:
        Character-level tokenizer instance

    Raises:
        ValueError: If tokenizer_type is not supported
    """
    if tokenizer_type == "unicode":
        return UnicodeCharacterTokenizer(
            normalize_unicode=normalize_unicode,
            include_whitespace=include_whitespace,
            include_control_chars=include_control_chars,
        )
    elif tokenizer_type == "grapheme":
        return GraphemeClusterTokenizer(normalize_unicode=normalize_unicode)
    else:
        raise ValueError(f"Unsupported tokenizer type: {tokenizer_type}")


# Convenience functions for common configurations
def unicode_character_tokenizer() -> UnicodeCharacterTokenizer:
    """Create a standard Unicode character tokenizer."""
    return UnicodeCharacterTokenizer()


def grapheme_cluster_tokenizer() -> GraphemeClusterTokenizer:
    """Create a standard grapheme cluster tokenizer."""
    return GraphemeClusterTokenizer()


def strict_character_tokenizer() -> UnicodeCharacterTokenizer:
    """Create a strict character tokenizer (no whitespace, no control chars)."""
    return UnicodeCharacterTokenizer(
        normalize_unicode=True,
        include_whitespace=False,
        include_control_chars=False,
    )
