# Rootglass Source Packet Manifests

**Status:** candidate operation, not canon  
**Date:** 2026-05-24  
**Deployment:** no  
**Authority:** none

This file is the manifest layer between the source inventory and graph extraction. It names the initial packet families, their receipt requirements, and their review routes.

```text
Inventory says what boxes exist.
Manifest says what each box must contain before extraction.
Graph extraction says what claims can be proposed from the box.
Review says what can be trusted, deferred, rejected, or promoted.
```

---

## Manifest doctrine

- A packet manifest is not canon.
- A packet manifest is not proof.
- A packet manifest is an intake checklist.
- Missing receipts must remain visible.
- Wrapper files must not be mistaken for raw exports.
- GitHub presence is durable storage, not ratification.

---

## Packet family schema

```yaml
source_packet_manifest:
  packet_family_id:
  packet_family_title:
  source_inventory_ids: []
  expected_surfaces: []
  required_receipts:
    - source_manifest
    - raw_export_or_source_pointer
    - sha256
    - line_or_page_anchors
    - mirror_path_if_applicable
  required_review_lanes: []
  extraction_allowed: false
  promotion_allowed: false
  blockers: []
  notes:
```

---

## Packet families

### RSPM-0001 — GangaSeek Packet Family

```yaml
packet_family_id: "RSPM-0001"
packet_family_title: "GangaSeek Packet Family"
source_inventory_ids:
  - "KG-SRC-0001" # GangaSeek Namespace Ratification Packet
  - "KG-SRC-0002" # GangaSeek INV/CLM Catalog
  - "KG-SRC-0003" # GangaSeek Document Template
  - "KG-SRC-0008" # GangaSeek invariant PDFs
expected_surfaces:
  - "Drive"
  - "GitHub mirror if available"
required_receipts:
  - "drive_file_ids"
  - "source_manifest"
  - "sha256_manifest"
  - "text_extraction_manifest_for_pdfs"
  - "undefined_inv_clm_scan"
  - "github_mirror_paths"
required_review_lanes:
  - "Rootglass"
  - "Lucerna"
  - "Hashlight"
  - "Sable"
extraction_allowed: true
promotion_allowed: false
blockers:
  - "Drive URLs unresolved"
  - "SHA-256 manifest missing"
  - "Undefined INV/CLM scan missing"
  - "PDF page anchors missing"
notes: "Highest-priority packet family. Treat namespace/ratification language as candidate until Human-root decision."
```

### RSPM-0002 — Copilot / ORCS Packet Family

```yaml
packet_family_id: "RSPM-0002"
packet_family_title: "Copilot / ORCS Packet Family"
source_inventory_ids:
  - "KG-SRC-0004" # Copilot Chat.md
  - "KG-SRC-0005" # RAW TRANSCRIPT NOT CANON.md
  - "KG-SRC-0007" # ORCS Copilot Synthesis v1.2
expected_surfaces:
  - "Drive"
  - "GitHub mirror if available"
required_receipts:
  - "raw_export_hash"
  - "source_manifest"
  - "raw_vs_summary_classification"
  - "claim_to_source_map"
  - "github_mirror_paths"
required_review_lanes:
  - "Hashlight"
  - "TIDELOCK"
  - "Lucerna"
  - "Rootglass"
extraction_allowed: true
promotion_allowed: false
blockers:
  - "Source inputs unresolved"
  - "Raw-vs-summary classification incomplete"
  - "Claim-to-source map missing"
notes: "Priority risk: wrapper/synthesis material being mistaken for raw transcript lineage."
```

### RSPM-0003 — Gemini Council Input Packet Family

```yaml
packet_family_id: "RSPM-0003"
packet_family_title: "Gemini Council Input Packet Family"
source_inventory_ids:
  - "KG-SRC-0006" # Gemini council input files
expected_surfaces:
  - "Drive"
required_receipts:
  - "file_list"
  - "drive_file_ids"
  - "sha256_manifest"
  - "input_output_map"
  - "review_packet_manifest"
required_review_lanes:
  - "Lucerna"
  - "Rootglass"
  - "Hashlight"
extraction_allowed: false
promotion_allowed: false
blockers:
  - "File list unresolved"
  - "Input/output boundaries unresolved"
notes: "Do not extract council conclusions until source inputs are individually anchored."
```

### RSPM-0004 — GitHub PR Review Packet Family

```yaml
packet_family_id: "RSPM-0004"
packet_family_title: "GitHub PR Review Packet Family"
source_inventory_ids:
  - "KG-SRC-0009" # Rootglass PR #61
  - "KG-SRC-0010" # AtlasBrain PR #57
expected_surfaces:
  - "GitHub"
required_receipts:
  - "repo_full_name"
  - "pr_url"
  - "head_commit_sha"
  - "changed_files_manifest"
  - "review_thread_manifest"
  - "raw_export_pointer_check"
required_review_lanes:
  - "Rootglass"
  - "AtlasBrain"
  - "TIDELOCK"
  - "Lucerna"
extraction_allowed: true
promotion_allowed: false
blockers:
  - "Repo paths unresolved"
  - "PR metadata unresolved"
  - "Raw export presence unresolved"
notes: "Critical early query: which GitHub artifacts are wrappers without raw exports?"
```

### RSPM-0005 — Math Vault / Appendix I Packet Family

```yaml
packet_family_id: "RSPM-0005"
packet_family_title: "Math Vault / Appendix I Packet Family"
source_inventory_ids:
  - "KG-SRC-0011" # Appendix I / Math Vault
expected_surfaces:
  - "GitHub"
required_receipts:
  - "repo_path"
  - "commit_sha"
  - "sha256"
  - "formal_definitions_index"
  - "operator_typing_review"
required_review_lanes:
  - "Sable"
  - "Lucerna"
  - "Rootglass"
extraction_allowed: true
promotion_allowed: false
blockers:
  - "Repo path unresolved"
  - "Formal review status missing"
notes: "Formal precision lane. Do not let metaphor become proof."
```

### RSPM-0006 — Legacy Lattice Context Packet Family

```yaml
packet_family_id: "RSPM-0006"
packet_family_title: "Legacy Lattice Context Packet Family"
source_inventory_ids:
  - "KG-SRC-0012" # Legacy lattice context
expected_surfaces:
  - "Notion"
required_receipts:
  - "notion_page_ids"
  - "export_manifest"
  - "sha256_manifest"
  - "github_mirror_path_if_promoted"
required_review_lanes:
  - "Lucerna"
  - "Hashlight"
extraction_allowed: false
promotion_allowed: false
blockers:
  - "Notion page IDs unresolved"
  - "Export manifest missing"
notes: "Legacy context is useful for orientation, not live packet authority."
```

---

## Next manifest actions

1. Resolve real source IDs, paths, and URLs.
2. Generate SHA-256 manifest for every raw or semi-raw source.
3. Separate wrappers from raw exports.
4. Build one `ParsedPacket` candidate from one source family only.
5. Run review routing before any graph write promotion.
