"""Offline negative controls for the source-only Ariadne registry type boundary.

Synthetic data ONLY. A self-matching digest confirms structural integrity, not
Ariadne source authenticity, host identity, CANON or semantic approval.
"""
import copy
import unittest

from tools.ariadne_bridge import digest, verify_registry


def fixture():
    rows = []
    for h in range(1, 13):
        for s in range(1, 13):
            for n in range(1, 13):
                index = len(rows)
                rows.append({
                    "coordinate": f"H{h:02d}.S{s:02d}.N{n:02d}",
                    "house_name": "SYNTHETIC_HOUSE",
                    "sphere_name": "SYNTHETIC_SPHERE",
                    "node_name": "SYNTHETIC_NODE",
                    "node_kind": ("DOMAIN_SPECIALIZATION" if index < 1008
                                  else "META_METHOD_AUDIT"),
                    "source_node_sha256": "a" * 64,
                })
    return {"edition": "fixture-v1", "records": rows}


class TypedRegistryGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = fixture()

    def test_positive_structure_not_external_attestation(self):
        data = copy.deepcopy(self.original)
        result = verify_registry(data, digest(data), "fixture-v1")
        self.assertEqual(result["state"], "PINNED_REGISTRY_VALID")
        self.assertEqual(result["digest"], digest(data))
        self.assertNotIn("host_attested", result)
        self.assertNotIn("canon", result)

    def test_non_object_roots_explicit_hold(self):
        for value in (None, [], True, "not-json", 1):
            with self.subTest(value=repr(value)):
                with self.assertRaises(ValueError):
                    verify_registry(value, "a" * 64, "fixture-v1")

    def test_non_string_pin_and_edition_hold(self):
        for value in (None, [], {}, True, 123):
            with self.subTest(value=repr(value)):
                with self.assertRaises(ValueError):
                    verify_registry(self.original, value, "fixture-v1")
                with self.assertRaises(ValueError):
                    verify_registry(self.original, digest(self.original), value)

    def test_non_object_row_fail_closed(self):
        for value in (None, [], 1, "candidate", True):
            with self.subTest(value=repr(value)):
                data = copy.deepcopy(self.original)
                data["records"][0] = value
                with self.assertRaisesRegex(ValueError, "INVALID_REGISTRY"):
                    verify_registry(data, digest(data), "fixture-v1")

    def test_bad_coordinate_type_fail_closed(self):
        for value in (None, [], {}, 42, True):
            with self.subTest(value=repr(value)):
                data = copy.deepcopy(self.original)
                data["records"][0]["coordinate"] = value
                with self.assertRaisesRegex(ValueError, "INVALID_REGISTRY"):
                    verify_registry(data, digest(data), "fixture-v1")

    def test_bad_source_hash_holds(self):
        data = copy.deepcopy(self.original)
        data["records"][0]["source_node_sha256"] = []
        with self.assertRaises(ValueError):
            verify_registry(data, digest(data), "fixture-v1")

    def test_duplicate_coordinate_holds(self):
        data = copy.deepcopy(self.original)
        data["records"][1]["coordinate"] = data["records"][0]["coordinate"]
        with self.assertRaises(ValueError):
            verify_registry(data, digest(data), "fixture-v1")

    def test_pinned_but_false_semantic_names_still_structurally_valid(self):
        # Expected: validates only shape and digest. Demonstrates the remaining
        # external provenance gate, without making a scientific/semantic claim.
        data = copy.deepcopy(self.original)
        data["records"][0]["node_name"] = "FICTIONAL_NAME_NOT_ATTESTED"
        result = verify_registry(data, digest(data), "fixture-v1")
        self.assertEqual(result["state"], "PINNED_REGISTRY_VALID")


if __name__ == "__main__":
    unittest.main()
