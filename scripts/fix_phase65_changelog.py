from pathlib import Path

path = Path("CHANGELOG.md")
text = path.read_text(encoding="utf-8")
old = "\n### Changed\n\n- Narrowed the remaining YOLO, Pair Extraordinaire, and Starstruck contradiction backlog"
new = "\n- Narrowed the remaining YOLO, Pair Extraordinaire, and Starstruck contradiction backlog"
if old not in text:
    raise SystemExit("Expected duplicate Phase 65 changelog heading was not found")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Consolidated the Phase 65 Unreleased Changed section")
