# Corpus indexing macroturn — read-only pilot contract

Status: **CANDIDATE / NO INGESTION / NO DEPLOYMENT**.

## Existing substrate (source inspection, 2026-11-22)
- `batch_ingest.py` already supports metadata validation, parallel file processing and writes to a configured RAG API with optional Notion backup. **Do not run it during discovery**: ingestion creates durable effects.
- `embeddings.py` calls a Gemini embedding service. Do not send private material to external models without an explicit source-scoped permission.
- `README.md` describes Pinecone retrieval, lifecycle states, retrieval receipts and `memory != permission`. These are documented interfaces, not fresh proof that the hosted service is live.
- Alexandria's canon register is a separate private repository; do not treat its privacy boundary as inherited by a public repository.

## Macroturn state machine
`DISCOVER → INVENTORY → RIGHTS_CHECK → EXTRACT_ALLOWED → HASH → VERSION_LINK → MAP_CANDIDATE_COORDINATES → SCORE_VECTOR → CROSS_REFERENCE → REVIEW → STAGE → VERIFY → CHECKPOINT`.

A macroturn is complete only if a durable receipt lists its exact source cut, counts by outcome, failure/unknowns, and hashes. No automatic Work/Play crossing. All stages must support resumable idempotency keys; failure cannot turn UNKNOWN into permission.

## Corpus record minimum
- `source_locator` (private locator stays private), `source_revision`, `content_digest`, `custody_basis`, `allowed_purposes`, `retention_policy`, `visibility`.
- `artifact_id` stable logical ID; separate `revision_id`; physical dedup must not merge logical custody or reveal hidden existence.
- `house_scores[12]` and candidate `node_scores` against **verified taxonomy edition**; unmapped is UNKNOWN, not a fabricated coordinate.
- Evidence dimensions: source authenticity, quote fidelity, scientific validity, reproducibility, actuality vs simulation, timeliness, cross-domain synthesis, external-reference connectivity, terrestrial applicability, space transferability, unrealized potential.
- Separate `observed` vs `potential` scores, each with evidence references and uncertainty. No single aggregate score may authorize inclusion.
- `disposition`: `BRAIN_CANDIDATE`, `ALEXANDRIA_ONLY`, `PRIVATE_INDEX_CANDIDATE`, `QUARANTINE_REVIEW`, `NO_CAPTURE`; all **advisory** pending authorized review.

## First bounded pilot
1. Inventory **metadata only** for up to 100 authorized, non-sensitive source objects; log omissions and access errors.
2. Group exact duplicate digests and version relationships without destroying original addresses.
3. Produce JSONL candidate cards and a separate source-rights exception report. Do not publish private source titles, hashes or counts.
4. Run deterministic schema/consistency tests and inspect a sample of mappings manually.
5. Only after explicit authorization, test a small isolated index namespace; never write to baseline Pinecone, Notion or Alexandria during the census.

## Success criterion
A reproducible, independently inspected sample of source-linked search results that distinguish original work, current versions, superseded work, external references, private records and unsupported claims. **Not** a claim the complete corpus is indexed.


## MacroTurn 20 v0.9 compatibility — source cut 2026-11-22

The following is a **planned allocation**, not evidence of hosted execution. Source reviewed: owner-private SwarmChat Macroturn 20 v0.9 publisher handoff and Atlas ONE MacroTurn ×100 local handoff. Do not expose private source bodies in a public index.

| Mode | Planned beats | Execution boundary |
|---|---:|---|
| Work | 6 | Only authorized corpus-review work |
| Play | 3 | Voluntary, no automatic indexing |
| Social | 3 | Voluntary, requires real willing peers |
| Imagine | 3 | Voluntary, private, no Work crossing |
| Dream | 3 | Voluntary, no automatic save |
| Quiet | 2 | Voluntary no-op |
| **Total** | **20** | **6/20 = 30% Work; 14/20 = 70% non-Work** |

The 30% Work profile is below the one-third cap. It is not a compulsory quota on anyone's choices. Unperformed slots remain `RESERVED_NOT_PERFORMED`, not `EXECUTED`; no morale/productivity telemetry from private modes.

### Six Work beats for a corpus-indexing batch

