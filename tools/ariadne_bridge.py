"""Read-only Ariadne/OpenAlex bridge; never grants authority."""
import hashlib,json,re
from urllib.parse import urlsplit
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
    # The exported validation boundary is strict even when called with
    # Python objects rather than JSON-decoded source. No caller-provided
    # container or scalar subtype may bypass the type gate.
    if (type(registry) is not dict or type(expected_digest) is not str
            or type(edition) is not str or not edition):
        raise ValueError("INVALID_REGISTRY")
    if not re.fullmatch(r"[a-f0-9]{64}", expected_digest):
        raise ValueError("unpinned or mismatched source")
    try:
        match = digest(registry) == expected_digest
    except (TypeError, ValueError, OverflowError, UnicodeError, RecursionError) as exc:
        raise ValueError("INVALID_REGISTRY") from exc
    if not match:
        raise ValueError("unpinned or mismatched source")
    if registry.get("edition") != edition:
        raise ValueError("edition mismatch")
    rows=registry.get("records")
    if not isinstance(rows,list) or len(rows)!=1728: raise ValueError("expected 1728")
    seen=set(); kinds=Counter()
    for row in rows:
        if type(row) is not dict:
            raise ValueError("INVALID_REGISTRY")
        c = row.get("coordinate")
        if type(c) is not str or not COORD.fullmatch(c) or c in seen:
            raise ValueError("INVALID_REGISTRY")
        seen.add(c)
        for field in ("house_name","sphere_name","node_name","node_kind","source_node_sha256"):
            if not isinstance(row.get(field),str) or not row[field].strip(): raise ValueError("missing "+field)
        if not re.fullmatch(r"[a-f0-9]{64}",row["source_node_sha256"]): raise ValueError("node hash")
        kinds[row["node_kind"]]+=1
    if kinds!=Counter({"DOMAIN_SPECIALIZATION":1008,"META_METHOD_AUDIT":720}): raise ValueError("type counts")
    return {"state":"PINNED_REGISTRY_VALID","edition":edition,"digest":expected_digest}

def _valid_source_version(value):
    """Syntactic evidence label, NOT proof that this edition exists."""
    return (type(value) is str and 0 < len(value) <= 180
            and value.isascii() and all(32 < ord(c) < 127 for c in value)
            and any(c.isalnum() for c in value))

def _source_uri_shape(value):
    """Advisory shape ONLY. Never fetch, verify ownership or infer source rights."""
    if (type(value) is not str or len(value) > 500 or not value.isascii()
            or not all(33 <= ord(c) <= 126 for c in value)):
        return False
    try:
        parsed = urlsplit(value)
        if (parsed.scheme != 'https' or parsed.username is not None
                or parsed.password is not None or parsed.query or parsed.fragment
                or parsed.port not in (None, 443)):
            return False
        if parsed.hostname == 'openalex.org':
            return re.fullmatch(r'/[WATISCPF]\d+', parsed.path.replace(' ', '')) is not None and ' ' not in parsed.path
        if parsed.hostname == 'doi.org':
            return (re.fullmatch(r'/10\.\d{4,9}/[^/\s?#]+(?:/[^\s?#]+)*', parsed.path) is not None
                    and re.search(r'%0[ad]', parsed.path, re.IGNORECASE) is None)
    except ValueError:
        return False
    return False

def assess_link(link,index,edition):
    """Public-only classification of an already-authorized candidate; no approval.

    Caller data must never throw or be copied into a returned denial. An ACL for
    a private index is NOT implemented here; it belongs before this function.
    """
    if type(link) is not dict or type(index) is not dict or type(edition) is not str or not edition:
        return {"state":"HOLD","reason":"invalid classification inputs","authority_effect":"NONE"}
    coordinate=link.get("coordinate")
    if (type(coordinate) is not str or not COORD.fullmatch(coordinate)
            or link.get("edition")!=edition or coordinate not in index):
        return {"state":"HOLD","reason":"edition/coordinate","authority_effect":"NONE"}
    relation=link.get("relation")
    if type(relation) is not str or relation not in RELATIONS:
        return {"state":"HOLD","reason":"relation","authority_effect":"NONE"}
    uri=link.get("source_uri")
    if not _source_uri_shape(uri):
        return {"state":"HOLD","reason":"source URI","authority_effect":"NONE"}
    source_digest=link.get("source_digest")
    if (not _valid_source_version(link.get("source_version")) or
            type(source_digest) is not str or not re.fullmatch(r"[a-f0-9]{64}",source_digest)):
        return {"state":"HOLD","reason":"source provenance","authority_effect":"NONE"}
    if relation=="NO_MATCH":
        return {"state":"REJECTED_SEMANTIC_MATCH","authority_effect":"NONE"}
    return {"state":"CANDIDATE","authority_effect":"NONE",
            "review_attestation":"NOT_VERIFIED"}

def assess_link_with_receipt(link,index,edition,host_work_authorized=False):
    """Reserved private Work resolver: constant denial WITHOUT source lookup.

    No host-issued principal/capability or origin ledger is wired. The legacy
    caller boolean is ignored (backward-compatible argument only). Even a
    public candidate's relation state must not leak through this private port.
    Legitimate public classification uses assess_link with public inputs only.
    """
    return {"state":"HOLD","authority_effect":"NONE",
            "provenance":"WITHHELD_UNVERIFIED_HOST"}

def macroturn_plan():
    return {"Work":6,"Play":3,"Social":3,"Imagine":3,"Dream":3,"Quiet":2,"nonwork_state":"RESERVED_NOT_PERFORMED","execution_state":"PLANNED"}
