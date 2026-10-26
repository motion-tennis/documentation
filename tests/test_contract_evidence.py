"""Freshness checks must reject stale, partial and incomplete source manifests."""

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_contract_evidence import contract_sources, evidence_errors


class EvidenceFreshnessTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for name in ("spec/motion.proto", "spec/reference-profile.json",
                     "scripts/match_contract.py", "scripts/contract/check_contract.py",
                     "tests/match/test_match_contract.py"):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture\n")
        sources = {name: hashlib.sha256(path.read_bytes()).hexdigest()
                   for name, path in contract_sources(self.root).items()}
        self.report = {"status": "passed_offline_contract_checks",
                       "semantic_checks": {"status": "passed", "tests": 1},
                       "source_sha256": sources,
                       "schema_sha256": sources["spec/motion.proto"],
                       "profile_sha256": sources["spec/reference-profile.json"]}
        self.save()

    def save(self):
        path = self.root / "evidence/s0-contract-report.json"
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(self.report))

    def test_matching_evidence_passes(self):
        self.assertEqual(evidence_errors(self.root), [])

    def test_changed_contract_invalidates_evidence(self):
        (self.root / "spec/motion.proto").write_text("changed\n")
        self.assertTrue(any("Stale" in error for error in evidence_errors(self.root)))

    def test_new_test_invalidates_inventory(self):
        (self.root / "tests/match/new_test.py").write_text("fixture\n")
        self.assertTrue(any("inventory" in error for error in evidence_errors(self.root)))

    def test_missing_source_is_rejected(self):
        (self.root / "scripts/match_contract.py").unlink()
        self.assertTrue(any("Missing" in error for error in evidence_errors(self.root)))

    def test_partial_codec_report_is_rejected(self):
        self.report["status"] = "codec_only_incomplete"
        self.report["semantic_checks"] = {"status": "not_run", "tests": 0}
        self.save()
        self.assertEqual(len(evidence_errors(self.root)), 2)

    def test_top_level_schema_identity_must_match(self):
        self.report["schema_sha256"] = "0" * 64
        self.save()
        self.assertTrue(any("identity" in error for error in evidence_errors(self.root)))


if __name__ == "__main__":
    unittest.main()
