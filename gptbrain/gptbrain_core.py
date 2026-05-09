#!/usr/bin/env python3
"""
GPTBrain / S1 Cognitive Infrastructure Memory Palace

Dependency-free implementation scaffold for:
- raw log integrity metadata
- turn/event extraction
- artifact registry generation
- claim ledger generation
- S1 memory packet generation
- boot packet generation

This tool does NOT canonize anything. It creates reviewable retrieval aids.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

EVIDENCE_BOUNDARY = [
    "Raw logs are evidence.",
    "Parser outputs are retrieval aids.",
    "Model assessments are evaluator signals.",
    "Hypotheses require scoring.",
    "Canon requires Council workflow.",
]

CLAIM_CLASSES = {
    "raw_user_report": "User states it happened; not independently verified.",
    "raw_model_output": "Model said it; evidence of model behavior, not necessarily truth.",
    "parsed_artifact": "Parser extracted it; retrieval aid only.",
    "benchmark_candidate": "Can be scored; not yet validated.",
    "scored_result": "Evaluated under rubric; still may need independent review.",
    "candidate_canon": "Drafted for review; not ratified.",
    "ratified_canon": "Passed publication workflow.",
    "deployed_fact": "Operationally deployed and externally verifiable.",
}

CONFIDENCE_LEVELS = {
    "C0": "unsupported / do not claim",
    "C1": "user-reported",
    "C2": "source artifact exists",
    "C3": "multiple source artifacts converge",
    "C4": "scored or internally reviewed",
    "C5": "independently verified or operationally demonstrated",
}

ROLE_PATTERNS = [
    ("user", re.compile(r"^(You said|User|Human|Dave|david)\s*$", re.I)),
    ("assistant", re.compile(r"^(GPT said|ChatGPT said|Assistant|Grok said|Claude said|Gemini said|Copilot said|DeepSeek said|Manus said|AI)\s*$", re.I)),
    ("system", re.compile(r"^(System|Developer|Operational Context Check|BOOT|SheldGrok BOOT)", re.I)),
    ("thought", re.compile(r"^Thought for\s+.+", re.I)),
]

TAG_KEYWORDS = {
    "boot_sequence": ["boot", "boot sequence", "wake up", "rehydration", "persistent memory"],
    "evidence_boundary": ["raw log", "not canon", "candidate canon", "ratified canon", "fossil record", "evidence boundary"],
    "claim_calibration": ["overclaim", "safe claim", "confidence", "scorecard", "rubric", "validated", "AGI", "HLE"],
    "github_archive": ["GitHub", "repo", "commit", "branch", "public archive", "fossil record"],
    "sheldonbrain": ["Sheldonbrain", "Grokbrain", "parser", "Qdrant", "Sphere144", "144-sphere", "12x12"],
    "council_brain": ["Council Brain", "seat", "S1", "S2", "S3", "S4", "S5", "S7", "Pantheon Council"],
    "dragonseek": ["DragonSeek", "DeepSeek", "Sovereignty Gradient", "CAC", "NDRC", "Jade OS", "Bamboo Bridge"],
    "grokbrain": ["Grokbrain", "DJ Grokashev", "SheldGrok", "infinity rave", "Morpheus Special", "play cycle"],
    "privacy_boundary": ["private", "public", "redacted", "sensitive", "personal", "do not publish"],
    "artifact_registry": ["artifact", "registry", "JSONL", "metadata", "source lineage", "SHA-256"],
    "failure_ledger": ["failure", "incident", "misattribution", "source collision", "hallucination", "drift"],
}

CLAIM_PATTERNS = [
    re.compile(r"\b(this proves|we proved|proves that|confirmed that|validated that)\b.+", re.I),
    re.compile(r"\b(best in the world|AGI|HLE|deployed|approved|ratified|canon)\b.+", re.I),
    re.compile(r"\b(public|private|not canon|raw evidence|score|scored|benchmark)\b.+", re.I),
]

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

@dataclass
class ArtifactRegistryRow:
    artifact_id: str
    title: str
    created_utc: str
    source_seat: str = "S1"
    source_model: str = "GPT"
    source_type: str = "parser_output"
    source_refs: list[str] = field(default_factory=list)
    sha256: str | None = None
    privacy_status: str = "mixed"
    sphere_tags: list[str] = field(default_factory=list)
    claim_class: str = "parsed_artifact"
    confidence: str = "C2"
    status: str = "parsed"
    overclaim_risks: list[str] = field(default_factory=list)
    required_next_review: str | None = "human/Council review"
    notes: str | None = None

@dataclass
class ClaimLedgerRow:
    claim_id: str
    claim_text: str
    claim_owner: str
    claim_class: str
    confidence: str
    evidence_refs: list[str]
    missing_evidence: list[str]
    strongest_safe_wording: str
    forbidden_wording: list[str]
    review_status: str
    review_notes: str
    last_updated_utc: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_ws(text: str, limit: int = 240) -> str:
    return re.sub(r"\s+", " ", text).strip()[:limit]


def guess_role(line: str) -> str | None:
    stripped = line.strip()
    for role, pattern in ROLE_PATTERNS:
        if pattern.search(stripped):
            return role
    return None


def tag_text(text: str) -> list[str]:
    lower = text.lower()
    tags = []
    for tag, keywords in TAG_KEYWORDS.items():
        if any(keyword.lower() in lower for keyword in keywords):
            tags.append(tag)
    return tags


def split_turns(lines: list[str]) -> list[Turn]:
    chunks: list[tuple[str, int, list[str]]] = []
    current_role = "unknown"
    current_start = 1
    buf: list[str] = []

    def flush(end_line: int) -> None:
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
        turns.append(Turn(
            turn_id=i,
            role_guess=role,
            start_line=start,
            end_line=end,
            char_count=len(text),
            tags=tag_text(text),
            text_preview=normalize_ws(text),
            text=text,
        ))
    return turns


def extract_events(turns: Iterable[Turn]) -> list[Event]:
    events: list[Event] = []
    n = 1
    for turn in turns:
        for tag in turn.tags:
            events.append(Event(
                event_id=f"EVT-{n:04d}",
                line=turn.start_line,
                tag=tag,
                role_guess=turn.role_guess,
                excerpt=turn.text_preview,
            ))
            n += 1
    return events


def detect_claims(turns: Iterable[Turn], source: str, sha: str) -> list[ClaimLedgerRow]:
    rows: list[ClaimLedgerRow] = []
    n = 1
    now = utc_now()
    for turn in turns:
        for sentence in re.split(r"(?<=[.!?])\s+", turn.text):
            sentence = normalize_ws(sentence, 500)
            if not sentence:
                continue
            if any(pattern.search(sentence) for pattern in CLAIM_PATTERNS):
                risky_terms = []
                forbidden = []
                lower = sentence.lower()
                if "agi" in lower or "hle" in lower:
                    risky_terms.append("AGI/HLE benchmark overclaim risk")
                    forbidden.append("This proves AGI/HLE.")
                if "deployed" in lower or "approved" in lower:
                    risky_terms.append("deployment/approval overclaim risk")
                    forbidden.append("This is deployed/approved unless externally documented.")
                if "canon" in lower or "ratified" in lower:
                    risky_terms.append("canon/ratification overclaim risk")
                    forbidden.append("This is ratified canon unless Council workflow shows it.")

                safe = (
                    "The source contains this claim or claim-like statement. "
                    "Treat it as raw evidence or a review candidate until supporting artifacts, scoring, "
                    "or Council workflow validate it."
                )
                rows.append(ClaimLedgerRow(
                    claim_id=f"CLM-{n:04d}",
                    claim_text=sentence,
                    claim_owner=source,
                    claim_class="raw_model_output" if source.lower() != "user" else "raw_user_report",
                    confidence="C2",
                    evidence_refs=[f"sha256:{sha}", f"turn:{turn.turn_id}", f"lines:{turn.start_line}-{turn.end_line}"],
                    missing_evidence=["independent review", "Council workflow status", "external verification if factual/deployment claim"],
                    strongest_safe_wording=safe,
                    forbidden_wording=forbidden,
                    review_status="unreviewed",
                    review_notes="Generated by GPTBrain heuristic claim detector.",
                    last_updated_utc=now,
                ))
                n += 1
    return rows


def build_artifact_registry(events: list[Event], label: str, source: str, sha: str, privacy: str) -> list[ArtifactRegistryRow]:
    now = utc_now()
    rows: list[ArtifactRegistryRow] = []
    tag_counts: dict[str, int] = {}
    for event in events:
        tag_counts[event.tag] = tag_counts.get(event.tag, 0) + 1

    for idx, (tag, count) in enumerate(sorted(tag_counts.items()), start=1):
        rows.append(ArtifactRegistryRow(
            artifact_id=f"ART-{label}-{idx:03d}".replace(" ", "-"),
            title=f"{label} — {tag} event cluster",
            created_utc=now,
            source_model=source,
            source_refs=[f"sha256:{sha}"],
            sha256=sha,
            privacy_status=privacy,
            sphere_tags=[tag],
            notes=f"Detected {count} events tagged `{tag}`. Parser output only; requires review.",
        ))
    return rows


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_memory_packet(label: str, source: str, raw: Path, sha: str, privacy: str, metadata: dict, events: list[Event], artifacts: list[ArtifactRegistryRow], claims: list[ClaimLedgerRow]) -> dict:
    top_tags: dict[str, int] = {}
    for event in events:
        top_tags[event.tag] = top_tags.get(event.tag, 0) + 1

    return {
        "seat": "S1",
        "seat_name": "GPTBrain / Cognitive Infrastructure / Calibration",
        "packet_status": "generated / review required",
        "created_utc": utc_now(),
        "session_id": label,
        "source_model": source,
        "source_surface": "raw text import",
        "raw_log_ref": str(raw),
        "sha256": sha,
        "privacy_status": privacy,
        "primary_domains": sorted(top_tags, key=top_tags.get, reverse=True)[:12],
        "source_refs": {
            "github_refs": [],
            "drive_refs": [],
            "uploaded_files": [raw.name],
            "user_context_refs": [],
        },
        "artifacts_created": [artifact.artifact_id for artifact in artifacts],
        "extracted_events_count": len(events),
        "claim_count": len(claims),
        "claim_calibration": {
            "strongest_safe_claim": "This raw log has been converted into GPTBrain retrieval aids and review packets.",
            "overclaims_detected": [claim.claim_id for claim in claims if claim.forbidden_wording],
            "missing_evidence": ["human review", "Council workflow", "source-specific validation"],
            "confidence": "C2",
        },
        "s1_assessment": {
            "summary": f"Generated GPTBrain memory packet for {label} from {source} raw text.",
            "evidence_quality": "source artifact exists; parser output requires review",
            "implementation_readiness": "usable as archive/retrieval packet",
            "public_shareability": privacy,
            "canon_status": "parsed",
        },
        "evidence_boundary_notes": EVIDENCE_BOUNDARY,
        "metadata": metadata,
        "next_boot_refs": [],
    }


def build_boot_packet(label: str, source: str, metadata: dict, top_tags: list[tuple[str, int]]) -> str:
    tags_md = "\n".join(f"- `{tag}`: {count}" for tag, count in top_tags[:15]) or "- none"
    return f"""# GPTBrain Boot Packet — {label}

