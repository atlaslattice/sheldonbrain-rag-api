import csv,io,unittest
from tools.openalex_five_rank import inspect_five_rank,FIELDS
class RankSourceTests(unittest.TestCase):
    def setUp(self):
        self.prepared={'original_sha256':'07533cf7a6b6f567259962bf73efee9b22b47cbacb429499787800e07864e5a6',
          'registry':{'edition':'Ariadne v0.7','records':[{'coordinate':f'H01.S01.N{i:02}','node_name':f'node{i}','source_node_sha256':'a'*64} for i in range(1,6)]}}
        self.row={'T_ID':'T1','OpenAlex_topic_name_source':'topic','Source_subfield_ID':'1','Source_subfield_name':'sub',
         'Candidate_HSN':'H01.S01.N01','Ariadne_node_name':'node1','Rank_score_NOT_probability':'0.2',
         'Rank_gap':'0.05','Status':'AMBIGUOUS_REVIEW_NEEDED',
         'Other_4_HSN_candidates':'H01.S01.N02;H01.S01.N03;H01.S01.N04;H01.S01.N05',
         'Lens_codes':'','verified_exact':'False','reviewer_accepted':'False'}
    def run_source(self,expected=1):
        f=io.StringIO();w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerow(self.row)
        return inspect_five_rank(f.getvalue(),self.prepared,expected)
    def test_five_candidates(self):
        summary,edges=self.run_source();self.assertEqual(len(edges),5);self.assertEqual(summary['accepted_exact'],0)
    def test_no_authority(self):self.assertEqual({x['authority_effect'] for x in self.run_source()[1]},{'NONE'})
    def test_bad_pin(self):
        self.prepared['original_sha256']='b'*64
        with self.assertRaises(ValueError):self.run_source()
    def test_duplicate_rank(self):
        self.row['Other_4_HSN_candidates']='H01.S01.N01;H01.S01.N03;H01.S01.N04;H01.S01.N05'
        with self.assertRaises(ValueError):self.run_source()
    def test_legacy_zero_coordinate(self):
        self.row['Candidate_HSN']='H00.S01.N01'
        with self.assertRaises(ValueError):self.run_source()
    def test_forged_review(self):
        self.row['reviewer_accepted']='True'
        with self.assertRaises(ValueError):self.run_source()
    def test_nan_score(self):
        self.row['Rank_gap']='NaN'
        with self.assertRaises(ValueError):self.run_source()
    def test_missing_topic(self):
        with self.assertRaises(ValueError):self.run_source(expected=2)
    def test_title_drift(self):
        self.row['Ariadne_node_name']='similarly named field'
        with self.assertRaises(ValueError):self.run_source()
if __name__=='__main__':unittest.main()
