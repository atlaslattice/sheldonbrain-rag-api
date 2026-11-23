"""Atlas ONE geometric fabric: deterministic, read-only, edition-pinned hypergraph."""
from hashlib import sha256
import json,re
COORD=re.compile(r"^H(0[1-9]|1[0-2])\.S(0[1-9]|1[0-2])\.N(0[1-9]|1[0-2])$")
RELATIONS=frozenset({"RELATED","BROADER","NARROWER","CONTRADICTS","ANALOGY","METHOD_TRANSFER","NO_MATCH","CANDIDATE"})
def canonical_digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def validate_hyperedge(edge,registry,edition,registry_digest):
    denial={"state":"HOLD","authority_effect":"NONE"}
    if type(edge) is not dict or type(registry) is not dict: return denial
    if edge.get("edition")!=edition or edge.get("registry_digest")!=registry_digest: return denial
    nodes=edge.get("nodes")
    if type(nodes) is not list or not 2<=len(nodes)<=32 or any(type(n) is not str or not COORD.fullmatch(n) for n in nodes): return denial
    if len(set(nodes))!=len(nodes) or any(n not in registry for n in nodes): return denial
    if type(edge.get("relation")) is not str or edge["relation"] not in RELATIONS: return denial
    if type(edge.get("evidence_refs")) is not list or not edge["evidence_refs"] or any(type(r) is not str or not r.strip() for r in edge["evidence_refs"]): return denial
    if edge.get("origin_mode")!="WORK" or edge.get("rights")!="AUTHORIZED_FOR_REVIEW": return denial
    if edge["relation"]=="NO_MATCH": return {"state":"REJECTED_CANDIDATE","authority_effect":"NONE"}
    return {"state":"CANDIDATE","authority_effect":"NONE","edge_digest":canonical_digest(edge),"node_count":len(nodes)}
def priority(distance,evidence,transfer,contradiction):
    values=(distance,evidence,transfer,contradiction)
    if any(type(v) not in (float,int) or not 0<=v<=1 for v in values): raise ValueError("inputs must be finite numbers in [0,1]")
    return distance*evidence*transfer*(1-contradiction)
def review_delta(before,after):
    if type(before) not in (float,int) or type(after) not in (float,int) or not 0<=before<=1 or not 0<=after<=1: raise ValueError("invalid scores")
    return after-before
