#!/usr/bin/env python3
"""
PRD Decision Helper
Determines whether to generate a PRD for a backlog item based on points and score.
"""

import re
import sys
from typing import Optional, Tuple

def parse_backlog_item(backlog_content: str, item_id: str) -> tuple[int, float] | None:
    """Parse backlog item to extract points and score"""
    lines = backlog_content.split('\n')
    
    for i, line in enumerate(lines):
        if (item_id in line or item_id.replace('-', '‑') in line) and '|' in line:
            # Extract points from the table row
            parts = line.split('|')
            if len(parts) >= 5:
                points_str = parts[4].strip()
                try:
                    points = int(points_str)
                except ValueError:
                    continue
                
                # Look for score in the next few lines (comments)
                score = 0.0
                for j in range(i, min(i + 3, len(lines))):
                    score_match = re.search(r'<!--score_total:\s*([\d.]+)-->', lines[j])
                    if score_match:
                        score = float(score_match.group(1))
                        break
                
                return points, score
    
    return None

def should_generate_prd(points: int, score: float) -> bool:
    """Determine if PRD should be generated based on decision rule"""
    # Rule: points < 5 AND score >= 3.0 -> skip PRD
    if points < 5 and score >= 3.0:
        return False
    return True

def main():
    """Main function"""
    if len(sys.argv) != 3:
        print("Usage: python prd_decision_helper.py <backlog_content> <item_id>")
        sys.exit(1)
    
    backlog_content = sys.argv[1]
    item_id = sys.argv[2]
    
    result = parse_backlog_item(backlog_content, item_id)
    
    if result is None:
        print("ERROR: Could not parse backlog item")
        sys.exit(1)
    
    points, score = result
    should_generate = should_generate_prd(points, score)
    
    print(f"Item: {item_id}")
    print(f"Points: {points}")
    print(f"Score: {score}")
    print(f"Generate PRD: {should_generate}")
    
    if not should_generate:
        print("Reason: points < 5 AND score >= 3.0 -> skip PRD")
    else:
        print("Reason: points >= 5 OR score < 3.0 -> generate PRD")
    
    sys.exit(0 if should_generate else 1)

if __name__ == "__main__":
    main() 