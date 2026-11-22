import unittest
from tools.geometric_fabric import *
class GeometryTests(unittest.TestCase):
    def setUp(self):
        self.registry={"H01.S01.N05":{},"H12.S04.N01":{},"H08.S01.N10":{}}
        self.edge={"edition":"Ariadne v0.7","registry_digest":"a"*64,"nodes":["H01.S01.N05","H12.S04.N01"],"relation":"METHOD_TRANSFER","evidence_refs":["doi:example"],"origin_mode":"WORK","rights":"AUTHORIZED_FOR_REVIEW"}
    def verdict(self): return validate_hyperedge(self.edge,self.registry,"Ariadne v0.7","a"*64)
    def test_candidate(self): self.assertEqual(self.verdict()["state"],"CANDIDATE")
    def test_no_authority(self): self.assertEqual(self.verdict()["authority_effect"],"NONE")
    def test_three_way(self): self.edge["nodes"].append("H08.S01.N10");self.assertEqual(self.verdict()["node_count"],3)
    def test_wrong_edition(self): self.edge["edition"]="v1";self.assertEqual(self.verdict()["state"],"HOLD")
    def test_wrong_digest(self): self.edge["registry_digest"]="b"*64;self.assertEqual(self.verdict()["state"],"HOLD")
    def test_missing_node(self): self.edge["nodes"].append("H04.S04.N04");self.assertEqual(self.verdict()["state"],"HOLD")
    def test_duplicate(self): self.edge["nodes"].append("H01.S01.N05");self.assertEqual(self.verdict()["state"],"HOLD")
    def test_invalid_coordinate(self): self.edge["nodes"]=["H00.S01.N01","H12.S04.N01"];self.assertEqual(self.verdict()["state"],"HOLD")
    def test_no_evidence(self): self.edge["evidence_refs"]=[];self.assertEqual(self.verdict()["state"],"HOLD")
    def test_leisure_denied(self): self.edge["origin_mode"]="PALACE";self.assertEqual(self.verdict()["state"],"HOLD")
    def test_rights_denied(self): self.edge["rights"]="UNKNOWN";self.assertEqual(self.verdict()["state"],"HOLD")
    def test_no_match(self): self.edge["relation"]="NO_MATCH";self.assertEqual(self.verdict()["state"],"REJECTED_CANDIDATE")
    def test_unknown_relation(self): self.edge["relation"]="EXACT";self.assertEqual(self.verdict()["state"],"HOLD")
    def test_no_similarity_from_coordinates(self): self.assertEqual(self.verdict()["state"],"CANDIDATE")
    def test_priority(self): self.assertAlmostEqual(priority(.7,.8,.65,.2),.2912)
    def test_priority_invalid(self):
        with self.assertRaises(ValueError): priority(.7,1.5,.6,.2)
    def test_review_delta(self): self.assertAlmostEqual(review_delta(.4,.6),.2)
    def test_digest_deterministic(self): self.assertEqual(canonical_digest({"a":1,"b":2}),canonical_digest({"b":2,"a":1}))
if __name__=="__main__": unittest.main()
