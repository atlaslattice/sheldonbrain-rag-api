# OpenAI-Grade Product Spine: Sheldonbrain RAG API

**Status:** Draft product spine  
**Date:** 2026-05-21  
**Repo:** `atlaslattice/sheldonbrain-rag-api`  
**Product thesis:** Turn Sheldonbrain from a useful RAG endpoint into a trusted multi-agent memory substrate with provenance, consent, auditability, and non-destructive lifecycle controls.

---

## 1. One-sentence product definition

Sheldonbrain is a shared, ontology-aware memory API that lets multiple AI agents store, retrieve, classify, preserve, and audit knowledge across sessions without treating lost context as dead context.

---

## 2. Product promise

Most AI systems fail at continuity. They either forget, hallucinate a memory, or collapse complex prior work into lossy summaries.

Sheldonbrain should become the continuity layer that says:

```text
Nothing disappears silently.
Nothing becomes canon without provenance.
Nothing executes merely because it was remembered.
```

That makes it more than RAG. It becomes a memory governance layer.

---

## 3. Current foundation

The existing system already has a strong base:

- Flask REST API with `/health`, `/query`, `/store`, `/classify`, and `/lattice` endpoints.
- Gemini `text-embedding-004` embeddings.
- Pinecone vector database.
- 12x12+1 lattice ontology metadata.
- Multi-agent use case across GPT, Claude, Gemini, Grok, and other agents.
- Declared Zero Erasure / persistent memory intent.

The strongest current product insight is that the API already combines three things most RAG products keep separate:

1. semantic retrieval,
2. ontology classification,
3. cross-agent continuity.

That is the wedge.

---

## 4. Product-grade invariant stack

### INV-0: Nothing dies

No record should be hard-deleted through normal product flows. Instead use lifecycle states:

```text
active -> superseded -> archived -> quarantined -> redacted_pointer
```

A user-facing delete request should become a governed retention operation:

- hide from default retrieval,
- preserve a tombstone,
- retain audit lineage,
- optionally preserve a salted hash / receipt,
- allow legal/privacy redaction modes where required.

### INV-1: Memory is not authorization

Retrieved memory can inform an answer, but cannot authorize tool execution, external writes, financial action, medical/legal action, or irreversible changes.

Every tool-executing agent must treat Sheldonbrain output as context, not permission.

### INV-2: Provenance before confidence

Every stored memory should carry enough metadata to answer:

- who or what generated it,
- when it was generated,
- what source conversation or artifact it came from,
- what model or agent transformed it,
- whether it is raw, summarized, inferred, contradicted, or ratified.

### INV-3: Search is not canon

High similarity does not mean truth. Query responses should expose:

- vector score,
- provenance score,
- ratification status,
- contradiction state,
- freshness / staleness,
- ontology location.

### INV-4: Receipts beat vibes

The system should bias toward evidence trails over elegant synthesis. Beautiful summaries are allowed, but they must remain subordinate to source receipts.

---

## 5. Target users

### Primary user: multi-model power user

Someone using several AI systems at once who needs persistent continuity across sessions, models, and vendors.

### Secondary user: AI product team

A team building agents that need durable, inspectable memory with governance controls.

### Tertiary user: institution or lab

An organization that needs auditable knowledge preservation, research memory, and model-agnostic continuity.

---

## 6. Minimum lovable product

The first lovable product should not try to be a complete OS. It should be a memory control plane.

### Required capabilities

1. Store memory with structured provenance.
2. Query memory with ontology and metadata filters.
3. Classify text into lattice coordinates.
4. Preserve lifecycle states instead of hard deleting.
5. Return explainable retrieval receipts.
6. Provide agent-safe response envelopes.
7. Export portable archives.
8. Support human review / ratification.

### Required surfaces

- REST API for agents.
- CLI for humans and scripts.
- Minimal web console for inspection.
- OpenAPI schema for SDK generation.
- Docker / Cloud Run deploy path.

---

## 7. API shape v3

### `POST /v3/memory/store`

Stores a memory with text, metadata, provenance, ontology classification, and lifecycle defaults.

Required envelope:

