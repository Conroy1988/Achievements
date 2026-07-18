from __future__ import annotations

from pathlib import Path
from urllib.parse import unquote, urlsplit
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
SKIP_PARTS = {".git", "_site", "vendor"}


def candidates(source: Path, raw_target: str) -> list[Path]:
    target = raw_target.strip().split()[0].strip("<>")
    if not target or "{{" in target or "}}" in target:
        return []
    if target.startswith(("#", "mailto:", "tel:")):
        return []

    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc:
        return []

    path_text = unquote(parsed.path)
    if not path_text or path_text.startswith("/Achievements/"):
        return []

    path = ROOT / path_text.lstrip("/") if path_text.startswith("/") else source.parent / path_text
    result = [path]
    if path.suffix == ".html":
        result.append(path.with_suffix(".md"))
    if path_text.endswith("/"):
        result.extend((path / "index.md", path.with_suffix(".md")))
    elif not path.suffix:
        result.extend((path.with_suffix(".md"), path / "index.md"))
    return result


def main() -> int:
    failures: list[str] = []
    for source in sorted(ROOT.rglob("*.md")):
        if any(part in SKIP_PARTS for part in source.parts):
            continue
        text = source.read_text(encoding="utf-8")
        for match in LINK_PATTERN.finditer(text):
            checked = candidates(source, match.group(1))
            if checked and not any(path.exists() for path in checked):
                line = text.count("\n", 0, match.start()) + 1
                failures.append(f"{source.relative_to(ROOT)}:{line}: {match.group(1)}")

    if failures:
        print("Unresolved repository-relative links:")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1

    print("All repository-relative Markdown links resolved successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
