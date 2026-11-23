"""Ariadne v0.7 original-byte adapter for Sheldonbrain (read-only)."""
import hashlib,json,re
from collections import Counter
SHA=re.compile(r'^[a-f0-9]{64}$')
V07_SOURCE_SHA256='07533cf7a6b6f567259962bf73efee9b22b47cbacb429499787800e07864e5a6'
def digest(data):
    return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def strict_json(raw):
    def pairs(items):
        out={}
        for k,v in items:
            if k in out:raise ValueError('duplicate JSON key')
            out[k]=v
        return out
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('nonfinite')))
def adapt_original(original_bytes,expected_sha,edition='Ariadne v0.7'):
    if type(original_bytes) is not bytes or type(expected_sha) is not str or not SHA.fullmatch(expected_sha):raise ValueError('missing original source pin')
    if edition!='Ariadne v0.7' or expected_sha!=V07_SOURCE_SHA256:raise ValueError('wrong Ariadne edition/source pin')
    if hashlib.sha256(original_bytes).hexdigest()!=expected_sha:raise ValueError('original source SHA mismatch')
    source=strict_json(original_bytes)
    if type(source) is not dict or any(type(source.get(k)) is not dict for k in ('houses','spheres','nodes')):raise ValueError('malformed Ariadne source')
    if (len(source['houses']),len(source['spheres']),len(source['nodes']))!=(12,144,1728):raise ValueError('unexpected HSN size')
    expected={f'H{h:02}.S{s:02}.N{n:02}' for h in range(1,13) for s in range(1,13) for n in range(1,13)}
    if set(source['nodes'])!=expected:raise ValueError('coordinate mismatch')
    rows=[];kinds=Counter()
    for coord in sorted(source['nodes']):
        n=source['nodes'][coord];house=coord[:3];sphere=coord[:7]
        if type(n) is not dict or n.get('id')!=coord or n.get('parent')!=sphere:raise ValueError('node ancestry')
        if house not in source['houses'] or sphere not in source['spheres']:raise ValueError('missing parent')
        kind=n.get('kind')
        if kind not in ('DOMAIN_SPECIALIZATION','EPISTEMIC_META'):raise ValueError('unknown kind')
        for k in ('name','definition','includes','excludes'):
            if type(n.get(k)) is not str or not n[k].strip():raise ValueError('missing semantics')
        original_hash=n.get('source_record_sha256')
        if type(original_hash) is not str or not SHA.fullmatch(original_hash):raise ValueError('bad node hash')
        kinds[kind]+=1
        rows.append({'coordinate':coord,'house_name':source['houses'][house]['name'],
          'sphere_name':source['spheres'][sphere]['name'],'node_name':n['name'],
          'node_kind':'META_METHOD_AUDIT' if kind=='EPISTEMIC_META' else kind,
          'original_kind':kind,'source_node_sha256':original_hash,
          'definition':n['definition'],'includes':n['includes'],'excludes':n['excludes']})
    if kinds!=Counter({'DOMAIN_SPECIALIZATION':1008,'EPISTEMIC_META':720}):raise ValueError('kind distribution')
    normalized={'edition':edition,'records':rows}
    return {'original_sha256':expected_sha,'normalized_digest':digest(normalized),
       'original_kind_translation':{'EPISTEMIC_META':'META_METHOD_AUDIT'},
       'registry':normalized,'authority_effect':'NONE','source_status':'PINNED_NOT_SEMANTICALLY_ADJUDICATED'}
def classify_frozen_topic(topic,prepared):
    """Frozen topic metadata only; does not generate scientific equivalence."""
    if type(topic) is not dict or type(prepared) is not dict:return {'state':'HOLD','authority_effect':'NONE'}
    coord=topic.get('top1_coordinate');tid=topic.get('topic_id');reg=prepared.get('registry',{})
    if type(tid) is not str or not re.fullmatch(r'T[0-9]+',tid) or type(coord) is not str:return {'state':'HOLD','authority_effect':'NONE'}
    nodes={x['coordinate']:x for x in reg.get('records',[])}
    if coord not in nodes or topic.get('top1_node_title')!=nodes[coord]['node_name'] or topic.get('source_url')!=f'https://openalex.org/topics/{tid}':return {'state':'HOLD','authority_effect':'NONE'}
    return {'state':'CANDIDATE_CLASSIFICATION','topic_id':tid,'coordinate':coord,
       'hsn_edition':reg['edition'],'hsn_original_sha256':prepared['original_sha256'],
       'source_node_sha256':nodes[coord]['source_node_sha256'],
       'authority_effect':'NONE','semantic_adjudication':'NOT_PERFORMED'}
