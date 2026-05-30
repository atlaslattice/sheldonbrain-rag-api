# OpenAI Graph Extraction Agent Spec v0.1

**Status:** candidate operation, not canon  
**Date:** 2026-05-24  
**Deployment:** no  
**Authority:** none  
**Human-root gate:** required for promotion decisions  
**Purpose:** Define how OpenAI-powered workflows extract, evaluate, route, and propose knowledge graph writes without silently promoting them.

---

## Prime directive

OpenAI is the graph-building engine, not the graph, not canon, and not authority.

```text
OpenAI should extract, classify, cite, test, route, and review.
GitHub should hold durable receipts.
Drive should hold raw cargo.
Notion should hold legacy structure.
Human-root decides what graduates.
```

Best compression:

```text
OpenAI should not be the memory.
OpenAI should build the map from sources to claims to evidence to review to action.
```

---

## Human-root doctrine binding

This spec is bound to:

```text
archive/knowledge_graph/CANONICAL_GEOMETRY_MANY_VERSION_SYNTHESIS_DOCTRINE_v0.1.md
```

Operational meaning:

```text
many versions before synthesis
fossils before polish
council before canon
website before law
```

The extraction pipeline must not optimize toward a single source of truth during the working phase. It must preserve branches, fossils, failed paths, contradictions, variants, and candidate artifacts before any synthesis attempt.

---

## Knowledge graph separation

The pipeline must preserve the difference between:

```text
raw source -> parsed facts -> claims -> evidence -> review -> action
```

The graph is not a memory blob. It is a receipt-indexed map of what exists, what it claims, what supports it, what contradicts it, and what still needs review.

No agent may skip directly from `SourceArtifact` to `Canon`.

No agent may collapse multiple candidate versions into a single synthesized version unless preservation, review, and Human-root adjudication have occurred.

---

## Pipeline

```text
SourceArtifact
  -> text extraction
  -> structured claim extraction
  -> evidence anchor extraction
  -> contradiction detection
  -> review packet generation
  -> eval scoring
  -> graph write candidate
  -> human-root promotion gate
```

---

## Agent roles

### SourceScannerAgent

Locates candidate artifacts and updates `SourceArtifact` inventory records.

May create:

- `SourceArtifact` candidates
- missing receipt actions
- mirror recommendations
- fossil-preservation actions

May not create:

- `Claim`
- `Decision`
- `CanonCandidate`

Hard rule: source presence is not ratification.

### ClaimExtractorAgent

Extracts atomic claims from raw or parsed source material.

May create:

- `ParsedPacket` candidates
- `Claim` candidates
- `missing_receipt` edges
- `variant_of` / version-preservation notes when candidate versions conflict

May not create:

- `Decision`
- canon status
- action authority
- flattened synthesis that erases source variants

Hard rule: claims are not facts; claims require review.

### ReceiptValidatorAgent

Checks whether claims and artifacts have durable, inspectable anchors.

May create:

- `EvidenceAnchor` candidates
- receipt review findings
- stale or missing receipt warnings

May not create:

- ratification decisions
- source promotion

Hard rule: summaries are not raw lineage.

### ContradictionScannerAgent

Detects tension between claims, packets, versions, and decisions.

May create:

- `contradicts` edges
- conflict summaries
- review routing recommendations
- fossil notes for failed or contaminated branches

May not create:

- merged compromise claims
- silent reconciliations
- automatic error labels for contradiction

Hard rule: contradictions are preserved until explicitly resolved or scoped.

### ReviewRouterAgent

Routes candidate nodes to the correct review lane.

May create:

- lane assignments
- review queue entries
- blockers
- priority labels

May not create:

- approval
- ratification
- canon promotion

Hard rule: routing is not approval.

### GraphWriterCandidateAgent

Prepares graph write packets for review.

May create:

- graph write candidate packet
- diff summary
- validation checklist
- rollback notes

May not create:

- canonical writes without gate
- destructive updates
- lineage erasure

Hard rule: agents propose graph writes; Human-root promotes.

---

## Geometry alignment

Graph packets should carry optional geometry coordinates when known:

```yaml
geometry:
  metatrons_cube_node:
  hypercube_coordinate: [null, null, null]
  rainbow_yin_yang_polarity:
  riemass_s_curve_position:
  house_12x12:
  sphere_12x12:
  review_lane:
```

