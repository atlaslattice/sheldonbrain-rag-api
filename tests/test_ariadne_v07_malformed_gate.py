"""Source-equivalent negative review of public frozen-topic classifier only.
Never verifies original Ariadne private bytes, issuer, rights or host integration.
"""
import copy
import unittest
from tools.ariadne_v07_adapter import V07_SOURCE_SHA256, classify_frozen_topic

TOPIC={'topic_id':'T10018','top1_coordinate':'H01.S01.N05',
       'top1_node_title':'Gas and plasma physics',
       'source_url':'https://openalex.org/topics/T10018'}

def fixture():
    return {'registry':{'edition':'Ariadne v0.7','records':[
        {'coordinate':'H01.S01.N05','node_name':'Gas and plasma physics',
         'source_node_sha256':'a'*64}]},'original_sha256':V07_SOURCE_SHA256}

class FrozenTopicMalformedTests(unittest.TestCase):
    def hold(self, prepared):
        self.assertEqual(classify_frozen_topic(TOPIC, prepared),
                         {'state':'HOLD','authority_effect':'NONE'})
    def test_valid_synthetic_remains_unverified_candidate(self):
        out=classify_frozen_topic(TOPIC,fixture())
        self.assertEqual(out['state'],'CANDIDATE_CLASSIFICATION')
        self.assertIs(out['publisher_attested'],False)
        self.assertEqual(out['semantic_adjudication'],'NOT_PERFORMED')
    def test_malformed_registry_non_object(self):
        for value in (None, [], 5, 'bad'):
            with self.subTest(value=value): self.hold({'registry':value})
    def test_malformed_rows(self):
        for value in (None, 3, {}, 'bad', [1], [{'coordinate':'H01.S01.N05'}]):
            with self.subTest(value=repr(value)):
                x=fixture();x['registry']['records']=value;self.hold(x)
    def test_duplicate_coordinate_rejected(self):
        x=fixture();x['registry']['records']*=2;self.hold(x)
    def test_oversized_rows_bounded(self):
        x=fixture();x['registry']['records']*=1729;self.hold(x)
    def test_wrong_original_pin(self):
        x=fixture();x['original_sha256']='0'*64;self.hold(x)
    def test_wrong_node_hash(self):
        x=fixture();x['registry']['records'][0]['source_node_sha256']='bad';self.hold(x)
    def test_wrong_edition(self):
        x=fixture();x['registry']['edition']='legacy';self.hold(x)
    def test_zero_based_coordinate_rejected(self):
        x=fixture();x['registry']['records'][0]['coordinate']='H00.S00.N00';self.hold(x)
    def test_forged_source_remains_caller_unverified(self):
        x=fixture();x['registry']['records'][0]['node_name']='fictional sensor'
        topic=dict(TOPIC,top1_node_title='fictional sensor')
        out=classify_frozen_topic(topic,x)
        self.assertEqual(out['state'],'CANDIDATE_CLASSIFICATION')
        self.assertIs(out['publisher_attested'],False)

if __name__ == '__main__':
    unittest.main()
