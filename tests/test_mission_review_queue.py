from __future__ import annotations

from pathlib import Path
import importlib.util
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "build_mission_review_queue.py"
spec = importlib.util.spec_from_file_location("mission_review", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def policy() -> dict:
    return {
        "canonical_mutation_allowed": False,
        "dispositions": {
            "accept-evidence": {"queue_status": "accepted", "minimum_reviewers": 1, "promotion_proposal_allowed": True},
            "defer": {"queue_status": "deferred", "minimum_reviewers": 1, "promotion_proposal_allowed": False},
            "retain-inconclusive": {"queue_status": "retained-inconclusive", "minimum_reviewers": 1, "promotion_proposal_allowed": False},
            "request-correction": {"queue_status": "needs-correction", "minimum_reviewers": 1, "promotion_proposal_allowed": False},
            "reject": {"queue_status": "rejected", "minimum_reviewers": 1, "promotion_proposal_allowed": False}
        },
        "required_checklist": [
            "relationship_valid", "sources_public", "required_evidence_complete", "controls_credible",
            "limitations_complete", "privacy_safe", "safeguards_compliant", "timing_valid",
            "contradictions_addressed", "duplication_checked"
        ],
        "promotion_requirements": {
            "observed": {"rule_id": "ADJ-R01", "minimum_reviewers": 2, "minimum_unconflicted_reviewers": 1},
            "confirmed": {"rule_id": "ADJ-R02", "minimum_reviewers": 2, "minimum_unconflicted_reviewers": 1},
            "official": {"rule_id": "ADJ-R03", "minimum_reviewers": 2, "minimum_unconflicted_reviewers": 1}
        },
        "conflict_values": ["none", "participant", "repository-maintainer", "claim-author", "other-disclosed"],
        "publication_rules": ["a", "b", "c", "d", "e"],
        "schema_version": "1.0.0",
        "packet_directory": "triage/mission-drafts",
        "review_directory": "reviews/mission"
    }


def mission() -> dict:
    return {
        "id": "MSN-003", "title": "Bracket the Quickdraw timing boundary", "achievement_slug": "quickdraw",
        "research_task_ids": ["RSH-001"], "claim_ids": ["CLM-003"], "contradiction_ids": ["CTR-001"],
        "required_evidence": ["public_object_url", "elapsed_seconds"],
        "promotion_targets": [{"claim_id": "CLM-003", "target_level": "confirmed"}]
    }


def packet() -> dict:
    return {
        "schema_version": "1.0.0", "id": "MISSION-DRAFT-ISSUE-123",
        "source_issue": "https://github.com/Conroy1988/Achievements/issues/123", "submitted_by": "Conroy1988",
        "submitted_at": "2026-07-22T20:00:00Z", "mission_id": "MSN-003", "mission_rank": 3,
        "mission_title": "Bracket the Quickdraw timing boundary", "mission_status_at_submission": "participant-needed",
        "achievement_slug": "quickdraw", "claim_id": "CLM-003", "contradiction_id": "CTR-001",
        "research_task_id": "RSH-001", "protocol_ids": ["LAB-001"], "observation_date": "2026-07-22",
        "result": "awarded", "repository_visibility": "public", "qualifying_event_time_utc": "2026-07-22T19:55:00Z",
        "first_badge_visibility_time_utc": "2026-07-22T20:00:00Z",
        "source_urls": ["https://github.com/Conroy1988/Achievements/issues/123"],
        "required_evidence": {"public_object_url": "https://github.com/example/repo/issues/1", "elapsed_seconds": "4"},
        "environment_and_controls": "A controlled public repository observation with recorded timing.",
        "limitations": "One account and one positive observation.", "safeguard_status": "declared-compliant",
        "privacy_status": "automated-screening-passed", "reviewer_decision": "pending-human-review"
    }


def review() -> dict:
    return {
        "schema_version": "1.0.0", "id": "MRV-2026-001", "packet_id": "MISSION-DRAFT-ISSUE-123",
        "mission_id": "MSN-003", "source_packet": "triage/mission-drafts/issue-123.json",
        "disposition": "accept-evidence", "reviewed_at": "2026-07-22T21:00:00Z",
        "reviewers": [
            {"login": "ReviewerOne", "conflict": "none", "notes": "Independent review."},
            {"login": "ReviewerTwo", "conflict": "repository-maintainer", "notes": "Maintainer review with disclosed role."}
        ],
        "checklist": {key: True for key in policy()["required_checklist"]},
        "rationale": "The public packet satisfies the mission controls and the published confirmed-level adjudication requirements.",
        "promotion_proposal": {"target_claim_id": "CLM-003", "target_level": "confirmed", "applied_rule_ids": ["ADJ-R02"]},
        "canonical_mutation": False
    }


class MissionReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = policy()
        self.missions = {"MSN-003": mission()}
        self.claims = {"CLM-003": {"id": "CLM-003"}}
        self.contradictions = {"CTR-001": {"id": "CTR-001"}}
        self.rules = {"ADJ-R01", "ADJ-R02", "ADJ-R03"}
        self.review_path = module.ROOT / "reviews/mission/MRV-2026-001.json"
        self.packet_path = module.ROOT / "triage/mission-drafts/issue-123.json"

    def test_empty_queue_is_valid_launch_state(self) -> None:
        output = module.build_queue(self.policy, [], [])
        self.assertEqual(output["count"], 0)
        self.assertEqual(output["metrics"]["automatic_canonical_mutation_count"], 0)

    def test_valid_confirmed_proposal_passes(self) -> None:
        errors = module.validate_review(self.review_path, review(), packet(), self.policy, self.missions, self.claims, self.rules)
        self.assertEqual(errors, [])

    def test_promotion_requires_two_reviewers(self) -> None:
        candidate = review()
        candidate["reviewers"] = candidate["reviewers"][:1]
        errors = module.validate_review(self.review_path, candidate, packet(), self.policy, self.missions, self.claims, self.rules)
        self.assertTrue(any("required reviewers" in item for item in errors))

    def test_canonical_mutation_is_rejected(self) -> None:
        candidate = review()
        candidate["canonical_mutation"] = True
        errors = module.validate_review(self.review_path, candidate, packet(), self.policy, self.missions, self.claims, self.rules)
        self.assertTrue(any("canonical_mutation" in item for item in errors))

    def test_failed_checklist_blocks_promotion(self) -> None:
        candidate = review()
        candidate["checklist"]["contradictions_addressed"] = False
        errors = module.validate_review(self.review_path, candidate, packet(), self.policy, self.missions, self.claims, self.rules)
        self.assertTrue(any("checklist item" in item for item in errors))

    def test_packet_relationship_mismatch_is_rejected(self) -> None:
        candidate = packet()
        candidate["claim_id"] = "CLM-999"
        errors = module.validate_packet(self.packet_path, candidate, self.missions, self.claims, self.contradictions)
        self.assertTrue(any("claim does not match mission" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
