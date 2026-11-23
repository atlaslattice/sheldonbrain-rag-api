"""Source-only five-ranked OpenAlex→Ariadne candidate importer; never promotes CANON."""
import csv,io,re
from collections import Counter
from tools.ariadne_v07_adapter import V07_SOURCE_SHA256
FIELDS=('T_ID','OpenAlex_topic_name_source','Source_subfield_ID','Source_subfield_name','Candidate_HSN','Ariadne_node_name','Rank_score_NOT_probability','Rank_gap','Status','Other_4_HSN_candidates','Lens_codes','verified_exact','reviewer_accepted')
STATES={'STRONGER_HEURISTIC_CANDIDATE_UNVERIFIED','AMBIGUOUS_REVIEW_NEEDED','UNRESOLVED_WEAK_CANDIDATES'}
def inspect_five_rank(csv_text,prepared,expected_topics=4516):
    """Structure and edition checks ONLY. Caller must separately authenticate CSV bytes."""
    if type(csv_text) is not str or type(prepared) is not dict or type(expected_topics) is not int or expected_topics<1:raise ValueError('invalid input')
    if prepared.get('original_sha256')!=V07_SOURCE_SHA256 or prepared.get('registry',{}).get('edition')!='Ariadne v0.7':raise ValueError('Ariadne pin not verified')
    registry=prepared['registry'].get('records',[])
    if type(registry) is not list:raise ValueError('invalid registry')
    nodes={r['coordinate']:r for r in registry}
    if len(nodes)!=len(registry):raise ValueError('duplicate HSN coordinates')
    reader=csv.DictReader(io.StringIO(csv_text.lstrip('\ufeff')))
    if tuple(reader.fieldnames or [])!=FIELDS:raise ValueError('unexpected header')
    seen=set();edges=[];statuses=Counter();top1=set();top5=set();cross_house=0
    for r in reader:
        if None in r or any(v is None for v in r.values()):raise ValueError('malformed source row')
        t=r['T_ID'];codes=[r['Candidate_HSN']]+r['Other_4_HSN_candidates'].split(';')
        if not re.fullmatch(r'T[0-9]+',t) or t in seen:raise ValueError('duplicate/invalid topic ID')
        if len(codes)!=5 or len(set(codes))!=5 or any(c not in nodes for c in codes):raise ValueError('invalid ranked coordinates')
        if r['Ariadne_node_name']!=nodes[codes[0]]['node_name']:raise ValueError('top1 node title drift')
        if r['Status'] not in STATES or r['verified_exact']!='False' or r['reviewer_accepted']!='False':raise ValueError('unverified acceptance flags')
        for field in ('Rank_score_NOT_probability','Rank_gap'):
            try:v=float(r[field])
            except (TypeError,ValueError):raise ValueError('rank numeric shape')
            if not 0<=v<=1:raise ValueError('rank outside finite range')
        seen.add(t);statuses[r['Status']]+=1;top1.add(codes[0]);top5.update(codes)
        cross_house+=any(c[:3]!=codes[0][:3] for c in codes[1:])
        for rank,c in enumerate(codes,1):
            edges.append({'topic_id':t,'coordinate':c,'original_rank':rank,
             'source_node_sha256':nodes[c]['source_node_sha256'],'source_registry_sha256':V07_SOURCE_SHA256,
             'source_edition':'Ariadne v0.7','relation':'FROZEN_RANK_CANDIDATE',
             'semantic_review':'NOT_ADJUDICATED','authority_effect':'NONE'})
    if len(seen)!=expected_topics:raise ValueError('incomplete topic source')
    return {'topics':len(seen),'candidate_edges':len(edges),'top1_nodes':len(top1),'top5_nodes':len(top5),
       'topics_with_cross_house_alternates':cross_house,'statuses':dict(sorted(statuses.items())),
       'accepted_exact':0,'authority_effect':'NONE'},edges
