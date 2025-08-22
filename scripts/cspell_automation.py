#!/usr/bin/env python3
"""
cSpell Automation Script
------------------------
Automated cSpell word addition for VS Code settings.json

This script is designed to be triggered by the "cspell" role in the memory rehydration system.
It automatically adds words to the cSpell configuration in .vscode/settings.json.

Usage:
    python3 scripts/cspell_automation.py "word1 word2 word3"
    python3 scripts/cspell_automation.py --file word_list.txt
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Set


def load_settings_json() -> dict:
    """Load the current VS Code settings.json file"""
    settings_path = Path(".vscode/settings.json")

    if not settings_path.exists():
        raise FileNotFoundError(f"Settings file not found: {settings_path}")

    with open(settings_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_settings_json(settings: dict) -> None:
    """Save the updated VS Code settings.json file"""
    settings_path = Path(".vscode/settings.json")

    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)


def get_current_words(settings: dict) -> Set[str]:
    """Extract current cSpell words from settings"""
    words = settings.get("cSpell", {}).get("words", [])
    return set(word.lower() for word in words)


def add_words_to_settings(settings: dict, new_words: List[str]) -> List[str]:
    """Add new words to settings, maintaining alphabetical order"""
    if "cSpell" not in settings:
        settings["cSpell"] = {}

    if "words" not in settings["cSpell"]:
        settings["cSpell"]["words"] = []

    current_words = set(word.lower() for word in settings["cSpell"]["words"])
    added_words = []

    for word in new_words:
        word_lower = word.lower()
        if word_lower not in current_words:
            # Find the correct position to insert (alphabetical order)
            insert_index = 0
            for i, existing_word in enumerate(settings["cSpell"]["words"]):
                if word.lower() < existing_word.lower():
                    insert_index = i
                    break
                insert_index = i + 1

            settings["cSpell"]["words"].insert(insert_index, word)
            current_words.add(word_lower)
            added_words.append(word)

    return added_words


def validate_word(word: str) -> bool:
    """Validate that a word is suitable for cSpell"""
    # Basic validation: alphanumeric and common symbols only
    if not re.match(r"^[a-zA-Z0-9_-]+$", word):
        return False

    # Don't add very short words (likely to cause false positives)
    if len(word) < 2:
        return False

    return True


def parse_words_from_text(text: str) -> List[str]:
    """Parse words from text input"""
    # Split on whitespace and common delimiters
    words = re.split(r"[\s,;]+", text.strip())
    # Filter out empty strings and validate
    return [word for word in words if word and validate_word(word)]


def main():
    """Main function for cSpell automation"""
    parser = argparse.ArgumentParser(description="Automated cSpell word addition")
    parser.add_argument("words", nargs="?", help="Words to add (space-separated)")
    parser.add_argument("--file", help="File containing words to add (one per line)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be added without making changes")

    args = parser.parse_args()

    if not args.words and not args.file:
        print("❌ Error: Must provide words or --file argument")
        sys.exit(1)

    # Parse words
    new_words = []
    if args.words:
        new_words.extend(parse_words_from_text(args.words))

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ Error: File not found: {file_path}")
            sys.exit(1)

        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
            new_words.extend(parse_words_from_text(file_content))

    if not new_words:
        print("❌ Error: No valid words found")
        sys.exit(1)

    # Remove duplicates while preserving order
    seen = set()
    unique_words = []
    for word in new_words:
        if word.lower() not in seen:
            seen.add(word.lower())
            unique_words.append(word)

    print(f"📝 Processing {len(unique_words)} words: {', '.join(unique_words)}")

    try:
        settings = load_settings_json()
        current_words = get_current_words(settings)

        # Filter out words that already exist
        words_to_add = [word for word in unique_words if word.lower() not in current_words]

        if not words_to_add:
            print("✅ All words already exist in cSpell configuration")
            return

        print(f"➕ Adding {len(words_to_add)} new words: {', '.join(words_to_add)}")

        if args.dry_run:
            print("🔍 Dry run - no changes made")
            return

        # Add words to settings
        added_words = add_words_to_settings(settings, words_to_add)

        # Save updated settings
        save_settings_json(settings)

        print(f"✅ Successfully added {len(added_words)} words to cSpell configuration")
        print(f"📊 Total cSpell words: {len(settings['cSpell']['words'])}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
