import unittest
from tools.ariadne_bridge import *
class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.index={"H01.S01.N01":{}}
        self.link={"edition":"v1","coordinate":"H01.S01.N01","relation":"RELATED","source_uri":"https://openalex.org/W123","source_version":"2026-11-22","source_digest":"a"*64,"review_state":"SOURCE_TRACED"}
    def test_budget(self): self.assertEqual(sum(v for v in macroturn_plan().values() if isinstance(v,int)),20)
    def test_nonwork_unperformed(self): self.assertEqual(macroturn_plan()["nonwork_state"],"RESERVED_NOT_PERFORMED")
    def test_duplicate(self):
        with self.assertRaises(ValueError): load_strict('{"a":1,"a":2}')
    def test_nonfinite(self):
        with self.assertRaises(ValueError): load_strict('{"a":NaN}')
    def test_digest_order(self): self.assertEqual(digest({"a":1,"b":2}),digest({"b":2,"a":1}))
    def test_unpinned(self):
        with self.assertRaises(ValueError): verify_registry({"edition":"v1","records":[]},"","v1")
    def test_count(self):
        r={"edition":"v1","records":[]}
        with self.assertRaises(ValueError): verify_registry(r,digest(r),"v1")
    def test_edition(self):
        r={"edition":"v1","records":[]}
        with self.assertRaises(ValueError): verify_registry(r,digest(r),"v2")
    def test_candidate(self): self.assertEqual(assess_link(self.link,self.index,"v1")["state"],"CANDIDATE")
    def test_link_edition(self): self.assertEqual(assess_link(self.link,self.index,"v2")["state"],"HOLD")
    def test_unknown_node(self): self.assertEqual(assess_link(self.link,{},"v1")["state"],"HOLD")
    def test_relation(self):
        self.link["relation"]="CANON";self.assertEqual(assess_link(self.link,self.index,"v1")["state"],"HOLD")
    def test_uri(self):
        self.link["source_uri"]="file:///private";self.assertEqual(assess_link(self.link,self.index,"v1")["state"],"HOLD")
    def test_version(self):
        del self.link["source_version"];self.assertEqual(assess_link(self.link,self.index,"v1")["state"],"HOLD")
    def test_missing_review(self):
        self.link["review_state"]="INDEPENDENTLY_ADJUDICATED";self.assertEqual(assess_link(self.link,self.index,"v1")["state"],"HOLD")
    def test_false_friend_no_match(self):
        self.link["relation"]="NO_MATCH"
        self.assertEqual(assess_link(self.link,self.index,"v1")["state"],"REJECTED_SEMANTIC_MATCH")
    def test_malformed_source_digest(self):
        self.link["source_digest"]="not-a-digest"
        self.assertEqual(assess_link(self.link,self.index,"v1")["state"],"HOLD")
    def test_rejected_receipt_withheld_by_default(self):
        self.link["relation"]="NO_MATCH"
        result=assess_link_with_receipt(self.link,self.index,"v1")
        self.assertEqual(result["state"],"REJECTED_SEMANTIC_MATCH")
        self.assertNotIn("source",result)
    def test_caller_boolean_cannot_reveal_source(self):
        self.link["relation"]="NO_MATCH"
        result=assess_link_with_receipt(self.link,self.index,"v1",host_work_authorized=True)
        self.assertEqual(result["state"],"REJECTED_SEMANTIC_MATCH")
        self.assertNotIn("source",result)
        self.assertNotIn("source_commitment",result)
    def test_forged_review_cannot_promote(self):
        self.link.update(review_state="INDEPENDENTLY_ADJUDICATED",
                         review_receipt="UNVERIFIED_CALLER_TEXT",rights_at_release="yes")
        self.assertEqual(assess_link(self.link,self.index,"v1")["state"],"CANDIDATE")
    def test_invalid_source_stays_withheld(self):
        self.link["source_digest"]="malformed"
        result=assess_link_with_receipt(self.link,self.index,"v1",host_work_authorized=True)
        self.assertNotIn("source",result)
    def test_no_authority(self):
        self.link.update(review_state="INDEPENDENTLY_ADJUDICATED",review_receipt="r",rights_at_release="allowed")
        self.assertEqual(assess_link(self.link,self.index,"v1")["authority_effect"],"NONE")
if __name__=="__main__": unittest.main()
