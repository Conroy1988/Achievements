from __future__ import annotations

from pathlib import Path
from urllib.parse import unquote, urlsplit
import argparse
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
SKIP_PARTS = {".git", "_site", "vendor"}


def changed_markdown_files() -> list[Path]:
    try:
        output = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD^", "HEAD"],
            cwd=ROOT,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

    files: list[Path] = []
    for line in output.splitlines():
        path = ROOT / line.strip()
        if path.suffix == ".md" and path.exists():
            files.append(path)
    return sorted(files)


def all_markdown_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.md")
        if not any(part in SKIP_PARTS for part in path.relative_to(ROOT).parts)
    )


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate repository-relative Markdown links.")
    parser.add_argument(
        "--all",
        action="store_true",
        help="validate every Markdown file instead of only files changed by the latest commit",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sources = all_markdown_files() if args.all else changed_markdown_files()
    mode = "full repository" if args.all else "changed-file"

    if not sources:
        print(f"No Markdown files require {mode} link validation.")
        return 0

    failures: list[str] = []
    for source in sources:
        text = source.read_text(encoding="utf-8")
        for match in LINK_PATTERN.finditer(text):
            checked = candidates(source, match.group(1))
            if checked and not any(path.exists() for path in checked):
                line = text.count("\n", 0, match.start()) + 1
                failures.append(f"{source.relative_to(ROOT)}:{line}: {match.group(1)}")

    if failures:
        print(f"Unresolved repository-relative links found during {mode} validation:")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1

    print(f"All links passed {mode} validation across {len(sources)} Markdown files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
