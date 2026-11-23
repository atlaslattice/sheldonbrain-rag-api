"""Offline, metadata-only corpus pilot gate (candidate; never an ingest grant).

No network, embedding, storage, source-body reads, or rights authentication.
Failures expose record positions and error *codes*, never field values.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

EDITION = "0.1.0"
LIMIT = 100
MAX_MANIFEST_BYTES = 1_048_576
OPAQUE = re.compile(r"^[A-Za-z0-9._:/-]{1,180}$")
COORD = re.compile(r"^H(?:0[1-9]|1[0-2])\.S(?:0[1-9]|1[0-2])\.N(?:0[1-9]|1[0-2])$")
FIELDS = frozenset({
    "artifact_id", "revision_id", "source_revision", "source_locator",
    "source_mode", "source_kind", "visibility", "rights_status",
    "rights_evidence_ref", "allowed_purposes", "raw_export_status",
    "retention_policy", "taxonomy_edition", "house_scores", "node_scores",
})
REQUIRED = FIELDS - {"taxonomy_edition", "house_scores", "node_scores"}


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("DUPLICATE_JSON_KEY")
        value[key] = item
    return value


def _reject_constant(_: str) -> None:
    raise ValueError("NON_FINITE_NUMBER")


def _opaque(value: Any) -> bool:
    return isinstance(value, str) and OPAQUE.fullmatch(value) is not None


def _safe_source_locator(value: Any) -> bool:
    """No source is fetched, but do not pass path-traversal segments onward."""
    return _opaque(value) and all(part not in {".", ".."} for part in value.replace(":", "/").split("/"))


def _score(value: Any) -> bool:
    return type(value) in (float, int) and 0 <= value <= 1 and math.isfinite(value)


def validate_manifest(raw: bytes) -> dict[str, Any]:
    """Review format only. No record or source value appears in the receipt."""
    errors: list[dict[str, Any]] = []
    def flag(code: str, index: int | None = None) -> None:
        errors.append({"index": index, "code": code})

    if len(raw) > MAX_MANIFEST_BYTES:
        flag("MANIFEST_BYTES_EXCEEDED")
        data = None
    else:
        try:
            data = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_pairs,
                              parse_constant=_reject_constant)
        except (UnicodeError, ValueError, TypeError, RecursionError, OverflowError):
            flag("INVALID_JSON_OR_DUPLICATE_KEY")
            data = None
    records: list[Any] = []
    if data is not None:
        if not isinstance(data, dict) or set(data) != {"schema_version", "records"} or data.get("schema_version") != EDITION:
            flag("ROOT_SCHEMA")
        elif not isinstance(data["records"], list):
            flag("RECORDS_NOT_ARRAY")
        else:
            records = data["records"]
            if len(records) > LIMIT:
                flag("PILOT_LIMIT_EXCEEDED")

    seen: set[tuple[str, str]] = set()
    for index, record in enumerate(records[:LIMIT]):
        if not isinstance(record, dict):
            flag("RECORD_NOT_OBJECT", index)
            continue
        if set(record) - FIELDS:
            flag("UNRECOGNIZED_OR_BODY_FIELD", index)
        if REQUIRED - set(record):
            flag("REQUIRED_METADATA_MISSING", index)
        if any(not _opaque(record.get(k)) for k in (
            "artifact_id", "revision_id", "source_revision", "source_locator",
            "rights_evidence_ref", "retention_policy"
        )):
            flag("INVALID_OPAQUE_REFERENCE", index)
        # A syntactically opaque locator can still contain ../ path traversal.
        # Keep source content out of receipts, even when rejecting a locator.
        if _opaque(record.get("source_locator")) and not _safe_source_locator(record["source_locator"]):
            flag("UNSAFE_SOURCE_LOCATOR", index)
        pair = (record.get("artifact_id"), record.get("revision_id"))
        if all(isinstance(v, str) for v in pair):
            if pair in seen:
                flag("DUPLICATE_ARTIFACT_REVISION", index)
            seen.add(pair)
        if record.get("source_mode") != "work":
            flag("NON_WORK_SOURCE_MODE", index)
        kind = record.get("source_kind")
        if not isinstance(kind, str) or kind not in {"repository", "drive", "notion", "web", "synthetic", "other"}:
            flag("INVALID_SOURCE_KIND", index)
        visibility = record.get("visibility")
        if not isinstance(visibility, str) or visibility not in {"public", "consented_work", "synthetic"}:
            flag("VISIBILITY_HOLD", index)
        if record.get("rights_status") != "rights_reviewed":
            flag("RIGHTS_REVIEW_HOLD", index)
        if record.get("allowed_purposes") != ["metadata_census"]:
            flag("PURPOSE_HOLD", index)
        if record.get("raw_export_status") != "not_fetched":
            flag("BODY_FETCH_OUT_OF_SCOPE", index)
        edition = record.get("taxonomy_edition")
        houses = record.get("house_scores")
        nodes = record.get("node_scores")
        # Even when scores are absent, a supplied edition must be an opaque
        # reference, not an unchecked body-bearing object or arbitrary value.
        if "taxonomy_edition" in record and not _opaque(edition):
            flag("INVALID_TAXONOMY_EDITION", index)
        # A present null vector is malformed, not equivalent to absent data.
        if ("house_scores" in record or "node_scores" in record) and "taxonomy_edition" not in record:
            flag("TAXONOMY_EDITION_MISSING", index)
        if "house_scores" in record and (not isinstance(houses, list) or len(houses) != 12 or not all(_score(s) for s in houses)):
            flag("INVALID_HOUSE_VECTOR", index)
        if "node_scores" in record and (
            not isinstance(nodes, dict) or len(nodes) > 1728 or
            any(not isinstance(k, str) or not COORD.fullmatch(k) or not _score(s) for k, s in nodes.items())
        ):
            flag("INVALID_NODE_VECTOR", index)

    return {
        "disposition": "HOLD" if errors else "REVIEWABLE_CANDIDATE",
        "schema_version": EDITION,
        "records_seen": len(records),
        "records_read_from_sources": 0,
        "records_indexed": 0,
        "can_ingest": False,
        "rights_authenticated": False,
        "canon": False,
        "deployed": False,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Review a local metadata-only manifest without ingesting any source")
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    verdict = validate_manifest(args.manifest.read_bytes())
    print(json.dumps(verdict, sort_keys=True))
    return 0 if verdict["disposition"] == "REVIEWABLE_CANDIDATE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
