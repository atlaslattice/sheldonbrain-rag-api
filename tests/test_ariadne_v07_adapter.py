"""No private source bytes committed. Set ATLAS_ORIGINAL_JSON for full local source test."""
import os, pathlib, unittest
from tools.ariadne_v07_adapter import adapt_original,classify_frozen_topic,strict_json,V07_SOURCE_SHA256
class OriginalAdapterTests(unittest.TestCase):
    def test_pin_is_authoritative(self):
        self.assertEqual(V07_SOURCE_SHA256,'07533cf7a6b6f567259962bf73efee9b22b47cbacb429499787800e07864e5a6')
    def test_source_bytes_required(self):
        with self.assertRaises(ValueError):adapt_original('not-bytes',V07_SOURCE_SHA256)
    def test_wrong_sha_rejected(self):
        with self.assertRaises(ValueError):adapt_original(b'{}','0'*64)
    def test_fake_edition_rejected(self):
        with self.assertRaises(ValueError):adapt_original(b'{}',V07_SOURCE_SHA256,'Ariadne v0.8')
    def test_duplicate_json_rejected(self):
        with self.assertRaises(ValueError):strict_json('{"a":1,"a":2}')
    def test_invalid_json_constant_rejected(self):
        with self.assertRaises(ValueError):strict_json('{"x":NaN}')
    def test_caller_review_cannot_promote(self):
        r={'registry':{'edition':'Ariadne v0.7','records':[{'coordinate':'H01.S01.N05','node_name':'Gas and plasma physics','source_node_sha256':'a'*64}]},'original_sha256':V07_SOURCE_SHA256}
        topic={'topic_id':'T10018','top1_coordinate':'H01.S01.N05','top1_node_title':'Gas and plasma physics','source_url':'https://openalex.org/topics/T10018','review_state':'INDEPENDENTLY_ADJUDICATED','rights_at_release':'yes'}
        out=classify_frozen_topic(topic,r)
        self.assertEqual(out['state'],'CANDIDATE_CLASSIFICATION')
        self.assertEqual(out['authority_effect'],'NONE')
    def test_url_mismatch_held(self):
        r={'registry':{'edition':'Ariadne v0.7','records':[{'coordinate':'H01.S01.N05','node_name':'Gas and plasma physics','source_node_sha256':'a'*64}]},'original_sha256':V07_SOURCE_SHA256}
        x={'topic_id':'T10018','top1_coordinate':'H01.S01.N05','top1_node_title':'Gas and plasma physics','source_url':'file:///secret'}
        self.assertEqual(classify_frozen_topic(x,r)['state'],'HOLD')
    @unittest.skipUnless(os.environ.get('ATLAS_ORIGINAL_JSON'),'Set ATLAS_ORIGINAL_JSON to run private-source exact reconciliation')
    def test_authentic_1728_source_when_supplied(self):
        b=pathlib.Path(os.environ['ATLAS_ORIGINAL_JSON']).read_bytes()
        result=adapt_original(b,V07_SOURCE_SHA256)
        self.assertEqual(len(result['registry']['records']),1728)
        self.assertEqual(result['registry']['records'][4]['node_name'],'Gas and plasma physics')
if __name__=='__main__':unittest.main()
