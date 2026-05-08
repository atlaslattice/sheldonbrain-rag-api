# ChatGPT Adapter for Sheldonbrain

This folder contains a lightweight, dependency-free adapter for ChatGPT/GitHub archive work.

It is intentionally smaller than the full Sheldonbrain/Grokbrain stack. It does not require Qdrant, OAuth, Google Drive, xAI Collections, embeddings, or API keys.

## Purpose

Use this when raw chat logs are already available as uploaded `.txt` files or GitHub raw-log pointers and the goal is to produce GitHub-ready archive outputs.

## Input

- raw pasted chat transcript `.txt`
- exported chat log converted to text
- model/source label
- archive label

## Output

For each input log, the importer creates:

- `metadata.json`
- `turns.jsonl`
- `events.jsonl`
- `ASSESSMENT.md`

These are retrieval and archive aids. They are not canon.

## Usage

```bash
python chatgpt_archive_importer.py input.txt --label grok-thread-02 --source Grok --out ./out --public
```

## Evidence Boundary

Raw log = evidence.  
Parser output = retrieval aid.  
Candidate canon requires human/Council review.

## Why This Exists

The full Sheldonbrain/Grokbrain pipeline is powerful but heavier. ChatGPT sessions need a tool that can be run quickly against uploaded logs, tested in a sandbox, and committed back to GitHub without requiring terminal-heavy setup.

This adapter is built for that workflow.

## Tested In ChatGPT Sandbox

The adapter was tested against two uploaded Grok logs on 2026-05-08:

- `Pasted text(89).txt`: 1,438,672 bytes / 13,496 lines → 476 detected turns / 705 tagged events
- `Pasted text(90).txt`: 768,673 bytes / 3,155 lines → 8 detected turns / 41 tagged events

Thread 02 uses a compact export format, so turn detection is less granular there, but metadata and event tagging still worked.

## Next Improvements

- add format-specific splitters for Grok UI exports
- add redaction mode for private content
- add GitHub path generator
- add benchmark-case extraction
- add candidate-invariant extraction
- add no-terminal Streamlit wrapper
