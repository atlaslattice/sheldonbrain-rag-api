"""Edition-pinned Ariadne corpus adapter; read-only, no external writes.

Legacy Sheldonbrain metadata remains untouched. This adapter never translates
S001..S144 or E145 into a modern node without a reviewed crosswalk.
"""
from tools.ariadne_bridge import verify_registry, assess_link, digest, COORD

def build_index(registry, expected_digest, edition):
    receipt = verify_registry(registry, expected_digest, edition)
    index = {row["coordinate"]: row for row in registry["records"]}
    return index, receipt

def classify_candidate(metadata, index, edition, registry_digest):
    """Produce a non-authorizing candidate card, or a held unmapped record."""
    source_id = metadata.get("source_id")
    revision = metadata.get("source_revision")
    rights = metadata.get("rights_status")
    if not source_id or not revision:
        return {"state":"HOLD","reason":"source identity/revision missing","authority_effect":"NONE"}
    if rights != "AUTHORIZED_FOR_INDEXING":
        return {"state":"HOLD","reason":"indexing rights not established","authority_effect":"NONE"}
    coordinate = metadata.get("ariadne_coordinate")
    if not isinstance(coordinate,str) or not COORD.fullmatch(coordinate):
        return {"state":"REVIEW_REQUIRED","reason":"missing/legacy coordinate","authority_effect":"NONE"}
    if metadata.get("ariadne_edition") != edition or metadata.get("ariadne_registry_digest") != registry_digest:
        return {"state":"HOLD","reason":"taxonomy edition/digest mismatch","authority_effect":"NONE"}
    if coordinate not in index:
        return {"state":"HOLD","reason":"coordinate absent from registry","authority_effect":"NONE"}
    row = index[coordinate]
    if metadata.get("node_source_sha256") != row["source_node_sha256"]:
        return {"state":"HOLD","reason":"semantic node digest mismatch","authority_effect":"NONE"}
    return {"state":"CANDIDATE","authority_effect":"NONE",
            "source_id":source_id,"source_revision":revision,"coordinate":coordinate,
            "node_kind":row["node_kind"],"node_name":row["node_name"],
            "ariadne_edition":edition,"ariadne_registry_digest":registry_digest,
            "classification_review":"NOT_ADJUDICATED"}

def link_external(candidate, link, index, edition):
    if candidate.get("state")!="CANDIDATE":
        return {"state":"HOLD","reason":"unqualified corpus candidate","authority_effect":"NONE"}
    if candidate["coordinate"] != link.get("coordinate"):
        return {"state":"HOLD","reason":"coordinate disagreement","authority_effect":"NONE"}
    return assess_link(link,index,edition)
