from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs" / "achievement-index.md"
NAVIGATION = ROOT / "docs" / "achievement-guide-navigation.md"
LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def catalogue_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    stop_heading = "## Evidence labels" if path == INDEX else "## Project references"
    return text.split(stop_heading, 1)[0]


def achievement_labels(path: Path) -> set[str]:
    return {
        label.strip()
        for label, _target in LINK_PATTERN.findall(catalogue_text(path))
    }


def main() -> int:
    missing = [str(path.relative_to(ROOT)) for path in (INDEX, NAVIGATION) if not path.exists()]
    if missing:
        print("Missing canonical catalogue files:")
        print("\n".join(f"- {path}" for path in missing))
        return 1

    index_labels = achievement_labels(INDEX)
    navigation_labels = achievement_labels(NAVIGATION)

    only_index = sorted(index_labels - navigation_labels)
    only_navigation = sorted(navigation_labels - index_labels)

    if only_index or only_navigation:
        print("Achievement catalogue drift detected.")
        if only_index:
            print("Present only in achievement index:")
            print("\n".join(f"- {label}" for label in only_index))
        if only_navigation:
            print("Present only in navigation hub:")
            print("\n".join(f"- {label}" for label in only_navigation))
        return 1

    if len(index_labels) != 9:
        print(f"Expected 9 achievement guides, found {len(index_labels)}.")
        return 1

    print("Achievement index and navigation hub contain the same 9 guides.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
