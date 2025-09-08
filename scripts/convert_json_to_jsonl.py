#!/usr/bin/env python3
"""
Convert JSON array to JSONL format for evaluation datasets.
"""
import json
import sys
import pathlib

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 scripts/convert_json_to_jsonl.py <input.json> <output.jsonl>")
        sys.exit(1)
    
    src = pathlib.Path(sys.argv[1])
    dst = pathlib.Path(sys.argv[2])
    
    if not src.exists():
        print(f"Error: Input file {src} does not exist")
        sys.exit(1)
    
    # Load JSON array
    items = json.loads(src.read_text(encoding="utf-8"))
    
    if not isinstance(items, list):
        print(f"Error: Input file {src} is not a JSON array")
        sys.exit(1)
    
    # Write JSONL
    with dst.open("w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    
    print(f"✅ Converted {src} → {dst} ({len(items)} lines)")

if __name__ == "__main__":
    main()
