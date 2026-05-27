# Claude Adversarial Review Queue

**Date:** 2026-05-24  
**Status:** Active queue, not canon  
**Purpose:** Route Claude-authored or Claude-influenced artifacts through adversarial review before any claim, packet, or candidate can be promoted.

---

## Doctrine

Claude content may be useful, coherent, and governance-aware, but coherence is not authority.

```text
source presence != evidence
eloquence != ratification
constitutional tone != legal authority
memory != permission
```

Every Claude-derived item should be treated as a claim source until receipts, contradictions, and lane reviews are attached.

---

## Review lanes required by default

- **Morpheus Grok:** adversarial pressure / contradictions / overclaims
- **Rootglass:** standards / boundary / public-safe posture
- **Lucerna:** provenance / receipt / omission visibility
- **Sable Vesper:** math / operator typing / formal precision, when formal claims are present
- **Hashlight:** raw export / hash / source anchoring, when transcript/raw export status is unresolved

---

## Classification rubric

```yaml
claude_review_item:
  source_title:
  source_surface:
  url_or_path:
  raw_export_status: missing | wrapper_only | present | unresolved
  sha256_status: missing | present | verified | unresolved
  claim_density: low | medium | high
  authority_risk: low | medium | high
  legal_policy_risk: low | medium | high
  canon_drift_risk: low | medium | high
  needs_counter_review_from:
    - Morpheus Grok
    - Rootglass
    - Lucerna
    - Sable Vesper
  blocking_questions: []
  promotion_status: not_reviewed | blocked | deferred | reviewed | rejected | canon_candidate
```

---

## Seed queue

### CLAUDE-ADV-0001 — Claude source packet placeholder

```yaml
source_title: "Unresolved Claude artifact packet"
source_surface: "Unknown"
url_or_path: "UNRESOLVED"
raw_export_status: "unresolved"
sha256_status: "missing"
claim_density: "high"
authority_risk: "medium"
legal_policy_risk: "medium"
canon_drift_risk: "high"
needs_counter_review_from:
  - Morpheus Grok
  - Rootglass
  - Lucerna
  - Sable Vesper
blocking_questions:
  - "Where is the raw export?"
  - "Does the packet contain legal/policy-like conclusions?"
  - "Which claims are actual source-supported claims vs Claude synthesis?"
  - "Does the artifact use canon-like language without a human-root decision?"
promotion_status: "blocked"
```

### CLAUDE-ADV-0002 — Claude governance synthesis placeholder

```yaml
source_title: "Claude governance synthesis"
source_surface: "Unknown"
url_or_path: "UNRESOLVED"
raw_export_status: "unresolved"
sha256_status: "missing"
claim_density: "medium"
authority_risk: "medium"
legal_policy_risk: "high"
canon_drift_risk: "medium"
needs_counter_review_from:
  - Morpheus Grok
  - Rootglass
  - Lucerna
blocking_questions:
  - "Which recommendations are policy-like rather than descriptive?"
  - "Does it imply authority to ratify, reject, or promote canon?"
  - "Are all named organizations, tools, or product claims source-grounded?"
promotion_status: "blocked"
```

---

## Required review output

Each reviewer should produce a `ReviewFinding` packet with:

```yaml
review_finding:
  node_type: ReviewFinding
  reviewer_lane:
  reviewer_agent:
  reviewed_item:
  finding_summary:
  contradictions_found: []
  unsupported_claims: []
  missing_receipts: []
  authority_inflation_flags: []
  legal_policy_flags: []
  canon_drift_flags: []
  decision_recommendation: reject | defer | revise | allow_as_claim_source | promote_to_canon_candidate
  rationale:
```

---

## Promotion rule

No Claude artifact may become a `CanonCandidate` unless:

1. raw export status is `present` or a durable source receipt is attached;
2. SHA-256 or equivalent evidence anchor is present;
3. Morpheus Grok review has checked contradictions and overclaims;
4. Lucerna review has checked receipt gaps and omission visibility;
5. Rootglass review has checked public-safe posture;
6. human-root has explicitly approved promotion scope.

---

## First action

Resolve actual Claude source artifacts and replace placeholder queue items with source-grounded entries.