```json
{
  "text": "...",
  "source": {
    "agent": "gpt",
    "model": "gpt-5.5-thinking",
    "session_id": "optional",
    "artifact_uri": "optional"
  },
  "metadata": {
    "sphere": "optional override",
    "tags": [],
    "status": "raw"
  }
}
```

### `POST /v3/memory/query`

Returns memories plus receipts.

Response should include:

```json
{
  "query": "...",
  "results": [
    {
      "id": "mem_...",
      "text": "...",
      "score": 0.91,
      "ontology": {},
      "provenance": {},
      "lifecycle": "active",
      "ratification": "unratified",
      "warnings": []
    }
  ],
  "retrieval_receipt": {
    "timestamp": "...",
    "filters": {},
    "index": "...",
    "namespace": "..."
  }
}
```

### `POST /v3/memory/lifecycle`

Replaces destructive deletion.

Supported operations:

```text
archive
quarantine
supersede
redact_pointer
restore
```

### `POST /v3/memory/ratify`

Marks a memory as reviewed, corrected, rejected, or promoted to canonical status.

### `GET /v3/ontology/lattice`

Returns houses, spheres, descriptions, version, and source commit.

### `GET /v3/health`

Returns service health, index health, ontology version, vector count, model config, namespace, and degraded-mode flags.

---

## 8. Data model

Minimum durable memory record:

```json
{
  "id": "mem_...",
  "text": "...",
  "embedding_ref": "pinecone://index/namespace/vector_id",
  "ontology": {
    "version": "12x12+1-v2.0",
    "house": "H02",
    "sphere": "H02.S11",
    "house_name": "...",
    "sphere_name": "..."
  },
  "provenance": {
    "created_at": "...",
    "created_by_agent": "...",
    "created_by_model": "...",
    "source_type": "chat|file|repo|manual|api",
    "source_uri": "...",
    "transform_chain": []
  },
  "governance": {
    "lifecycle": "active",
    "ratification": "unratified",
    "sensitivity": "normal",
    "execution_authority": false
  },
  "receipts": {
    "content_hash": "sha256:...",
    "previous_record": null,
    "supersedes": []
  }
}
```

---

## 9. Trust and safety boundary

The memory layer must not become an invisible authority system.

Hard rules:

- No memory grants permission to execute external actions.
- No retrieved memory overrides current user consent.
- No destructive deletion without lifecycle receipt.
- No private/sensitive expansion without user-visible basis.
- No canon promotion without ratification metadata.
- No model should silently rewrite provenance.

This keeps the system compatible with serious product use rather than just personal mythology.

---

## 10. Engineering roadmap

### Phase 0: Lock the invariant

- Replace `/delete` implementation with lifecycle transition or add `/lifecycle` and deprecate `/delete`.
- Add lifecycle metadata to every store response.
- Add migration script to tag existing records as `active`.

### Phase 1: Receipts

- Add content hash.
- Add source metadata schema.
- Add retrieval receipt to `/query`.
- Add OpenAPI schema.

### Phase 2: Product surface

- Add CLI: `sheldonbrain store`, `query`, `classify`, `archive`, `ratify`.
- Add minimal web console.
- Add examples for GPT, Claude, Gemini, and generic HTTP agents.

### Phase 3: Governance

- Add ratification workflow.
- Add contradiction tracking.
- Add role-aware response envelopes.
- Add export / backup / restore story.

### Phase 4: OpenAI-grade integration path

- Provide a clean tool contract that any agent can call.
- Add deterministic JSON schemas.
- Add eval fixtures for retrieval correctness, provenance preservation, and non-destructive lifecycle behavior.
- Add a `memory_is_not_authorization` test suite.

---

## 11. Definition of done

The product is ready to show seriously when a reviewer can:

1. run it locally,
2. store a memory,
3. query it with a receipt,
4. classify it into the lattice,
5. archive it without hard deletion,
6. inspect provenance,
7. verify that retrieval does not grant execution authority,
8. export the memory log,
9. understand the product in five minutes from the README.

---

## 12. North star

The best version of this product is not “a vector database wrapper.”

It is the continuity substrate for multi-agent work: a place where memory, provenance, ontology, and consent are kept together so advanced AI collaboration can become durable without becoming reckless.

```text
visibility != authorization
receipt != approval
simulation != execution
memory != permission
```

That is the product spine.
