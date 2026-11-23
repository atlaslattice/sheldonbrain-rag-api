"""NFC-collision regressions for source-only Ariadne JSON intake."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.ariadne_bridge import load_strict


class NFCSourceKeyTests(unittest.TestCase):
    def test_escaped_decomposed_and_composed_same_object_rejected(self):
        with self.assertRaises(ValueError):
            load_strict(r'{"e\u0301":1,"\u00e9":2}')

    def test_nested_alias_is_rejected(self):
        with self.assertRaises(ValueError):
            load_strict(r'{"outer":{"e\u0301":1,"\u00e9":2}}')

    def test_literal_and_escaped_composed_alias_rejected(self):
        with self.assertRaises(ValueError):
            load_strict(r'{"é":1,"\u00e9":2}')

    def test_original_decomposed_key_bytes_are_not_silently_normalized(self):
        result = load_strict(r'{"e\u0301":1}')
        self.assertIn("e\u0301", result)
        self.assertNotIn("\u00e9", result)

    def test_unrelated_keys_preserved(self):
        self.assertEqual(load_strict(r'{"e\u0301":1,"x":2}')["x"],2)

    def test_exact_duplicate_remains_rejected(self):
        with self.assertRaises(ValueError):
            load_strict('{"id":1,"id":2}')


if __name__ == "__main__":
    unittest.main()
