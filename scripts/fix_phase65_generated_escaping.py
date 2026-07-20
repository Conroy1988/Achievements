from __future__ import annotations

from pathlib import Path
import py_compile

ROOT = Path(__file__).resolve().parents[1]
GENERATED_BUILDERS = [
    ROOT / "scripts" / "build_research_hub.py",
    ROOT / "scripts" / "build_research_campaign.py",
]

for path in GENERATED_BUILDERS:
    text = path.read_text(encoding="utf-8")
    text = text.replace('"\n"', '"\\n"')
    text = text.replace("'\n'", "'\\n'")
    path.write_text(text, encoding="utf-8")
    py_compile.compile(str(path), doraise=True)
    print(f"Normalized and compiled {path.relative_to(ROOT)}")

mission_intake = ROOT / "scripts" / "build_mission_intake.py"
text = mission_intake.read_text(encoding="utf-8")
old = 'if not isinstance(mission_rows, list) or len(mission_rows) != 7:\n        errors.append("mission API must contain exactly seven missions")'
new = 'if not isinstance(mission_rows, list) or len(mission_rows) != 8:\n        errors.append("mission API must contain exactly eight missions")'
if old not in text:
    raise RuntimeError("Mission intake count contract was not found")
mission_intake.write_text(text.replace(old, new, 1), encoding="utf-8")
py_compile.compile(str(mission_intake), doraise=True)
print("Updated mission intake to the Phase 65 eight-mission contract")
