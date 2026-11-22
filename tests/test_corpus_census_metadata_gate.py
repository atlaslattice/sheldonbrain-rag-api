"""Synthetic-only negative and positive tests; no user corpus reads."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from census.metadata_gate import validate_manifest


BASE = {
    "artifact_id": "synthetic:alpha", "revision_id": "r1",
    "source_revision": "rev1", "source_locator": "synthetic:sample1",
    "source_mode": "work", "source_kind": "synthetic", "visibility": "synthetic",
    "rights_status": "rights_reviewed", "rights_evidence_ref": "synthetic:permission1",
    "allowed_purposes": ["metadata_census"], "raw_export_status": "not_fetched",
    "retention_policy": "synthetic:none",
}


def encode(records):
    return json.dumps({"schema_version": "0.1.0", "records": records}, separators=(",", ":")).encode()


class MetadataGateTests(unittest.TestCase):
    def setUp(self):
        self.row = copy.deepcopy(BASE)

    def verdict(self, rows=None):
        return validate_manifest(encode([self.row] if rows is None else rows))

    def held(self, code):
        result = self.verdict()
        self.assertEqual(result["disposition"], "HOLD")
        self.assertIn(code, [x["code"] for x in result["errors"]])
        return result

    def test_synthetic_metadata_only_never_grants_ingest(self):
        result = self.verdict()
        self.assertEqual(result["disposition"], "REVIEWABLE_CANDIDATE")
        self.assertEqual(result["records_seen"], 1)
        self.assertEqual(result["records_read_from_sources"], 0)
        self.assertEqual(result["records_indexed"], 0)
        for name in ("can_ingest", "rights_authenticated", "canon", "deployed"):
            self.assertIs(result[name], False)

    def test_path_traversal_locator_is_held_without_leak(self):
        for locator in ("../private", "synthetic:../secret", "/mnt/../protected", "safe/./alias"):
            with self.subTest(locator=locator):
                self.row["source_locator"] = locator
                result = self.held("UNSAFE_SOURCE_LOCATOR")
                self.assertNotIn(locator, json.dumps(result))

    def test_private_body_field_is_rejected_and_not_echoed(self):
        secret = "DO_NOT_PRINT_PRIVATE_SENTINEL"
        self.row["content"] = secret
        result = self.held("UNRECOGNIZED_OR_BODY_FIELD")
        self.assertNotIn(secret, json.dumps(result))
        self.assertNotIn(self.row["source_locator"], json.dumps(result))

    def test_duplicate_json_keys_fail_closed(self):
        raw = b'{"schema_version":"0.1.0","records":[],"records":[]}'
        self.assertEqual(validate_manifest(raw)["disposition"], "HOLD")

    def test_non_finite_json_numbers_fail_closed(self):
        self.row["house_scores"] = [float("nan")] * 12
        raw = encode([self.row])
        self.assertIn("INVALID_JSON_OR_DUPLICATE_KEY", [x["code"] for x in validate_manifest(raw)["errors"]])

    def test_non_work_modes_are_not_imported(self):
        for mode in ("play", "social", "imagine", "quiet", "dream", "habitat", "brain", "palace"):
            with self.subTest(mode=mode):
                self.row["source_mode"] = mode
                self.held("NON_WORK_SOURCE_MODE")

    def test_private_visibility_is_held(self):
        self.row["visibility"] = "private"
        self.held("VISIBILITY_HOLD")

    def test_absent_rights_and_unauthorized_purpose_are_held(self):
        self.row["rights_status"] = "unknown"
        self.row["allowed_purposes"] = ["embedding"]
        self.held("RIGHTS_REVIEW_HOLD")
        self.held("PURPOSE_HOLD")

    def test_raw_body_fetch_status_is_held(self):
        self.row["raw_export_status"] = "complete"
        self.held("BODY_FETCH_OUT_OF_SCOPE")

    def test_score_vector_requires_explicit_taxonomy_edition(self):
        self.row["house_scores"] = [0.5] * 12
        self.held("TAXONOMY_EDITION_MISSING")
        self.row["taxonomy_edition"] = "edition:v1"
        self.assertEqual(self.verdict()["disposition"], "REVIEWABLE_CANDIDATE")

    def test_optional_edition_never_accepts_embedded_body(self):
        # Before hardening, all of these passed as REVIEWABLE_CANDIDATE
        # if neither score field was present, including a dict carrying text.
        for unsafe in ({"body": "PRIVATE_FIXTURE_DO_NOT_PRINT"}, ["private"],
                       12, True, "", "a b", None):
            with self.subTest(kind=type(unsafe).__name__):
                self.row["taxonomy_edition"] = unsafe
                result = self.held("INVALID_TAXONOMY_EDITION")
                self.assertNotIn("PRIVATE_FIXTURE_DO_NOT_PRINT", json.dumps(result))
        self.row["taxonomy_edition"] = "ariadne/v0.7"
        self.assertEqual(self.verdict()["disposition"], "REVIEWABLE_CANDIDATE")

    def test_explicit_null_score_vectors_are_not_accepted_as_absent(self):
        self.row["taxonomy_edition"] = "ariadne/v0.7"
        for field, code in (("house_scores", "INVALID_HOUSE_VECTOR"),
                            ("node_scores", "INVALID_NODE_VECTOR")):
            with self.subTest(field=field):
                self.row[field] = None
                self.held(code)
                self.row.pop(field)

    def test_boolean_house_score_is_not_numeric_evidence(self):
        self.row.update({"taxonomy_edition": "edition:v1", "house_scores": [0.5] * 11 + [True]})
        self.held("INVALID_HOUSE_VECTOR")

    def test_coordinate_bounds_and_duplicate_json_coordinates(self):
        self.row.update({"taxonomy_edition": "edition:v1", "node_scores": {"H12.S12.N12": 1.0}})
        self.assertEqual(self.verdict()["disposition"], "REVIEWABLE_CANDIDATE")
        self.row["node_scores"] = {"H13.S12.N12": 1.0}
        self.held("INVALID_NODE_VECTOR")

    def test_more_than_100_objects_is_held(self):
        rows = []
        for i in range(101):
            row = copy.deepcopy(BASE)
            row["artifact_id"] = f"synthetic:{i}"
            rows.append(row)
        result = self.verdict(rows)
        self.assertEqual(result["records_seen"], 101)
        self.assertIn("PILOT_LIMIT_EXCEEDED", [x["code"] for x in result["errors"]])

    def test_duplicate_artifact_revision_is_not_folded(self):
        self.held_from_two = self.verdict([copy.deepcopy(BASE), copy.deepcopy(BASE)])
        self.assertIn("DUPLICATE_ARTIFACT_REVISION", [x["code"] for x in self.held_from_two["errors"]])
        self.assertEqual(self.held_from_two["records_seen"], 2)

    def test_same_revision_id_different_artifact_is_preserved(self):
        second = copy.deepcopy(BASE)
        second["artifact_id"] = "synthetic:beta"
        self.assertEqual(self.verdict([BASE, second])["disposition"], "REVIEWABLE_CANDIDATE")

    def test_bad_utf8_and_wrong_root_are_held(self):
        self.assertEqual(validate_manifest(b"\xff")["disposition"], "HOLD")
        self.assertEqual(validate_manifest(b'[]')["disposition"], "HOLD")

    def test_unhashable_enum_fields_hold_instead_of_crashing(self):
        self.row["source_kind"] = []
        self.row["visibility"] = {"nested": "value"}
        self.held("INVALID_SOURCE_KIND")
        self.held("VISIBILITY_HOLD")

    def test_huge_integer_score_holds_without_float_overflow(self):
        self.row["taxonomy_edition"] = "edition:v1"
        self.row["house_scores"] = [0.5] * 11 + [10 ** 500]
        self.held("INVALID_HOUSE_VECTOR")

    def test_oversized_manifest_is_held_before_parsing(self):
        result = validate_manifest(b"x" * 1_048_577)
        self.assertEqual(result["disposition"], "HOLD")
        self.assertEqual(result["errors"][0]["code"], "MANIFEST_BYTES_EXCEEDED")

    def test_nested_duplicate_json_key_is_held(self):
        raw = b'{"schema_version":"0.1.0","records":[{"source_mode":"work","source_mode":"play"}]}'
        self.assertEqual(validate_manifest(raw)["disposition"], "HOLD")

    def test_cli_local_only_aggregate_and_exit_code(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "fixture.json"
            p.write_bytes(encode([BASE]))
            command = [sys.executable, "-m", "census.metadata_gate", str(p)]
            run = subprocess.run(command, check=False, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn('"records_seen": 1', run.stdout)
            self.assertNotIn("synthetic:sample1", run.stdout)
            p.write_bytes(b'{"records":[],"schema_version":"0.1.0","content":"X"}')
            blocked = subprocess.run(command, check=False, capture_output=True, text=True)
            self.assertEqual(blocked.returncode, 2)


if __name__ == "__main__":
    unittest.main()
