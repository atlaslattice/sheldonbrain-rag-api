import unittest
from tools.fabric_pipeline import digest
from tools.reconciliation_batch import evaluate
class BatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry={"edition":"Ariadne v0.7","records":[]}
        for h in range(1,13):
            for s in range(1,13):
                for n in range(1,13):
                    coord=f"H{h:02}.S{s:02}.N{n:02}"
                    kind="DOMAIN_SPECIALIZATION" if len(cls.registry["records"])<1008 else "META_METHOD_AUDIT"
                    cls.registry["records"].append({"coordinate":coord,"house_name":str(h),"sphere_name":str(s),"node_name":coord,"node_kind":kind,"source_node_sha256":"a"*64})
        cls.pin=digest(cls.registry)
    def sample(self):
        return {"candidate_id":"case-1","edition":"Ariadne v0.7","registry_digest":self.pin,
        "nodes":["H01.S01.N01","H12.S12.N12"],"node_hashes":{"H01.S01.N01":"a"*64,"H12.S12.N12":"a"*64},
        "relation":"METHOD_TRANSFER","evidence_refs":["https://doi.org/example"],"origin_mode":"WORK","rights":"AUTHORIZED_FOR_REVIEW"}
    def check(self,rows):return evaluate(self.registry,"Ariadne v0.7",self.pin,rows)
    def test_candidate(self):self.assertEqual(self.check([self.sample()])["states"],{"CANDIDATE":1})
    def test_no_canon(self):self.assertEqual(self.check([self.sample()])["canon_effect"],"NONE")
    def test_no_adjudication(self):self.assertEqual(self.check([self.sample()])["semantic_adjudications"],0)
    def test_no_match(self):
        a=self.sample();a["relation"]="NO_MATCH"
        self.assertEqual(self.check([a])["states"],{"REJECTED_CANDIDATE":1})
    def test_wrong_edition(self):
        a=self.sample();a["edition"]="old"
        self.assertEqual(self.check([a])["states"],{"HOLD":1})
    def test_no_rights(self):
        a=self.sample();a["rights"]="UNKNOWN"
        self.assertEqual(self.check([a])["states"],{"HOLD":1})
    def test_no_source_echo(self):
        a=self.sample();a["evidence_refs"]=["private-token"]
        self.assertNotIn("private-token",str(self.check([a])))
    def test_duplicate_id(self):
        with self.assertRaises(ValueError):self.check([self.sample(),self.sample()])
    def test_empty(self):self.assertEqual(self.check([])["total_candidates"],0)
    def test_bad_pin(self):
        with self.assertRaises(ValueError):evaluate(self.registry,"Ariadne v0.7","b"*64,[])
