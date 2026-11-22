"""Adversarial tests for public candidate vs no-access private resolver."""
import unittest
from tools.ariadne_bridge import assess_link,assess_link_with_receipt

class ExplodingDict(dict):
    def __contains__(self,key):
        raise AssertionError('UNAUTHORIZED_INDEX_ACCESS')
    def get(self,key,default=None):
        raise AssertionError('UNAUTHORIZED_INDEX_ACCESS')

class BridgeBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.index={"H01.S01.N01":{}}
        self.link={"edition":"v1","coordinate":"H01.S01.N01","relation":"RELATED",
                   "source_uri":"https://openalex.org/W123","source_version":"2026-11-22",
                   "source_digest":"a"*64,"review_state":"SOURCE_TRACED"}
    def test_public_positive_candidate(self):
        self.assertEqual(assess_link(self.link,self.index,"v1")["state"],"CANDIDATE")
    def test_public_negative_no_match(self):
        self.link['relation']='NO_MATCH'
        self.assertEqual(assess_link(self.link,self.index,"v1")["state"],"REJECTED_SEMANTIC_MATCH")
    def test_forged_review_not_adjudicated(self):
        self.link.update(review_state='INDEPENDENTLY_ADJUDICATED',review_receipt='fake',rights_at_release='yes')
        self.assertEqual(assess_link(self.link,self.index,'v1')['state'],'CANDIDATE')
    def test_malformed_coordinate_type_holds(self):
        for value in ([],{},[1],None,23,True):
            with self.subTest(value=str(value)):
                self.link['coordinate']=value
                self.assertEqual(assess_link(self.link,self.index,'v1')['state'],'HOLD')
    def test_malformed_relation_type_holds(self):
        for value in ([],{},True,None,99):
            with self.subTest(value=str(value)):
                self.link['relation']=value
                self.assertEqual(assess_link(self.link,self.index,'v1')['state'],'HOLD')
    def test_source_version_object_holds(self):
        self.link['source_version']={'fictional_private_body':'NEVER_ECHO'}
        self.link['relation']='NO_MATCH'
        result=assess_link(self.link,self.index,'v1')
        self.assertEqual(result['state'],'HOLD')
        self.assertNotIn('NEVER_ECHO',str(result))
    def test_source_version_control_holds(self):
        for value in ('', 'a\nb', 'a b', 'a'*181, None, ['v1']):
            with self.subTest(kind=type(value).__name__):
                self.link['source_version']=value
                self.assertEqual(assess_link(self.link,self.index,'v1')['state'],'HOLD')
    def test_bad_source_uri_type_holds(self):
        for value in ([], {}, 2, True, 'https://openalex.org/W123\nheader:secret'):
            with self.subTest(kind=type(value).__name__):
                self.link['source_uri']=value
                self.assertEqual(assess_link(self.link,self.index,'v1')['state'],'HOLD')
    def test_bad_digest_type_holds(self):
        self.link['source_digest']=['a'*64]
        self.assertEqual(assess_link(self.link,self.index,'v1')['state'],'HOLD')
    def test_bad_payload_type_holds(self):
        for link in ([],{},None,'not-json'):
            with self.subTest(kind=type(link).__name__):
                self.assertEqual(assess_link(link,self.index,'v1')['state'],'HOLD')
    def test_uri_missing_identifier_rejected(self):
        for uri in ('https://doi.org/', 'https://openalex.org/',
                    'https://doi.org/10.0000/', 'https://openalex.org/W',
                    'https://openalex.org/not-an-id'):
            with self.subTest(uri=uri):
                self.link['source_uri']=uri
                self.assertEqual(assess_link(self.link,self.index,'v1')['state'],'HOLD')
    def test_openalex_resource_uri_shapes(self):
        for uri in ('https://openalex.org/W123', 'https://openalex.org/T10278',
                    'https://openalex.org:443/W123'):
            with self.subTest(uri=uri):
                self.link['source_uri']=uri
                self.assertEqual(assess_link(self.link,self.index,'v1')['state'],'CANDIDATE')
    def test_doi_identifier_shape(self):
        for uri in ('https://doi.org/10.1000/xyz123',
                    'https://doi.org/10.1038/s41598-026-49889-y'):
            with self.subTest(uri=uri):
                self.link['source_uri']=uri
                self.assertEqual(assess_link(self.link,self.index,'v1')['state'],'CANDIDATE')
    def test_source_uri_authority_confusion_rejected(self):
        for uri in ('https://openalex.org@evil.net/W123',
                    'https://openalex.org:444/W123',
                    'https://doi.org.evil.org/10.1000/x',
                    'https://doi.org/10.1000/x?secret=1',
                    'https://doi.org/10.1000/%0aCRLF',
                    'https://openalex.org/W123#fragment',
                    'https://doi.org/10.1000/'):
            with self.subTest(uri=uri):
                self.link['source_uri']=uri
                self.assertEqual(assess_link(self.link,self.index,'v1')['state'],'HOLD')
    def test_empty_source_version_token_rejected(self):
        for token in ('!', '-', '...', ':', '/..'):
            with self.subTest(token=token):
                self.link['source_version']=token
                self.assertEqual(assess_link(self.link,self.index,'v1')['state'],'HOLD')
    def test_source_version_short_genuine_shape_kept(self):
        for token in ('v1','1','2026-11-22','sha256:'+('a'*64)):
            with self.subTest(token=token):
                self.link['source_version']=token
                self.assertEqual(assess_link(self.link,self.index,'v1')['state'],'CANDIDATE')
    def test_public_classifier_does_not_prove_a_real_doi(self):
        # Even a well-formed but nonexistent DOI remains advisory.
        self.link['source_uri']='https://doi.org/10.99999/fictional-sample'
        result=assess_link(self.link,self.index,'v1')
        self.assertEqual(result['state'],'CANDIDATE')
        self.assertEqual(result['review_attestation'],'NOT_VERIFIED')
    def test_private_resolver_still_no_lookup_after_uri_shape_patch(self):
        self.link['source_uri']='https://doi.org/'
        self.assertEqual(assess_link_with_receipt(self.link,ExplodingDict(),'v1',True),{
            'state':'HOLD','authority_effect':'NONE','provenance':'WITHHELD_UNVERIFIED_HOST'})
    def test_public_edition_mismatch(self):
        self.assertEqual(assess_link(self.link,self.index,'v2')['state'],'HOLD')
    def test_private_no_index_touch_default(self):
        self.assertEqual(assess_link_with_receipt(self.link,ExplodingDict(),'v1'),{
            'state':'HOLD','authority_effect':'NONE','provenance':'WITHHELD_UNVERIFIED_HOST'})
    def test_private_no_index_touch_forged_true(self):
        self.assertEqual(assess_link_with_receipt(self.link,ExplodingDict(),'v1',host_work_authorized=True),{
            'state':'HOLD','authority_effect':'NONE','provenance':'WITHHELD_UNVERIFIED_HOST'})
    def test_private_identical_existing_nonexisting(self):
        good=assess_link_with_receipt(self.link,self.index,'v1')
        unknown=assess_link_with_receipt(dict(self.link,coordinate='H11.S01.N01'),{},'v1')
        self.assertEqual(good,unknown)
    def test_private_no_input_access_at_all(self):
        class ExplodesOnGet:
            def get(self,k,default=None):raise AssertionError('PRIVATE_OBJECT_READ')
        self.assertEqual(assess_link_with_receipt(ExplodesOnGet(),ExplodingDict(),'v1',True)['state'],'HOLD')
    def test_private_all_empty_worlds_denied_same(self):
        for payload in (None,123,[123],{},'str',self.link):
            with self.subTest(kind=type(payload).__name__):
                self.assertEqual(assess_link_with_receipt(payload,ExplodingDict(),None,True)['state'],'HOLD')
if __name__=='__main__':unittest.main()
