# Swarm Hub Batch 001 Scoreboard

```text
STATUS: SWARM HUB SCOREBOARD
CANON: NO
DEPLOYMENT: NO
AUTHORITY: NONE
PURPOSE: track bounded module execution without losing fossils, blockers, or deltas
DOCTRINE: one task -> one return packet; failed branches become fossils; review before promotion
```

Source matrix: [`SWARM_HUB_12x12_OPEN_TASK_MATRIX_2026-05-30.md`](SWARM_HUB_12x12_OPEN_TASK_MATRIX_2026-05-30.md)  
Return packet schema: [`SWARM_RETURN_PACKET_SCHEMA_v0.1.yaml`](SWARM_RETURN_PACKET_SCHEMA_v0.1.yaml)

---

## Status legend

| Status | Meaning |
|---|---|
| `not_started` | Not yet claimed. |
| `claimed` | Owner/seat selected, work not complete. |
| `in_progress` | Active work underway. |
| `blocked` | Needs external receipt, source, decision, or dependency. |
| `returned` | Return packet or output artifact exists. |
| `needs_review` | Output exists but needs lane review. |
| `fossilized` | Attempt failed/drifted; residue preserved. |
| `accepted_candidate` | Useful candidate accepted for next stage, not canon. |

---

## Batch 001 module board

| Module | Name | Priority | Owner lane | Status | Output artifact | Blockers | Next action |
|---|---:|---:|---|---|---|---|---|
| M01 | Source Passport Factory | 1 | Hashlight / Lucerna | `not_started` | TBD | Drive IDs, SHA-256, source manifests unresolved | Create source passport schema |
| M02 | Public Candidate Bundle | 3 | Rootglass | `not_started` | TBD | Needs source passports and release gate | Wait for M01 + M05 seed |
| M03 | Lattice Hypercube Ontology | 10 | Sable Vesper | `not_started` | TBD | Geometry must remain label, not proof | Define coordinate disclaimer |
| M04 | Knowledge Graph Schema Spine | 9 | TIDELOCK / Sable | `needs_review` | `archive/knowledge_graph/KG_NODE_EDGE_SCHEMA_v0.1.yaml` | Existing schema needs reconciliation | Add variant/fossil/source-passport extensions |
| M05 | Sensitive Release Gate | 4 | Rootglass / AtlasBrain | `not_started` | TBD | Public-safe rules not codified | Create release gate checklist |
| M06 | Claude Counter-Review Lane | 11 | Rootglass / Lucerna | `returned` | `archive/knowledge_graph/review_queues/CLAUDE_COUNTER_REVIEW_QUEUE_2026-05-24.md` | Review results not yet attached | Create return packet template |
| M07 | Claim Packet Factory | 5 | Lucerna / Sable | `not_started` | TBD | Source passports missing | Define claim packet schema |
| M08 | Missing Receipt Ledger | 2 | Lucerna / Hashlight | `returned` | `archive/knowledge_graph/ledgers/MISSING_RECEIPTS_LEDGER_2026-05-31.yaml` | Receipts still open; ledger now exists | Resolve MR-20260531-0001..0018 by lane |
| M09 | Toy Graph / Demo | 7 | TIDELOCK / AtlasBrain | `returned` | `archive/knowledge_graph/toy_graphs/TOY_GRAPH_BATCH_001.yaml` | Demo graph uses missing-receipt placeholders | Review query examples and expand to source passports |
| M10 | OpenAI Eval Fixtures | 6 | AtlasBrain / Rootglass | `not_started` | TBD | Need fixtures and expected outputs | Create first eval fixture set from toy graph |
| M11 | Public Communication Layer | 12 | Rootglass | `not_started` | TBD | Release gate missing | Draft public-safe overview later |
| M12 | Return Packets / Scoreboard | 8 | Fossilbranch / TIDELOCK | `returned` | `archive/swarm_hub/SWARM_RETURN_PACKET_SCHEMA_v0.1.yaml`; `archive/swarm_hub/SWARM_HUB_BATCH_001_SCOREBOARD.md` | Needs review, not canon | Review and continue Batch 001 |

---

## Batch 001 active return packets

| Packet ID | Module | Task | Seat | Status | Artifact | Review needed |
|---|---|---|---|---|---|---|
| SWARM-RP-20260531-0001 | M12 | T01 | Fossilbranch | `returned` | `SWARM_RETURN_PACKET_SCHEMA_v0.1.yaml` | Rootglass / Lucerna |
| SWARM-RP-20260531-0002 | M12 | T02 | Fossilbranch | `returned` | `SWARM_HUB_BATCH_001_SCOREBOARD.md` | TIDELOCK / Rootglass |
| SWARM-RP-20260531-0003 | M08 | T01-T12 slice | Fossilbranch | `returned` | `archive/knowledge_graph/ledgers/MISSING_RECEIPTS_LEDGER_2026-05-31.yaml` | Lucerna / Hashlight |
| SWARM-RP-20260531-0004 | M09 | T01-T12 slice | Fossilbranch | `returned` | `archive/knowledge_graph/toy_graphs/TOY_GRAPH_BATCH_001.yaml` | TIDELOCK / AtlasBrain |

---

## Immediate blockers ledger

| Blocker ID | Description | Affects | Owner lane | Status | Next action |
|---|---|---|---|---|---|
| BLK-001 | Drive URLs and file IDs unresolved | M01, M02, M07, M08, M09 | Lucerna | `open` | Resolve source inventory anchors |
| BLK-002 | SHA-256 manifest missing | M01, M08, M09, M10 | Hashlight | `open` | Generate source hash manifest |
| BLK-003 | GitHub PR paths unresolved for PR #61 / PR #57 | M01, M08, M09 | TIDELOCK | `open` | Resolve repo path and commit SHA |
| BLK-004 | Release gate not codified | M02, M05, M11 | Rootglass | `open` | Create release gate checklist |
| BLK-005 | Claim packet schema missing | M07, M09, M10 | Sable / Lucerna | `open` | Create CLAIM_PACKET_SCHEMA_v0.2 |
| BLK-006 | Toy graph nodes are placeholders, not verified evidence | M09, M10 | AtlasBrain | `open` | Use toy graph for eval fixtures only until receipts resolve |

---

## Graph-derived query surface now available

| Query | Current artifact |
|---|---|
| Which artifacts lack source manifests? | `MISSING_RECEIPTS_LEDGER_2026-05-31.yaml` |
| Which selected sources are blocked by missing receipts? | `TOY_GRAPH_BATCH_001.yaml` |
| What should Lucerna do next? | `TOY_GRAPH_BATCH_001.yaml` action node `KG-NODE-0011` |
| Which claims are canon candidates but not canon? | `TOY_GRAPH_BATCH_001.yaml` claim nodes `KG-NODE-0004`, `KG-NODE-0005` |

---

## Operating cadence

1. Claim one bounded task.
2. Produce one return packet.
3. Attach output artifact path.
4. Preserve blockers instead of smoothing them away.
5. Mark review lanes.
6. Promote nothing to canon from this board.

---

## Keeper

```text
The hub coordinates.
The hub does not crown.
The hub routes work.
The hub preserves failed branches.
The hub turns motion into receipts.
```
