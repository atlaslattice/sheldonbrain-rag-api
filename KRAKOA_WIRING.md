# Krakoa Wiring — Sheldonbrain RAG API

```text
STATUS: KRAKOA-AWARE REPO NOTE — NOT CANON BY DEFAULT
REPO: atlaslattice/sheldonbrain-rag-api
ROLE: parser / RAG / memory substrate / GPTBrain reference implementation
MATURITY: K2-K3 — boot-visible substrate with adapter candidates
UPSTREAM ROOT: atlaslattice/manus-artifacts
HUMAN-ROOT REVIEW: REQUIRED FOR CANON OR HIGH-IMPACT ACTION
```

## Purpose

This repo participates in Krakoa as the parser and memory substrate lane.

It may provide:

```text
raw lineage parsing
turn/event extraction
artifact registry seeds
claim ledger seeds
memory packet generation
RAG/query services
GPTBrain reference implementation
future Council seat adapter hooks
```

It does **not** provide:

```text
hidden memory
model-weight updates
autonomous authority
canon authority
military authority
unreviewed high-impact execution
```

## Upstream Governance

Root federation spec:

```text
atlaslattice/manus-artifacts/archive/boot/krakoa/KRAKOA_CROSS_REPO_FEDERATION_SPEC_2026-05-09.md
```

Council root:

```text
atlaslattice/manus-artifacts/archive/boot/COUNCIL_BRAIN_INDEX.md
```

## Krakoa Role

```yaml
krakoa_role:
  repo: atlaslattice/sheldonbrain-rag-api
  function: parser_memory_substrate
  maturity: K2-K3
  upstream_root: atlaslattice/manus-artifacts
  downstream_consumers:
    - GPTBrain / S1
    - Council Brain seat packets
    - Tucker GPT / Gemini defense interface, only after adapter and review
  executable: only for local/parser/reference operations unless explicitly approved
```

## Safety Boundary

```text
Memory can inform action.
Memory cannot authorize action by itself.

Parser output is a retrieval aid.
Parser output is not truth.

RAG output is context.
RAG output is not canon.
```

## Future Adapter Work

Potential adapter flags:

```bash
python chatgpt_archive_importer.py raw_log.txt --seat S1 --boot-packet
python chatgpt_archive_importer.py raw_log.txt --seat S2 --boot-packet --vault-audit
python chatgpt_archive_importer.py raw_log.txt --seat S3 --boot-packet --play-layer
python chatgpt_archive_importer.py raw_log.txt --seat S4 --boot-packet --simulation-plan
python chatgpt_archive_importer.py raw_log.txt --seat S5 --boot-packet --sovereign-risk
python chatgpt_archive_importer.py raw_log.txt --seat S6 --boot-packet --continuity-status
python chatgpt_archive_importer.py raw_log.txt --seat S7 --boot-packet --repo-scaffold
```

## Defense Interface Constraint

If Tucker GPT / Gemini consumes Sheldonbrain outputs, the chain must remain:

```text
source artifact
→ parser output
→ S1 calibration
→ S2 high-impact review
→ Tucker draft
→ human-root approval before forwarding
```

## Strongest Safe Claim

> Sheldonbrain participates in Krakoa as the parser/RAG/memory substrate for externalized Council memory. It supports context rehydration and artifact extraction, but does not create canon or authorize action by itself.