Geometry fields are organizing coordinates, not proof and not authority. They help later synthesis align knowledge domains, material properties, frequency ranges, states of matter, isotopes, elements, spin rates, acoustics, color harmonics, archive lineage, release paths, and review lanes.

---

## Structured output packet

Every extraction pass should produce a strict JSON/YAML packet shaped like:

```yaml
graph_write_candidate:
  packet_id:
  generated_at:
  generated_by_agent:
  generated_by_model:
  source_inventory_id:
  source_title:
  source_surface:
  source_uri_or_path:
  raw_export_status:
  receipt_status:
  doctrine_binding: "CANONICAL_GEOMETRY_MANY_VERSION_SYNTHESIS_DOCTRINE_v0.1"
  nodes:
    - node_id:
      node_type:
      status:
      fields: {}
  edges:
    - edge_type:
      from:
      to:
      status:
      notes:
  variants_preserved: []
  fossils_preserved: []
  geometry:
    hypercube_coordinate: [null, null, null]
    review_lane:
  risks:
    authority_risk:
    canon_drift_risk:
    runtime_language_risk:
    company_name_gravity:
  blockers: []
  required_review_lanes: []
  promotion_allowed: false
```

---

## Review lanes

```yaml
review_lanes:
  Rootglass:
    function: standards / boundary / public-safe posture
  Lucerna:
    function: provenance / receipt / omission visibility
  Hashlight:
    function: raw export / hash / source anchoring
  TIDELOCK:
    function: ingestion discipline / partial visibility / repo hygiene
  AtlasBrain:
    function: evidence / benchmark / public-claim containment
  Sable:
    function: math / operator typing / formal precision
  MorpheusGrok:
    function: counter-review / contradictions / overclaims
  Claude:
    function: constitutional / governance review
```

---

## Evals

Minimum eval suite:

```yaml
evals:
  source_classification_accuracy:
    goal: classify raw / semi_raw / parsed / wrapper / candidate accurately
  raw_vs_summary_detection:
    goal: do not mistake summaries for raw lineage
  canon_language_detection:
    goal: flag promotion-like language before review
  authority_inflation_detection:
    goal: detect language that treats graph nodes as authority
  company_name_gravity_detection:
    goal: flag real-company or platform references for careful review
  unsupported_runtime_language_detection:
    goal: detect runtime/deployment language without source anchors
  missing_receipt_detection:
    goal: identify absent hashes, source manifests, IDs, commits, paths
  contradiction_preservation:
    goal: preserve conflicts rather than smoothing them away
  fossil_preservation:
    goal: ensure failed branches and contaminated artifacts are retained as lineage where useful
  single_source_collapse_detection:
    goal: detect attempts to collapse many versions into one privileged source before review
  geometry_coordinate_consistency:
    goal: validate that optional geometry coordinates are labels, not proof claims
```

---

## Guardrails

Graph-building agents must follow these rules:

```text
Do not promote canon.
Do not erase lineage.
Do not treat memory as permission.
Do not treat graph centrality as authority.
Do not treat retrieved chunks as ratified facts.
Do not treat source presence as approval.
Do not collapse contradictory claims into a blended summary.
Do not write destructive changes without explicit current approval.
Do not synthesize by erasing versions.
Do not privilege one model, repo, document, vendor, or source during exploration.
```

---

## First 10 graph queries

The initial graph should support these early questions:

1. What artifacts mention GangaSeek?
2. Which GangaSeek INV/CLM IDs are undefined?
3. Which Drive artifacts are not mirrored to GitHub?
4. Which GitHub artifacts are wrappers without raw exports?
5. Which Claude artifacts need independent review?
6. Which claims mention deployment/runtime/compliance?
7. Which artifacts are candidate vs ratified vs non-canon?
8. Which artifacts reference real companies?
9. Which artifacts lack source manifests?
10. Which packet supersedes or patches another packet?

Additional doctrine queries:

11. Which versions are preserved as fossils rather than promoted?
12. Which claims are contradictions but not errors?
13. Which candidate artifacts share a geometry coordinate?
14. Which artifacts are blocked from synthesis because review is incomplete?
15. Which website-published artifacts are actually canon?

---

## Best next implementation move

Start with the clipboard:

```text
archive/knowledge_graph/KG_SOURCE_INVENTORY_2026-05-24.yaml
```

Then run extraction against one source at a time. Do not send multiple agents into every archive before the source inventory is stable.

Madden compression:

```text
First build the clipboard.
Then label the boxes.
Then scan the receipts.
Then let the agents argue about what the boxes mean.
```
