from __future__ import annotations

from pathlib import Path
import py_compile

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "scripts" / "build_research_hub.py",
    ROOT / "scripts" / "build_research_campaign.py",
]

for path in TARGETS:
    text = path.read_text(encoding="utf-8")
    text = text.replace('"\n"', '"\\n"')
    text = text.replace("'\n'", "'\\n'")
    path.write_text(text, encoding="utf-8")
    py_compile.compile(str(path), doraise=True)
    print(f"Normalized and compiled {path.relative_to(ROOT)}")
