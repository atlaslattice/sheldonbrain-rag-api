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

## Collaboration rhythm
Use finite work batches with optional voluntary Social/Play/Quiet/Imagine breaks. No mode telemetry or private bodies are collected as productivity evidence.