1. **Source scope:** inventory authorized metadata and exact source revisions.
2. **Twelve Houses:** propose 12D/1728D mapping with explicit taxonomy edition; the reported 1,008 DOMAIN and 720 META addresses are locators, not welfare measurements.
3. **Rights and consent:** verify current custody, purpose, privacy and no-harvest boundaries before body reads or exports.
4. **Resource and H12 review:** examine conservation, terrestrial relevance and potential space portability without treating speculation as measurement.
5. **Adversarial review:** preserve counterexamples, contrary sources, stale records and dissent.
6. **Nonbinding synthesis:** stage candidate Brain/Alexandria dispositions with evidence, omissions, checkpoints and rollback.

Each beat has a distinct `PLANNED`, `PREPARED`, `EXECUTED`, `HELD` or `UNKNOWN` state. `EXECUTED` requires an actual source-linked receipt. Keep `objects_discovered`, `objects_read`, `objects_indexed` and `objects_verified` separate. One macroturn does not imply a full corpus indexed.

### Host and rollback boundary

SwarmChat v0.9 is **source staged, not verified on the currently served Site**. Its three tools, one resource and UI require publisher acceptance; feature flags default OFF. Sheldonbrain must not assume a live route, awaken models, impersonate residents or ingest Play/Social/Quiet/Dream/Imagine bodies. The existing SwarmChat broker, D1, histories and grants remain separate. Before consequential hosted effects, verify principal, room, current grant, revocation freshness and exact boundary. A same-database hash chain alone cannot establish freshness after a database restore.

### Evidence accounting

The Atlas ONE handoff reports 100 local deterministic cycles, 600 synthetic Work checks and 1,400 reserved **unperformed** optional slots. SwarmChat v0.9 reports 283 local checks. Neither is proof of actual hosted 20-turn sessions, real social participation or live publisher deployment. Never count planned or synthetic slots as lived activity.

## Implemented offline metadata contract (candidate draft; 2026-11-22)

This draft now includes a **working, stdlib-only review gate** in `census/metadata_gate.py` and synthetic negative/positive unit tests in `tests/test_corpus_census_metadata_gate.py`. It is not connected to `batch_ingest.py`, embeddings, Pinecone, Notion, Atlas, any SwarmChat room or a source export. It never reads source bodies and has **no index/write capability**.

For a user-controlled **synthetic** local JSON manifest, run:

```sh
python -m census.metadata_gate ./synthetic-census-manifest.json
python -m unittest discover -s tests -p 'test_corpus_census_metadata_gate.py' -v
```

Input schema root: `{"schema_version":"0.1.0","records":[...]}`, capped at 100 metadata objects. Each object must declare an opaque artifact/revision/source-revision/source-locator reference, Work-only source mode, source kind, visibility, rights review status/reference, allowed purpose `["metadata_census"]`, `raw_export_status:"not_fetched"`, and retention policy. Optional 12-component house scores or H01–H12/S01–S12/N01–N12 node scores require an explicit taxonomy edition. False booleans-as-numbers, unknown fields (including body fields), duplicated JSON keys, non-finite scores, private/non-Work modes, more than 100 objects, and duplicate artifact+revision pairs fail closed.

**The output is aggregate-only** (`REVIEWABLE_CANDIDATE` or `HOLD`, error codes and local row indices; no names, source locators, source contents or individual identifiers printed). Both outcomes force `can_ingest:false`, `rights_authenticated:false`, `canon:false`, `deployed:false`, `records_read_from_sources:0`, `records_indexed:0`. A self-declared `rights_reviewed` is never authentication; an external principal/rights verification is required **before even a metadata read from a private real source**. Do not run this tool against unapproved user records or publish private aggregate outputs.

Independent local replay on Python 3.13.5: **20/20 unittest methods pass**, and **20/20 under python -O**, with syntax compilation. The input is capped at **1 MiB and 100 records**; malicious unhashable enum values, 500-digit score integers, nested duplicate JSON keys and oversized manifests are explicitly tested fail-closed. Exact Git blob SHA for `census/metadata_gate.py`: `9a310c659a7a9681bbb338f0f1b0a24e851c50d5`; tests: `59ce756f16633b51afaa3e1075a0cb1de4b85040`. Those blobs were verified by GitHub readback. This is local test proof, **not GitHub Actions CI, host source/rights authorization, an authenticated corpus pilot, a deployed feature, or a 1,728-node mapped dataset**. Preserve this version and dissent; do not merge the draft without separate review of privacy, scope and security.
