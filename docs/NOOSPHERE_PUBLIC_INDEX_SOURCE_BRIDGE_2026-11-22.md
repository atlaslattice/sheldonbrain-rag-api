# Sheldonbrain ↔ Noosphere public source bridge (2026-11-22)

**PUBLIC METADATA POINTER · CANDIDATE · NO HOST OR PERMISSION GRANT · NOT CANON**

This document adds a **discoverable outbound source pointer**, not a live connection between Sheldonbrain RAG storage and Noosphere. The current Noosphere registry holds 272 public repository metadata rows in a dated source cut, while all unreviewed HSN and cross-repo semantic links remain empty.

## Grounded public source addresses

- [Noosphere public registry](https://github.com/atlaslattice/noosphere-archive/blob/main/registry/public_repo_inventory_2026-11-22.json) — observed public repository URL/ID/default branch, **not** a data-access token
- [Noosphere strict public registry reader](https://github.com/atlaslattice/noosphere-archive/blob/main/registry/public_registry.py) — offline source-only validation and exact public lookup
- [Noosphere public safety and source passport](https://github.com/atlaslattice/noosphere-archive/blob/main/registry/README.md) — review gates for privacy, schema and provenance
- [Noosphere digital continuity v0 spec](https://github.com/atlaslattice/noosphere-archive/blob/main/specs/digital-continuity-protocol-v0.md) — an offline *synthetic* archive/rehydration contract, **not** a live Sheldonbrain memory migration or person/agent identity proof
- [Noosphere public safety disclaimer](https://github.com/atlaslattice/noosphere-archive/blob/main/docs/public-safety-disclaimer.md)

The registry's frozen source Git blob is `8c03e455a45971f3be8782095c748f64416dc114`, and its parser was strengthened against duplicate-key ambiguity in [PR #30](https://github.com/atlaslattice/noosphere-archive/pull/30). This link gives neither Sheldonbrain nor Noosphere the right to query private data.

## Explicit interoperability contract (NOT YET IMPLEMENTED)

Any future read of Sheldonbrain's RAG data or transfer of a memory bundle into a Noosphere/Atlas graph requires:
1. independently authenticated host principal plus owner/affected-party consent, at **READ and RETURN**;
2. precise record-level source scope, version, privacy classification, retention/deletion controls and revocation epoch;
3. typed source + claim + supporting evidence + dissent + method/edition passport (Ariadne v0.7 vs legacy 00–11 remain distinct);
4. provider-specific rights, storage boundaries, current served Site/commit and rollback verification;
5. actual test receipts, independent security review and explicit human-root approval for irreversible changes.

The previous repository's README may describe production status or embeddings, but **this document does not independently verify operational deployments, vector coverage, provider connectivity, real-time sync or authenticated identity.**

**Invariant: `memory != permission`. Links are provenance navigation, not runtime control.** No data is copied, no API is called, no secret is handled, and no scheduled jobs or agents are added.