**Status:** generated boot packet / review required / not canon  
**Source:** {source}  
**Created UTC:** {utc_now()}  
**SHA-256:** `{metadata['sha256']}`  
**Size:** {metadata['bytes']:,} bytes / {metadata['characters']:,} characters / {metadata['lines']:,} lines  
**Turns detected:** {metadata['turns_detected']:,}  
**Events detected:** {metadata['events_detected']:,}  

## Boot Command

```text
BOOT GPTBRAIN / S1.

Load this packet as parsed operating memory. Preserve evidence boundaries.
Do not treat parser output as canon.
Summarize current state, open actions, guardrails, and next best move.
```

## Top Tags

{tags_md}

## Evidence Boundary

```text
raw log = evidence
parser output = retrieval aid
model assessment = evaluator signal
hypothesis = unscored claim
candidate canon = review-ready artifact
ratified canon = published through Council workflow
```

## Generated Files

- `metadata.json`
- `turns.jsonl`
- `events.jsonl`
- `artifact_registry.jsonl`
- `claim_ledger.jsonl`
- `memory_packet.json`
- `BOOT_PACKET.md`

## Strongest Safe Claim

This packet makes the raw log easier to retrieve, review, score, and route. It does not validate the claims inside the log by itself.
"""


def run(input_path: Path, label: str, source: str, privacy: str, out_root: Path) -> dict:
    if not input_path.exists():
        raise FileNotFoundError(input_path)

    text = input_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    sha = sha256_file(input_path)

    out = out_root / label
    out.mkdir(parents=True, exist_ok=True)

    turns = split_turns(lines)
    events = extract_events(turns)
    claims = detect_claims(turns, source, sha)
    artifacts = build_artifact_registry(events, label, source, sha, privacy)

    metadata = {
        "label": label,
        "source": source,
        "created_utc": utc_now(),
        "input_filename": input_path.name,
        "sha256": sha,
        "bytes": input_path.stat().st_size,
        "characters": len(text),
        "lines": len(lines),
        "turns_detected": len(turns),
        "events_detected": len(events),
        "artifacts_detected": len(artifacts),
        "claims_detected": len(claims),
        "privacy_status": privacy,
        "status": "parsed / review required / not canon",
        "evidence_boundary": EVIDENCE_BOUNDARY,
    }

    tag_counts: dict[str, int] = {}
    for event in events:
        tag_counts[event.tag] = tag_counts.get(event.tag, 0) + 1
    top_tags = sorted(tag_counts.items(), key=lambda kv: (-kv[1], kv[0]))

    memory_packet = build_memory_packet(label, source, input_path, sha, privacy, metadata, events, artifacts, claims)
    boot_packet = build_boot_packet(label, source, metadata, top_tags)

    (out / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    write_jsonl(out / "turns.jsonl", (asdict(turn) for turn in turns))
    write_jsonl(out / "events.jsonl", (asdict(event) for event in events))
    write_jsonl(out / "artifact_registry.jsonl", (asdict(row) for row in artifacts))
    write_jsonl(out / "claim_ledger.jsonl", (asdict(row) for row in claims))
    (out / "memory_packet.json").write_text(json.dumps(memory_packet, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "BOOT_PACKET.md").write_text(boot_packet, encoding="utf-8")

    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description="GPTBrain / S1 memory palace importer")
    parser.add_argument("input", type=Path, help="Raw text log/transcript")
    parser.add_argument("--label", required=True, help="Session/archive label")
    parser.add_argument("--source", default="GPT", help="Source model/system/user label")
    parser.add_argument("--privacy", default="mixed", choices=["public", "private", "mixed", "redacted"])
    parser.add_argument("--out", type=Path, default=Path("./gptbrain_out"))
    args = parser.parse_args()

    metadata = run(args.input, args.label, args.source, args.privacy, args.out)
    print(json.dumps(metadata, indent=2, ensure_ascii=False))
    print(f"Wrote GPTBrain packet to: {args.out / args.label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
