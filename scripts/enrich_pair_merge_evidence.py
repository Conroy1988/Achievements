from __future__ import annotations

from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import json
import os
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "research" / "live-backlog-sweep.json"
PR_URL = re.compile(r"^https://github\.com/([^/]+)/([^/]+)/pull/(\d+)$")
TRAILER = re.compile(r"^Co-authored-by:\s*(.+?)\s*<([^>]+)>\s*$", re.IGNORECASE | re.MULTILINE)


def api_get(path: str) -> object:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-achievement-encyclopedia-pair-evidence/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(f"https://api.github.com{path}", headers=headers)
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def trailers(message: str) -> list[dict[str, str]]:
    return [{"name": name.strip(), "email": email.strip()} for name, email in TRAILER.findall(message or "")]


def commit_record(value: dict) -> dict:
    commit = value.get("commit") or {}
    author = value.get("author") or {}
    committer = value.get("committer") or {}
    message = str(commit.get("message") or "")
    return {
        "sha": value.get("sha"),
        "html_url": value.get("html_url"),
        "author_login": author.get("login"),
        "committer_login": committer.get("login"),
        "parent_shas": [parent.get("sha") for parent in value.get("parents", [])],
        "subject": message.splitlines()[0] if message else "",
        "coauthor_trailers": trailers(message),
    }


def classify_merge(pr: dict, pull_commits: list[dict], final_commit: dict) -> str:
    parents = final_commit.get("parents", [])
    final_sha = final_commit.get("sha")
    pull_shas = [item.get("sha") for item in pull_commits]
    if len(parents) >= 2:
        return "merge-commit"
    if final_sha and final_sha not in pull_shas:
        return "squash"
    if final_sha and final_sha in pull_shas:
        return "rebase-or-fast-forward"
    return "undetermined"


def enrich(url: str, fragment_ids: list[str]) -> dict:
    match = PR_URL.fullmatch(url)
    if not match:
        raise ValueError(f"Not a pull request URL: {url}")
    owner, repo, number = match.groups()
    prefix = f"/repos/{owner}/{repo}"
    pr = api_get(f"{prefix}/pulls/{number}")
    if not isinstance(pr, dict):
        raise ValueError(f"Unexpected pull response for {url}")
    pull_commits = api_get(f"{prefix}/pulls/{number}/commits?per_page=100")
    if not isinstance(pull_commits, list):
        raise ValueError(f"Unexpected commit list for {url}")
    merge_sha = pr.get("merge_commit_sha")
    final = api_get(f"{prefix}/commits/{merge_sha}") if merge_sha else {}
    if not isinstance(final, dict):
        final = {}

    final_record = commit_record(final) if final else {}
    pull_records = [commit_record(item) for item in pull_commits]
    final_trailers = final_record.get("coauthor_trailers", [])
    pull_trailers = [trailer for item in pull_records for trailer in item.get("coauthor_trailers", [])]
    return {
        "pull_request_url": url,
        "achievement_fragment_ids": fragment_ids,
        "github_linked_as_pair_event": True,
        "merged_at": pr.get("merged_at"),
        "author_login": (pr.get("user") or {}).get("login"),
        "merged_by_login": (pr.get("merged_by") or {}).get("login"),
        "merge_commit_sha": merge_sha,
        "pull_commit_count": len(pull_records),
        "merge_method_classification": classify_merge(pr, pull_commits, final),
        "pull_commits": pull_records,
        "final_default_branch_commit": final_record,
        "coauthor_trailers_in_pull_commits": pull_trailers,
        "coauthor_trailers_in_final_commit": final_trailers,
        "final_history_preserves_coauthor_trailer": bool(final_trailers),
        "limitations": [
            "GitHub links this pull request from an achievement fragment, but the fragment does not expose its internal attributed count.",
            "The merge-method classification is derived from public commit topology and does not reveal every internal qualification filter.",
        ],
    }


def main() -> int:
    payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    candidates: dict[str, list[str]] = {}
    for record in payload.get("records", []):
        if record.get("achievement_slug") != "pair-extraordinaire" or record.get("status") != "fetched":
            continue
        for link in record.get("github_links", []):
            if PR_URL.fullmatch(link):
                candidates.setdefault(link, []).append(str(record["id"]))

    enriched: list[dict] = []
    for url, fragment_ids in sorted(candidates.items()):
        try:
            enriched.append(enrich(url, sorted(fragment_ids)))
        except (HTTPError, URLError, TimeoutError, ValueError) as error:
            enriched.append({
                "pull_request_url": url,
                "achievement_fragment_ids": sorted(fragment_ids),
                "status": "enrichment-failed",
                "error": str(error),
            })

    payload["pair_linked_pull_requests"] = enriched
    payload["pair_merge_evidence_summary"] = {
        "linked_pull_request_count": len(enriched),
        "merge_methods": sorted({item.get("merge_method_classification") for item in enriched if item.get("merge_method_classification")}),
        "final_trailer_preserved_count": sum(item.get("final_history_preserves_coauthor_trailer") is True for item in enriched),
        "enrichment_failure_count": sum(item.get("status") == "enrichment-failed" for item in enriched),
        "automatic_canonical_mutation": False,
    }
    SNAPSHOT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Enriched {len(enriched)} Pair Extraordinaire pull requests.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
