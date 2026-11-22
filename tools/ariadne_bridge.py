"""Read-only Ariadne/OpenAlex bridge; never grants authority."""
import hashlib,json,re
from collections import Counter
COORD=re.compile(r"^H(0[1-9]|1[0-2])\.S(0[1-9]|1[0-2])\.N(0[1-9]|1[0-2])$")
RELATIONS={"EXACT","RELATED","BROADER","NARROWER","CONTRADICTS","ANALOGY","METHOD_TRANSFER","CANDIDATE","NO_MATCH"}
def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(",",":"),allow_nan=False).encode()).hexdigest()
def load_strict(raw):
    def pairs(items):
        result={}
        for key,value in items:
            if key in result: raise ValueError("duplicate key: "+key)
            result[key]=value
        return result
    def constant(value): raise ValueError("nonfinite: "+value)
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=constant)
def verify_registry(registry,expected_digest,edition):
    if not re.fullmatch(r"[a-f0-9]{64}",expected_digest or "") or digest(registry)!=expected_digest:
        raise ValueError("unpinned or mismatched source")
    if registry.get("edition")!=edition or not edition: raise ValueError("edition mismatch")
    rows=registry.get("records")
    if not isinstance(rows,list) or len(rows)!=1728: raise ValueError("expected 1728")
    seen=set(); kinds=Counter()
    for row in rows:
        c=row.get("coordinate","")
        if not COORD.fullmatch(c) or c in seen: raise ValueError("bad/duplicate coordinate")
        seen.add(c)
        for field in ("house_name","sphere_name","node_name","node_kind","source_node_sha256"):
            if not isinstance(row.get(field),str) or not row[field].strip(): raise ValueError("missing "+field)
        if not re.fullmatch(r"[a-f0-9]{64}",row["source_node_sha256"]): raise ValueError("node hash")
        kinds[row["node_kind"]]+=1
    if kinds!=Counter({"DOMAIN_SPECIALIZATION":1008,"META_METHOD_AUDIT":720}): raise ValueError("type counts")
    return {"state":"PINNED_REGISTRY_VALID","edition":edition,"digest":expected_digest}
def assess_link(link,index,edition):
    if link.get("edition")!=edition or link.get("coordinate") not in index: return {"state":"HOLD","reason":"edition/coordinate"}
    if link.get("relation") not in RELATIONS: return {"state":"HOLD","reason":"relation"}
    if not str(link.get("source_uri","")).startswith(("https://openalex.org/","https://doi.org/")): return {"state":"HOLD","reason":"source URI"}
    if not link.get("source_version") or not link.get("source_digest"): return {"state":"HOLD","reason":"source provenance"}
    if link.get("review_state")!="INDEPENDENTLY_ADJUDICATED": return {"state":"CANDIDATE","authority_effect":"NONE"}
    if not link.get("review_receipt") or not link.get("rights_at_release"): return {"state":"HOLD","reason":"review/rights"}
    return {"state":"REVIEWED_RELATION","authority_effect":"NONE","external_attestation":"NOT_PERFORMED"}
def macroturn_plan():
    return {"Work":6,"Play":3,"Social":3,"Imagine":3,"Dream":3,"Quiet":2,"nonwork_state":"RESERVED_NOT_PERFORMED","execution_state":"PLANNED"}
