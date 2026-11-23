"""Pin strict-source lexical regression cases against the public adapter.

These are local parser contract checks, not publisher authentication or a
host-verified Work/tenant source boundary. Original private bytes are omitted.
"""
import math
import unittest
from tools.ariadne_v07_adapter import strict_json, classify_frozen_topic
from tests.test_ariadne_v07_malformed_gate import TOPIC, fixture

class StrictAriadneJsonTests(unittest.TestCase):
    def fails(self,raw):
        with self.assertRaises(ValueError):strict_json(raw)

    def test_reject_exponent_overflow(self):
        self.fails('{"x":1e400}')
    def test_reject_nonzero_underflow(self):
        self.fails('{"x":1e-400}')
    def test_reject_long_mantissa_rounding(self):
        self.fails('{"x":1.234567890123456789}')
    def test_reject_NFC_aliased_keys(self):
        self.fails('{"e\\u0301":1,"\\u00e9":2}')
    def test_reject_nested_NFC_aliased_keys(self):
        self.fails('{"safe":{"e\\u0301":1,"\\u00e9":2}}')
    def test_reject_exact_duplicate_keys(self):
        self.fails('{"x":1,"x":2}')
    def test_reject_nonstandard_constants(self):
        for token in ('NaN','Infinity','-Infinity'):
            with self.subTest(token=token): self.fails('{"x":'+token+'}')
    def test_preserve_safe_decimal_float(self):
        self.assertEqual(strict_json('{"x":0.1,"y":-0.25}'),{'x':0.1,'y':-0.25})
    def test_preserve_exact_large_integer(self):
        self.assertEqual(strict_json('{"x":123456789012345678901234567890}')['x'],123456789012345678901234567890)
    def test_preserve_noncolliding_raw_key_forms(self):
        result=strict_json('{"e\\u0301":1,"e":2}')
        self.assertEqual(result['e\u0301'],1)
        self.assertEqual(result['e'],2)
    def test_original_classifier_still_unverified(self):
        result=classify_frozen_topic(TOPIC,fixture())
        self.assertEqual(result['state'],'CANDIDATE_CLASSIFICATION')
        self.assertIs(result['publisher_attested'],False)

if __name__=='__main__':unittest.main()
