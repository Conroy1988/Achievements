from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import json
import sys
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "triage_mission_submission.py"
spec = importlib.util.spec_from_file_location("triage_mission_submission", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def issue_body(
    *,
    mission: str = "MSN-001",
    task: str = "RSH-009",
    claim: str = "CLM-005",
    contradiction: str = "CTR-004",
    achievement: str = "pair-extraordinaire",
    evidence: str | None = None,
    environment: str = "Public repository; squash merge; two consenting real contributors.",
) -> str:
    evidence = evidence or "\n".join([
        "public_pull_request_url: https://github.com/example/repo/pull/1",
        "final_commit_url: https://github.com/example/repo/commit/abc",
        "merge_method: squash",
        "trailer_preserved: yes",
        "account_linkage_state: linked",
        "achievement_state_before: absent",
        "achievement_state_after: visible",
        "first_visible_time_utc_or_cutoff: 2026-07-23T12:00:00Z",
    ])
    fields = {
        "Mission ID": mission,
        "Research task ID": task,
        "Claim ID": claim,
        "Contradiction ID": contradiction,
        "Achievement": achievement,
        "Observation date": "2026-07-23",
        "Result": "Awarded",
        "Repository visibility": "Public",
        "Qualifying event time (UTC)": "2026-07-23T11:00:00Z",
        "First badge visibility time (UTC)": "2026-07-23T12:00:00Z",
        "Source URLs": "https://github.com/example/repo/pull/1",
        "Required evidence values": evidence,
        "Environment and controls": environment,
        "Limitations and failed attempts": "Single observation; processing delay remains uncertain.",
        "Safeguard declaration": module.SAFEGUARD_TEXT,
        "Privacy declaration": module.PRIVACY_TEXT,
        "Consent": module.CONSENT_TEXT,
    }
    return "\n\n".join(f"### {label}\n\n{value}" for label, value in fields.items())


class MissionSubmissionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "api").mkdir()
        (self.root / "data").mkdir()
        missions = {
            "missions": [
                {
                    "id": "MSN-001",
                    "rank": 1,
                    "title": "Pair mission",
                    "status": "participant-needed",
                    "achievement_slug": "pair-extraordinaire",
                    "claim_ids": ["CLM-005", "CLM-006"],
                    "contradiction_ids": ["CTR-004"],
                    "research_task_ids": ["RSH-009", "RSH-010"],
                    "protocol_ids": ["LAB-003"],
                    "required_evidence": [
                        "public_pull_request_url",
                        "final_commit_url",
                        "merge_method",
                        "trailer_preserved",
                        "account_linkage_state",
                        "achievement_state_before",
                        "achievement_state_after",
                        "first_visible_time_utc_or_cutoff",
                    ],
                },
                {
                    "id": "MSN-002",
                    "rank": 2,
                    "title": "Pull Shark hold",
                    "status": "scheduled",
                    "achievement_slug": "pull-shark",
                    "claim_ids": ["CLM-001", "CLM-002"],
                    "contradiction_ids": ["CTR-003"],
                    "research_task_ids": ["RSH-003", "RSH-008"],
                    "protocol_ids": [],
                    "required_evidence": [
                        "achievement_detail_url",
                        "observed_time_utc",
                        "displayed_tier_or_absence",
                        "contributing_event_links_if_exposed",
                        "processing_interval",
                        "support_escalation_package_if_absent",
                    ],
                    "no_action_before": "2026-07-22T20:00:00+01:00",
                },
            ]
        }
        queue = {"tasks": [{"id": "RSH-009"}, {"id": "RSH-010"}, {"id": "RSH-003"}, {"id": "RSH-008"}]}
        claims = {"claims": [
            {"id": "CLM-001"}, {"id": "CLM-002"}, {"id": "CLM-005"}, {"id": "CLM-006"}
        ]}
        contradictions = {"records": [{"id": "CTR-003"}, {"id": "CTR-004"}]}
        for path, payload in (
            ("api/acquisition-missions.json", missions),
            ("data/research-queue.json", queue),
            ("data/claims.json", claims),
            ("data/contradictions.json", contradictions),
        ):
            (self.root / path).write_text(json.dumps(payload), encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def event(self, body: str, updated_at: str = "2026-07-23T12:30:00Z") -> dict:
        return {
            "issue": {
                "number": 42,
                "title": "[Mission Evidence] test",
                "body": body,
                "html_url": "https://github.com/example/repo/issues/42",
                "updated_at": updated_at,
                "created_at": updated_at,
                "user": {"login": "tester"},
            }
        }

    def test_valid_submission_is_accepted(self) -> None:
        result, packet, _ = module.triage(self.event(issue_body()), self.root)
        self.assertEqual(result["status"], "accepted-for-human-review")
        self.assertIsNotNone(packet)
        self.assertEqual(packet["mission_id"], "MSN-001")
        self.assertEqual(len(packet["required_evidence"]), 8)

    def test_missing_required_evidence_is_blocked(self) -> None:
        body = issue_body(evidence="public_pull_request_url: https://github.com/example/repo/pull/1")
        result, packet, _ = module.triage(self.event(body), self.root)
        self.assertEqual(result["status"], "blocked")
        self.assertIsNone(packet)
        self.assertTrue(any("Missing required evidence keys" in item for item in result["errors"]))

    def test_relationship_mismatch_is_blocked(self) -> None:
        body = issue_body(task="RSH-003")
        result, _, _ = module.triage(self.event(body), self.root)
        self.assertTrue(any("Research task is not linked" in item for item in result["errors"]))

    def test_scheduled_mission_before_hold_is_blocked(self) -> None:
        evidence = "\n".join([
            "achievement_detail_url: https://github.com/example?achievement=pull-shark",
            "observed_time_utc: 2026-07-21T12:00:00Z",
            "displayed_tier_or_absence: absent",
            "contributing_event_links_if_exposed: none",
            "processing_interval: 48 hours",
            "support_escalation_package_if_absent: prepared",
        ])
        body = issue_body(
            mission="MSN-002",
            task="RSH-003",
            claim="CLM-002",
            contradiction="CTR-003",
            achievement="pull-shark",
            evidence=evidence,
        )
        result, _, _ = module.triage(self.event(body, "2026-07-21T12:00:00Z"), self.root)
        self.assertTrue(any("cannot be submitted before" in item for item in result["errors"]))

    def test_sensitive_value_is_blocked(self) -> None:
        body = issue_body(environment="Public repository password=supersecret and normal settings.")
        result, _, _ = module.triage(self.event(body), self.root)
        self.assertTrue(any("Automated privacy screening detected" in item for item in result["errors"]))


if __name__ == "__main__":
    unittest.main()
