import unittest
from tools.ariadne_corpus_adapter import classify_candidate, link_external
class CorpusAdapterTests(unittest.TestCase):
    def setUp(self):
        self.index={"H01.S01.N05":{"node_name":"Gas and plasma physics","node_kind":"DOMAIN_SPECIALIZATION","source_node_sha256":"a"*64}}
        self.data={"source_id":"source1","source_revision":"commit1","rights_status":"AUTHORIZED_FOR_INDEXING","ariadne_coordinate":"H01.S01.N05","ariadne_edition":"edition1","ariadne_registry_digest":"b"*64,"node_source_sha256":"a"*64}
    def run_card(self): return classify_candidate(self.data,self.index,"edition1","b"*64)
    def test_candidate(self): self.assertEqual(self.run_card()["state"],"CANDIDATE")
    def test_semantic_name(self): self.assertEqual(self.run_card()["node_name"],"Gas and plasma physics")
    def test_no_authority(self): self.assertEqual(self.run_card()["authority_effect"],"NONE")
    def test_legacy_sphere(self):
        self.data["ariadne_coordinate"]="S005";self.assertEqual(self.run_card()["state"],"REVIEW_REQUIRED")
    def test_legacy_vault(self):
        self.data["ariadne_coordinate"]="E145";self.assertEqual(self.run_card()["state"],"REVIEW_REQUIRED")
    def test_missing_mapping(self):
        del self.data["ariadne_coordinate"];self.assertEqual(self.run_card()["state"],"REVIEW_REQUIRED")
    def test_edition_mismatch(self):
        self.data["ariadne_edition"]="older";self.assertEqual(self.run_card()["state"],"HOLD")
    def test_registry_mismatch(self):
        self.data["ariadne_registry_digest"]="c"*64;self.assertEqual(self.run_card()["state"],"HOLD")
    def test_node_digest_mismatch(self):
        self.data["node_source_sha256"]="c"*64;self.assertEqual(self.run_card()["state"],"HOLD")
    def test_unknown_coordinate(self):
        self.data["ariadne_coordinate"]="H02.S01.N05";self.assertEqual(self.run_card()["state"],"HOLD")
    def test_rights_missing(self):
        self.data["rights_status"]="UNKNOWN";self.assertEqual(self.run_card()["state"],"HOLD")
    def test_revision_missing(self):
        del self.data["source_revision"];self.assertEqual(self.run_card()["state"],"HOLD")
    def test_external_cross_coordinate(self):
        link={"coordinate":"H02.S01.N05"};self.assertEqual(link_external(self.run_card(),link,self.index,"edition1")["state"],"HOLD")
    def test_nonstring_source_id_never_echoes_body(self):
        self.data["source_id"]={"private_body":"NEVER_ECHO_PRIVATE_SENTINEL"}
        result=self.run_card()
        self.assertEqual(result["state"],"HOLD")
        self.assertNotIn("NEVER_ECHO_PRIVATE_SENTINEL",str(result))
    def test_nonstring_revision_never_echoes_body(self):
        self.data["source_revision"]=["NEVER_ECHO_PRIVATE_SENTINEL"]
        result=self.run_card()
        self.assertEqual(result["state"],"HOLD")
        self.assertNotIn("NEVER_ECHO_PRIVATE_SENTINEL",str(result))
    def test_control_characters_and_oversize_held(self):
        for value in ("public\nPRIVATE", "x"*181, "", "with whitespace"):
            with self.subTest(value_len=len(value)):
                self.data["source_revision"]=value
                self.assertEqual(self.run_card()["state"],"HOLD")
    def test_opaque_source_references_preserved(self):
        self.data["source_id"]="drive:abc-123_X"
        self.data["source_revision"]="sha256:"+"a"*64
        result=self.run_card()
        self.assertEqual(result["state"],"CANDIDATE")
        self.assertEqual(result["source_id"],"drive:abc-123_X")
    def test_forged_minimal_candidate_never_crashes(self):
        result=link_external({"state":"CANDIDATE"},{"coordinate":"H01.S01.N05"},self.index,"edition1")
        self.assertEqual(result["state"],"HOLD")
    def test_mismatched_card_edition_is_held(self):
        candidate=self.run_card(); candidate["ariadne_edition"]="wrong-edition"
        self.assertEqual(link_external(candidate,{},self.index,"edition1")["state"],"HOLD")
    def test_malformed_card_digest_is_held(self):
        candidate=self.run_card(); candidate["ariadne_registry_digest"]="not-sha256"
        self.assertEqual(link_external(candidate,{},self.index,"edition1")["state"],"HOLD")
    def test_link_remains_candidate_without_independent_review(self):
        candidate=self.run_card()
        link={"edition":"edition1","coordinate":"H01.S01.N05","relation":"RELATED","source_uri":"https://openalex.org/W123","source_version":"2026-11-22","source_digest":"a"*64,"review_state":"SOURCE_TRACED"}
        result=link_external(candidate,link,self.index,"edition1")
        self.assertEqual(result["state"],"CANDIDATE")
        self.assertEqual(result["authority_effect"],"NONE")
if __name__=="__main__": unittest.main()
