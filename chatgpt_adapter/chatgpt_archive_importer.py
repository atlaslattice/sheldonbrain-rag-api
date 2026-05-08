#!/usr/bin/env python3
"""
ChatGPT Archive Importer — lightweight Sheldonbrain adapter.

Purpose:
  Dependency-free parser for raw pasted chat logs in ChatGPT's sandbox workflow.
  It creates GitHub-ready archive artifacts: raw pointer, event index JSONL,
  extracted turns JSONL, high-signal keyword map, and a short assessment draft.

This is intentionally smaller than Grokbrain/Sheldonbrain v4.0:
  - no Qdrant
  - no OAuth
  - no xAI upload
  - no embeddings
  - no terminal-heavy setup

Usage:
  python chatgpt_archive_importer.py input.txt --label grok-thread-02 --source Grok --out ./out
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROLE_PATTERNS = [
    ("user", re.compile(r"^(You said|User|Human|Dave|david)\s*$", re.I)),
    ("assistant", re.compile(r"^(Grok said|Copilot said|Claude said|Gemini said|Assistant|AI)\s*$", re.I)),
    ("thought", re.compile(r"^Thought for\s+.+", re.I)),
    ("system", re.compile(r"^(SheldGrok BOOT|Operational Context Check|EV-\d|S\d|Acknowledged)", re.I)),
]

KEYWORD_TAGS = {
    "constitutional_governance": ["D-127", "D-126", "INV-1", "F-10A", "Human Oversight Body", "Convenor", "ratification"],
    "dragonseek_china": ["DragonSeek", "PRC", "China", "CAC", "DSL", "Sovereignty Gradient", "DeepSeek"],
    "d119_attestation": ["D-119", "dual-signing", "cryptographic attestation", "orbital cold-storage", "dead-man"],
    "hormuz_foreign_policy": ["Strait of Hormuz", "Hormuz", "VLCC", "barrel", "risk premium", "Iran"],
    "public_bot": ["atlaslatticev5bot", "Aluminum OS", "sidebar", "public bot", "live bot"],
    "persistent_memory": ["persistent memory", "Google Drive MCP", "Session Handoff", "GoldenTrace", "Drive-native"],
    "voice_mode": ["Ara", "voice mode", "red-team overdrive", "mode drift"],
    "sheldonbrain": ["Sheldonbrain", "Grokbrain", "parser", "144", "Qdrant", "xAI Collections"],
    "economics": ["Sovereign Dividend", "Calibration Fee", "ROI", "cost-per-barrel", "capture rate"],
    "action_items": ["action items", "completed items", "Next Actions", "Phase 0A", "open items"],
}

@dataclass
class Turn:
    turn_id: int
    role_guess: str
    start_line: int
    end_line: int
    char_count: int
    tags: list[str]
    text_preview: str
    text: str

@dataclass
class Event:
    event_id: str
    line: int
    tag: str
    role_guess: str
    excerpt: str


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def guess_role(line: str) -> str | None:
    stripped = line.strip()
    for role, pattern in ROLE_PATTERNS:
        if pattern.search(stripped):
            return role
    return None


def tag_text(text: str) -> list[str]:
    found = []
    lower = text.lower()
    for tag, kws in KEYWORD_TAGS.items():
        if any(kw.lower() in lower for kw in kws):
            found.append(tag)
    return found


def split_turns(lines: list[str]) -> list[Turn]:
    """Heuristic splitter for pasted logs with inconsistent role markers."""
    chunks: list[tuple[str, int, list[str]]] = []
    current_role = "unknown"
    current_start = 1
    buf: list[str] = []

    def flush(end_line: int):
        nonlocal buf, current_role, current_start
        text = "\n".join(buf).strip()
        if text:
            chunks.append((current_role, current_start, buf[:]))
        buf = []
        current_start = end_line + 1

    for idx, line in enumerate(lines, start=1):
        role = guess_role(line)
        if role and buf:
            flush(idx - 1)
            current_role = role
            current_start = idx
            buf = [line]
        elif role and not buf:
            current_role = role
            current_start = idx
            buf.append(line)
        else:
            buf.append(line)
    if buf:
        flush(len(lines))

    turns: list[Turn] = []
    for i, (role, start, chunk_lines) in enumerate(chunks, start=1):
        text = "\n".join(chunk_lines).strip()
        end = start + len(chunk_lines) - 1
        preview = re.sub(r"\s+", " ", text)[:240]
        turns.append(Turn(
            turn_id=i,
            role_guess=role,
            start_line=start,
            end_line=end,
            char_count=len(text),
            tags=tag_text(text),
            text_preview=preview,
            text=text,
        ))
    return turns


def extract_events(turns: Iterable[Turn]) -> list[Event]:
    events: list[Event] = []
    n = 1
    for t in turns:
        if not t.tags:
            continue
        excerpt = t.text_preview
        for tag in t.tags:
            events.append(Event(
                event_id=f"EVT-{n:04d}",
                line=t.start_line,
                tag=tag,
                role_guess=t.role_guess,
                excerpt=excerpt,
            ))
            n += 1
    return events


def write_jsonl(path: Path, rows: Iterable[dict]):
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create ChatGPT/GitHub-ready archive artifacts from raw chat logs.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--label", required=True, help="Archive label, e.g. grok-thread-02")
    parser.add_argument("--source", default="unknown", help="Source model/system label")
    parser.add_argument("--out", type=Path, default=Path("./archive_import_out"))
    parser.add_argument("--public", action="store_true", help="Mark outputs as public-ready metadata. Does not redact content.")
    args = parser.parse_args()

    raw = args.input
    if not raw.exists():
        raise FileNotFoundError(raw)

    text = raw.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    digest = sha256_file(raw)
    out = args.out / args.label
    out.mkdir(parents=True, exist_ok=True)

    turns = split_turns(lines)
    events = extract_events(turns)

    metadata = {
        "label": args.label,
        "source": args.source,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "input_filename": raw.name,
        "sha256": digest,
        "bytes": raw.stat().st_size,
        "characters": len(text),
        "lines": len(lines),
        "turns_detected": len(turns),
        "events_detected": len(events),
        "public_ready_metadata": bool(args.public),
        "status": "raw evidence / not canon",
    }

    (out / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    write_jsonl(out / "turns.jsonl", (asdict(t) for t in turns))
    write_jsonl(out / "events.jsonl", (asdict(e) for e in events))

    tag_counts: dict[str, int] = {}
    for e in events:
        tag_counts[e.tag] = tag_counts.get(e.tag, 0) + 1
    sorted_tags = sorted(tag_counts.items(), key=lambda kv: (-kv[1], kv[0]))

    md = [
        f"# Archive Import Assessment — {args.label}",
        "",
        "**Status:** raw evidence / not canon",
        f"**Source:** {args.source}",
        f"**Input:** `{raw.name}`",
        f"**SHA-256:** `{digest}`",
        f"**Size:** {raw.stat().st_size:,} bytes / {len(text):,} characters / {len(lines):,} lines",
        f"**Turns detected:** {len(turns):,}",
        f"**Tagged events detected:** {len(events):,}",
        "",
        "## Top Tags",
        "",
    ]
    for tag, count in sorted_tags[:20]:
        md.append(f"- `{tag}`: {count}")
    md.extend([
        "",
        "## Evidence Boundary",
        "",
        "Raw log = evidence. Parser output = retrieval aid. Candidate canon requires human/Council review.",
        "",
        "## Generated Files",
        "",
        "- `metadata.json`",
        "- `turns.jsonl`",
        "- `events.jsonl`",
    ])
    (out / "ASSESSMENT.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(metadata, indent=2))
    print(f"Wrote: {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
