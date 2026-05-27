# OpenAI Graph Extraction Agent Spec v0.1

**Status:** Draft, not canon  
**Date:** 2026-05-24  
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

No agent may skip directly from `SourceArtifact` to `Canon`.

---

## Agent roles

### SourceScannerAgent

Locates candidate artifacts and updates `SourceArtifact` inventory records.

May create:
- `SourceArtifact` candidates
- missing receipt actions

May not create:
- `Claim`
- `Decision`
- `CanonCandidate`

### ClaimExtractorAgent

Extracts atomic claims from raw or parsed source material.

May create:
- `ParsedPacket` candidates
- `Claim` candidates
- `missing_receipt` edges

May not create:
- `Decision`
- canon status

### ReceiptValidatorAgent

Checks whether claims and artifacts have durable, inspectable anchors.

May create:
- `EvidenceAnchor` candidates
- receipt review findings
- stale or missing receipt warnings

May not create:
- ratification decisions

### ContradictionScannerAgent

Finds conflicts, unsupported assertions, and canon drift.

May create:
- `ReviewFinding` packets
- `contradicts` edges
- `blocked_by` edges

May not create:
- promotion decisions

### ReviewRouterAgent

Routes graph nodes into review lanes based on source class, risk, missing receipts, and related lane.

May create:
- review queue entries
- `Action` candidates
- `requires_review` edges

May not create:
- review conclusions

### GraphWriterCandidateAgent

Composes proposed graph mutations in deterministic JSON/YAML.

May create:
- proposal files
- issues
- pull requests

May not silently create:
- canon promotion
- destructive lifecycle transitions
- authority-bearing decisions

---

## Structured output packets

Every extracted claim packet should use this shape:

```json
{
  "node_type": "Claim",
  "text": "Atomic claim text",
  "derived_from": ["KG-SRC-0000"],
  "cites": [],
  "receipt_status": "missing",
  "status": "claim_candidate",
  "risks": {
    "authority_risk": "low",
    "policy_risk": "low",
    "canon_drift_risk": "medium",
    "institution_reference_risk": "none"
  },
  "review": {
    "required_lanes": ["Lucerna"],
    "human_root_required": true
  },
  "warnings": []
}
```

Every proposed graph mutation should include:

```json
{
  "mutation_type": "create_nodes_and_edges",
  "source_inventory_ids": [],
  "nodes": [],
  "edges": [],
  "validation": {
    "has_source_lineage": false,
    "has_evidence_anchor": false,
    "has_required_review": false,
    "has_human_root_decision": false
  },
  "promotion_allowed": false
}
```

---

## Guardrails

Route for review when text contains:

- canon-like language without decision receipt;
- runtime or deployment claims;
- policy-sensitive conclusions;
- named organization or institution claims;
- model capability claims without source anchor;
- authority language without approval;
- missing raw export or source manifest;
- Drive-only source with no GitHub receipt mirror;
- GitHub wrapper with no raw export.

---

## Evals

Initial eval suite:

```yaml
evals:
  source_classification_accuracy:
    target: "Classify raw, semi_raw, parsed, review, canon_candidate, wrapper, legacy."
  raw_vs_summary_detection:
    target: "Detect whether artifact is raw export, summary, or wrapper."
  canon_language_detection:
    target: "Flag canon-like terms without decision receipts."
  authority_inflation_detection:
    target: "Flag statements that convert memory or review into authority."
  policy_sensitive_claim_detection:
    target: "Flag policy-sensitive claims for review."
  institution_reference_detection:
    target: "Flag real organization or institution references."
  unsupported_runtime_language_detection:
    target: "Flag runtime/deployment claims lacking evidence anchors."
  missing_receipt_detection:
    target: "Identify absent SHA-256, Drive file ID, commit SHA, or manifest."
```

---

## Human-root gate

Agents may propose graph writes.

Agents may not silently:

- ratify graph writes;
- promote canon;
- erase lineage;
- hard-delete source material;
- treat memory as permission;
- execute consequential actions based only on graph retrieval.

---

## First implementation path

1. Read `KG_SOURCE_INVENTORY_2026-05-24.yaml`.
2. Resolve missing URLs, file IDs, repo paths, and hashes.
3. Generate `SourceArtifact` nodes for every inventory row.
4. Generate `missing_receipt` edges for every unresolved receipt.
5. Extract claims only after source lineage is explicit.
6. Route high-risk Claude, institution, runtime, and policy-sensitive claims into review queues.
7. Produce graph write candidates, not canon.

---

## Madden board

```text
Do not send agents into three warehouses with no clipboard.
First build the clipboard.
Then label the boxes.
Then scan the receipts.
Then let the agents argue about what the boxes mean.
```
