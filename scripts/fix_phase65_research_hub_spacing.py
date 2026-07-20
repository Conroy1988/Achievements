from pathlib import Path

path = Path("scripts/build_research_hub.py")
text = path.read_text(encoding="utf-8")
old = '''    for bucket in ("active", "blocked", "monitoring", "queued", "complete"):
        lines.extend(["", f"## {bucket.title()} tasks", ""])
'''
new = '''    for bucket in ("active", "blocked", "monitoring", "queued", "complete"):
        if lines and lines[-1] == "":
            lines.pop()
        lines.extend(["", f"## {bucket.title()} tasks", ""])
'''
if old not in text:
    raise SystemExit("Expected research hub bucket rendering block was not found")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Corrected research hub bucket spacing")
