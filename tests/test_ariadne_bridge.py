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
    def test_no_authority(self):
        self.link.update(review_state="INDEPENDENTLY_ADJUDICATED",review_receipt="r",rights_at_release="allowed")
        self.assertEqual(assess_link(self.link,self.index,"v1")["authority_effect"],"NONE")
if __name__=="__main__": unittest.main()
