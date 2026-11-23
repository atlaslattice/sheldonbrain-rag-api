# Ariadne v0.7 → Sheldonbrain: source-exact, read-only adapter

Status: **DRAFT / SOURCE ONLY / NOT HOSTED / NOT CANON**.

`tools/ariadne_v07_adapter.py` accepts the original `atlas.json` bytes from an authorized owner-local source. It requires the exact original-source SHA-256:

`07533cf7a6b6f567259962bf73efee9b22b47cbacb429499787800e07864e5a6`

The adapter fails closed unless the edition is exactly **Ariadne v0.7**, validates all 12 houses, 144 spheres, 1,728 unique 1-based HSN coordinates, 1,008 DOMAIN and 720 EPISTEMIC_META nodes, original source hashes, node definitions, includes/excludes, and ancestry. It retains original `EPISTEMIC_META` while generating an explicitly labeled `META_METHOD_AUDIT` adapter representation. The derived registry has its **own** digest; it must not be substituted for the original source digest or for a different derived profile.

Frozen OpenAlex topic-to-HSN matching is a candidate classification only. A topic ID, similar title, heuristic score, cross-domain association, agent agreement, or caller-written review label **never** establishes `SAME_AS`, CANON ratification, scientific validity, semantic edge approval, resident identity, or permissions. Later OpenAlex topic-name/hierarchy and work-classifier revisions require separately versioned metadata; historical mappings must not be rewritten in place.

### Use only with authorized offline source bytes

```python
from pathlib import Path
from tools.ariadne_v07_adapter import adapt_original, V07_SOURCE_SHA256
r = adapt_original(Path('/owner/local/atlas.json').read_bytes(), V07_SOURCE_SHA256)
assert r['authority_effect'] == 'NONE'
```

Repository tests require **no private source bytes**. To enable the optional exact-source regression locally, set `ATLAS_ORIGINAL_JSON=/authorized/path/to/atlas.json`.

**Not implemented in this module:** authenticated and permission-filtered SwarmChat host READ/RETURN; live OpenAlex refresh; actual source-wide expert semantic adjudication; private-mode ingestion; graph promotion; deployment; model-weight upgrades. Production access must be enforced by an independently trusted publisher manifest and host-owned principal/rights checks *before any private index query and again at egress*. Do not pass caller-authorized booleans as IAM.

This change preserves existing legacy Sheldonbrain behavior and creates a separately reviewable Ariadne-native path. No original private files or bulk candidate matrices are committed to this public repo.
