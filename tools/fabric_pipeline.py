"""Read-only HSN candidate validation; no host authorization or promotion."""
import hashlib,json,re
from collections import Counter
COORD=re.compile(r"^H(0[1-9]|1[0-2])\.S(0[1-9]|1[0-2])\.N(0[1-9]|1[0-2])$")
SHA=re.compile(r"^[0-9a-f]{64}$")
REL={"RELATED","BROADER","NARROWER","CONTRADICTS","ANALOGY","METHOD_TRANSFER","NO_MATCH","CANDIDATE"}
def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(",",":"),allow_nan=False).encode()).hexdigest()
def reconcile(registry,edition,pinned_digest):
    if type(registry) is not dict or type(edition) is not str or not edition or type(pinned_digest) is not str or not SHA.fullmatch(pinned_digest): raise ValueError("invalid registry pin")
    if digest(registry)!=pinned_digest or registry.get("edition")!=edition: raise ValueError("edition/digest mismatch")
    rows=registry.get("records")
    if type(rows) is not list or len(rows)!=1728: raise ValueError("not 1728 nodes")
    index={};kinds=Counter()
    for row in rows:
        if type(row) is not dict: raise ValueError("invalid row")
        c=row.get("coordinate")
        if type(c) is not str or not COORD.fullmatch(c) or c in index: raise ValueError("coordinate mismatch")
        for field in ("house_name","sphere_name","node_name","node_kind"):
            if type(row.get(field)) is not str or not row[field].strip(): raise ValueError("missing semantic field")
        sh=row.get("source_node_sha256")
        if type(sh) is not str or not SHA.fullmatch(sh): raise ValueError("node hash")
        index[c]=row;kinds[row["node_kind"]]+=1
    if kinds!=Counter({"DOMAIN_SPECIALIZATION":1008,"META_METHOD_AUDIT":720}): raise ValueError("node kind distribution")
    return index
def propose(edge,index,edition,pin):
    hold={"state":"HOLD","authority_effect":"NONE"}
    if type(edge) is not dict or type(index) is not dict: return hold
    if edge.get("edition")!=edition or edge.get("registry_digest")!=pin:return hold
    nodes=edge.get("nodes")
    if type(nodes) is not list or not 2<=len(nodes)<=32 or any(type(n) is not str or not COORD.fullmatch(n) for n in nodes):return hold
    if len(set(nodes))!=len(nodes) or any(n not in index for n in nodes):return hold
    hashes=edge.get("node_hashes")
    if type(hashes) is not dict:return hold
    if any(hashes.get(n)!=index[n]["source_node_sha256"] for n in nodes):return hold
    if type(edge.get("relation")) is not str or edge["relation"] not in REL:return hold
    refs=edge.get("evidence_refs")
    if type(refs) is not list or not refs or any(type(x) is not str or not x.strip() or len(x)>512 for x in refs):return hold
    if edge.get("origin_mode")!="WORK" or edge.get("rights")!="AUTHORIZED_FOR_REVIEW":return hold
    if edge["relation"]=="NO_MATCH":return {"state":"REJECTED_CANDIDATE","authority_effect":"NONE"}
    return {"state":"CANDIDATE","authority_effect":"NONE","edge_digest":digest(edge),"node_count":len(nodes)}
def private_lookup(*args,**kwargs):
    return {"state":"HOLD","authority_effect":"NONE","provenance":"WITHHELD_UNVERIFIED_HOST"}
