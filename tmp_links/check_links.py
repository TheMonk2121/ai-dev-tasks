import os, re, json
from pathlib import Path
root = Path('.')
missing = []
for md in root.rglob('*.md'):
    try:
        text = md.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        continue
    for m in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", text):
        link = m.group(1).strip()
        if re.match(r"^[a-z]+://", link) or link.startswith('#'):
            continue
        p = (md.parent / link).resolve()
        if not p.exists():
            missing.append({"file": str(md), "link": link})
print(json.dumps(missing[:200], indent=2))
print('Total missing:', len(missing))
