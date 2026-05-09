# GPTBrain / S1 — Cognitive Infrastructure Memory Palace Code

**Status:** lightweight implementation scaffold / not canon  
**Seat:** S1 — GPTBrain / Cognitive Infrastructure / Calibration  
**Purpose:** Convert raw logs and archive context into GPTBrain memory artifacts: metadata, event indexes, artifact registry entries, claim ledger entries, memory packet JSON, and a boot packet.

This is the code translation of the GPTBrain memory palace spec:

- fossil record first
- parsed artifacts as operating memory
- strict evidence/canon boundaries
- no hidden memory claims
- no model-weight memory claims
- no autonomous authority

## What This Does

`gptbrain_core.py` is dependency-free Python. It can run in a sandbox, terminal, or future automation without Qdrant/OAuth/API keys.

Input:

- raw `.txt` log or transcript
- source label
- session label
- privacy status

Output:

```text
metadata.json
turns.jsonl
events.jsonl
artifact_registry.jsonl
claim_ledger.jsonl
memory_packet.json
BOOT_PACKET.md
```

## Usage

```bash
python gptbrain_core.py raw_log.txt \
  --label grok-thread-01 \
  --source Grok \
  --privacy public \
  --out ./out
```

## Evidence Boundary

```text
raw log = evidence
parser output = retrieval aid
model assessment = evaluator signal
hypothesis = unscored claim
candidate canon = review-ready artifact
ratified canon = published through Council workflow
```

## Core Files

- `gptbrain_core.py` — CLI + parser + generators
- `README.md` — this file

## Designed Outputs

### `metadata.json`

Integrity and source metadata: hash, size, line count, detected turns, event count.

### `turns.jsonl`

Heuristic turn splits with role guesses, tags, and text previews.

### `events.jsonl`

High-signal tagged events extracted from turns.

### `artifact_registry.jsonl`

Candidate artifact rows with source lineage and confidence class.

### `claim_ledger.jsonl`

Detected claims with safe wording and confidence level.

### `memory_packet.json`

S1 memory packet compatible with the GPTBrain spec.

### `BOOT_PACKET.md`

Human/model-readable boot packet for future GPTBrain sessions.

## Guardrail

This tool does not make outputs canon. It only turns raw evidence into structured retrieval aids and review packets.

## Next Improvements

- Add Sphere144 classifier integration.
- Add redaction mode.
- Add direct GitHub commit package generation.
- Add seat-specific modes for S2/S3/S4/S5/S7.
- Add `--claim-review` mode for user-provided assertions.
- Add JSON Schema validation.
