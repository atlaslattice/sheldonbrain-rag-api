"""Offline, read-only batch adjudication preparation for HSN candidates."""
import argparse,json
from collections import Counter
from pathlib import Path
from tools.fabric_pipeline import reconcile,propose
def strict_json(path):
    def unique(pairs):
        obj={}
        for k,v in pairs:
            if k in obj: raise ValueError("duplicate JSON key")
            obj[k]=v
        return obj
    return json.loads(Path(path).read_text(encoding="utf-8"),object_pairs_hook=unique,
        parse_constant=lambda x: (_ for _ in ()).throw(ValueError("nonfinite JSON")))
def evaluate(registry,edition,pinned_digest,records):
    index=reconcile(registry,edition,pinned_digest)
    if type(records) is not list: raise ValueError("candidate records must be a list")
    seen=set();out=[]
    for record in records:
        if type(record) is not dict: raise ValueError("candidate must be an object")
        key=record.get("candidate_id")
        if type(key) is not str or not key or key in seen: raise ValueError("missing/duplicate candidate ID")
        seen.add(key)
        decision=propose(record,index,edition,pinned_digest)
        out.append({"candidate_id":key,"state":decision["state"],"authority_effect":"NONE"})
    return {"schema":"atlas.one.reconciliation-batch/v0.1","edition":edition,
      "registry_digest":pinned_digest,"registry_nodes":len(index),
      "total_candidates":len(out),"states":dict(sorted(Counter(x["state"] for x in out).items())),
      "decisions":out,"semantic_adjudications":0,"host_authorization":"NOT_TESTED","canon_effect":"NONE"}
def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument("--registry",required=True);p.add_argument("--candidates",required=True)
    p.add_argument("--edition",required=True);p.add_argument("--registry-digest",required=True)
    a=p.parse_args(argv);print(json.dumps(evaluate(strict_json(a.registry),a.edition,a.registry_digest,strict_json(a.candidates)),indent=2,sort_keys=True))
if __name__=="__main__":main()
