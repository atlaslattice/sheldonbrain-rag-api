# Rootglass Source Packet Manifests

**Status:** draft, not canon  
**Authority:** none  
**Purpose:** Define receipt-first source packet manifests for Copilot, Gemini, GangaSeek, and model-originated materials.

## Doctrine

```text
A manifest is a clipboard.
A clipboard is not canon.
A source packet needs receipts before claims.
```

## Standard source packet manifest

```yaml
source_packet_manifest:
  packet_id:
  packet_title:
  packet_family: Copilot / Gemini / GangaSeek / ModelOutput / ORCS / Other
  source_inventory_ids: []
  raw_exports: []
  parsed_packets: []
  evidence_anchors: []
  review_lanes_required: []
  review_lanes_complete: []
  missing_receipts: []
  promotion_status: draft / blocked / review_pending / candidate / rejected / ratified
  notes:
```

## Manifest: Copilot

```yaml
source_packet_manifest:
  packet_id: ROOTGLASS-MANIFEST-COPILOT-0001
  packet_title: "Copilot Source Packet Manifest"
  packet_family: "Copilot"
  source_inventory_ids:
    - KG-SRC-0004
  raw_exports: []
  parsed_packets: []
  evidence_anchors: []
  review_lanes_required:
    - Hashlight
    - Lucerna
    - TIDELOCK
    - Rootglass
  review_lanes_complete: []
  missing_receipts:
    - raw_export_hash
    - source_manifest
    - github_mirror_path
  promotion_status: blocked
  notes: "Resolve raw-vs-summary state before claim extraction."
```

## Manifest: Gemini

```yaml
source_packet_manifest:
  packet_id: ROOTGLASS-MANIFEST-GEMINI-0001
  packet_title: "Gemini Council Input Manifest"
  packet_family: "Gemini"
  source_inventory_ids:
    - KG-SRC-0006
  raw_exports: []
  parsed_packets: []
  evidence_anchors: []
  review_lanes_required:
    - Lucerna
    - Hashlight
    - Rootglass
  review_lanes_complete: []
  missing_receipts:
    - file_list
    - drive_file_ids
    - sha256_manifest
    - github_mirror_path
  promotion_status: blocked
  notes: "Treat as council input until per-file anchors are attached."
```

## Manifest: GangaSeek

```yaml
source_packet_manifest:
  packet_id: ROOTGLASS-MANIFEST-GANGASEEK-0001
  packet_title: "GangaSeek Namespace / Template / Catalog Manifest"
  packet_family: "GangaSeek"
  source_inventory_ids:
    - KG-SRC-0001
    - KG-SRC-0002
    - KG-SRC-0003
    - KG-SRC-0008
  raw_exports: []
  parsed_packets: []
  evidence_anchors: []
  review_lanes_required:
    - Rootglass
    - Lucerna
    - Hashlight
    - Sable_Vesper
  review_lanes_complete: []
  missing_receipts:
    - drive_file_ids
    - sha256_manifest
    - github_mirror_paths
    - undefined_inv_clm_scan
    - ratification_decision
  promotion_status: blocked
  notes: "Priority family for first graph queries: undefined INV/CLM IDs, non-canon status, source manifest gaps."
```

## Manifest: ORCS / Copilot synthesis

```yaml
source_packet_manifest:
  packet_id: ROOTGLASS-MANIFEST-ORCS-0001
  packet_title: "ORCS Copilot Synthesis Manifest"
  packet_family: "ORCS"
  source_inventory_ids:
    - KG-SRC-0007
  raw_exports: []
  parsed_packets: []
  evidence_anchors: []
  review_lanes_required:
    - TIDELOCK
    - Lucerna
    - Rootglass
  review_lanes_complete: []
  missing_receipts:
    - drive_file_id
    - sha256
    - source_inputs
    - github_mirror_path
  promotion_status: blocked
  notes: "Synthesis must cite source inputs before graph claims become usable."
```

## Manifest: Appendix I / Math Vault

```yaml
source_packet_manifest:
  packet_id: ROOTGLASS-MANIFEST-MATHVAULT-0001
  packet_title: "Appendix I / Math Vault Manifest"
  packet_family: "MathVault"
  source_inventory_ids:
    - KG-SRC-0011
  raw_exports: []
  parsed_packets: []
  evidence_anchors: []
  review_lanes_required:
    - Sable_Vesper
    - Lucerna
    - Rootglass
  review_lanes_complete: []
  missing_receipts:
    - repo_path
    - commit_sha
    - sha256
    - formal_review_status
  promotion_status: blocked
  notes: "Formal precision lane. No promotion without operator/type review."
```
