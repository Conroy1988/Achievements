from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import json
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "build_promotion_plans.py"
SPEC = importlib.util.spec_from_file_location("promotion_planner", MODULE_PATH)
planner = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(planner)


class PromotionPlannerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "reviews" / "mission").mkdir(parents=True)
        self.old_root = planner.ROOT
        planner.ROOT = self.root
        self.policy = {
            "schema_version": "1.0.0",
            "automatic_application_allowed": False,
            "eligible_queue_statuses": ["accepted"],
            "eligible_target_levels": ["observed", "confirmed", "official"],
            "evidence_level_order": ["unknown", "community-reported", "observed", "confirmed", "official"],
            "plan_statuses": ["ready-for-maintainer-review", "blocked"],
            "canonical_source_paths": ["a", "b", "c", "d", "e", "f"],
            "generated_output_paths": [f"generated-{index}" for index in range(10)],
            "required_preconditions": [f"precondition-{index}" for index in range(7)],
            "validation_commands": [f"command-{index}" for index in range(6)],
            "rollback_rules": [f"rollback-{index}" for index in range(5)],
            "publication_rules": [f"rule-{index}" for index in range(6)],
        }
        self.claims = {
            "claims": [
                {
                    "id": "CLM-003",
                    "achievement_slug": "quickdraw",
                    "claim_type": "trigger",
                    "evidence_level": "community-reported",
                }
            ]
        }

    def tearDown(self) -> None:
        planner.ROOT = self.old_root
        self.temp.cleanup()

    def write_review(self, review_id: str = "MRV-2026-001", target: str = "observed") -> str:
        path = self.root / "reviews" / "mission" / f"{review_id}.json"
        path.write_text(
            json.dumps(
                {
                    "id": review_id,
                    "packet_id": "MISSION-DRAFT-ISSUE-1",
                    "disposition": "accept-evidence",
                    "canonical_mutation": False,
                    "promotion_proposal": {
                        "target_level": target,
                        "target_claim_id": "CLM-003",
                        "applied_rule_ids": ["ADJ-R01"],
                    },
                }
            ),
            encoding="utf-8",
        )
        return str(path.relative_to(self.root))

    def queue_item(self, review_path: str, status: str = "accepted", target: str = "observed") -> dict:
        return {
            "packet_id": "MISSION-DRAFT-ISSUE-1",
            "mission_id": "MSN-003",
            "mission_title": "Bracket the Quickdraw timing boundary",
            "achievement_slug": "quickdraw",
            "claim_id": "CLM-003",
            "contradiction_id": "CTR-001",
            "research_task_id": "RSH-001",
            "source_issue": "https://github.com/Conroy1988/Achievements/issues/1",
            "review_path": review_path,
            "status": status,
            "promotion_target_level": target,
            "promotion_target_claim_id": "CLM-003",
            "canonical_mutation": False,
        }

    def payload(self, items: list[dict], automatic: int = 0) -> dict:
        return {
            "metrics": {
                "promotion_proposal_count": sum(item["promotion_target_level"] != "none" for item in items),
                "automatic_canonical_mutation_count": automatic,
            },
            "queue": items,
        }

    def test_empty_queue_produces_no_plans(self) -> None:
        plans, errors = planner.build_plans(self.policy, self.payload([]), self.claims)
        self.assertEqual(errors, [])
        self.assertEqual(plans, [])

    def test_valid_accepted_proposal_produces_ready_plan(self) -> None:
        review_path = self.write_review()
        plans, errors = planner.build_plans(self.policy, self.payload([self.queue_item(review_path)]), self.claims)
        self.assertEqual(errors, [])
        self.assertEqual(len(plans), 1)
        self.assertEqual(plans[0]["id"], "PPL-2026-001")
        self.assertEqual(plans[0]["status"], "ready-for-maintainer-review")
        self.assertFalse(plans[0]["automatic_application"])
        self.assertTrue(plans[0]["separate_pull_request_required"])

    def test_nonaccepted_promotion_is_rejected(self) -> None:
        review_path = self.write_review()
        plans, errors = planner.build_plans(
            self.policy,
            self.payload([self.queue_item(review_path, status="deferred")]),
            self.claims,
        )
        self.assertEqual(plans, [])
        self.assertTrue(any("not accepted" in error for error in errors))

    def test_duplicate_claim_proposals_are_rejected(self) -> None:
        first = self.write_review("MRV-2026-001")
        second = self.write_review("MRV-2026-002")
        second_item = self.queue_item(second)
        second_item["packet_id"] = "MISSION-DRAFT-ISSUE-2"
        review = json.loads((self.root / second).read_text(encoding="utf-8"))
        review["packet_id"] = "MISSION-DRAFT-ISSUE-2"
        (self.root / second).write_text(json.dumps(review), encoding="utf-8")
        plans, errors = planner.build_plans(
            self.policy,
            self.payload([self.queue_item(first), second_item]),
            self.claims,
        )
        self.assertEqual(len(plans), 1)
        self.assertTrue(any("duplicate active promotion proposal" in error for error in errors))

    def test_non_stronger_level_is_blocked(self) -> None:
        self.claims["claims"][0]["evidence_level"] = "observed"
        review_path = self.write_review(target="observed")
        plans, errors = planner.build_plans(self.policy, self.payload([self.queue_item(review_path)]), self.claims)
        self.assertEqual(errors, [])
        self.assertEqual(plans[0]["status"], "blocked")
        self.assertTrue(plans[0]["blockers"])

    def test_automatic_mutation_metric_fails_closed(self) -> None:
        plans, errors = planner.build_plans(self.policy, self.payload([], automatic=1), self.claims)
        self.assertEqual(plans, [])
        self.assertTrue(any("automatic canonical mutation" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
