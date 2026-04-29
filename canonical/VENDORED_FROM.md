# Vendored Canonical Ontology Files

These files are vendored snapshots from the `aluminum-os` monorepo.
They provide the canonical 12×12+1 lattice ontology that replaces the
legacy grokbrain_v4 academic-category ontology.

## Source

| File | Source Repo | Source Path |
|------|-------------|-------------|
| `lattice_ontology_v2.py` | `atlaslattice/aluminum-os` | `element-145/aluminum-os-core/lattice_ontology_v2.py` |
| `sphere_classifier_v2.py` | `atlaslattice/aluminum-os` | `element-145/aluminum-os-core/sphere_classifier_v2.py` |
| `lattice_ontology.yaml` | `atlaslattice/aluminum-os` | `registries/lattice_ontology.yaml` |

## Source Commit

- **Repo:** `atlaslattice/aluminum-os`
- **Branch:** `main`
- **Date:** 2026-04-29

## Migration Path

These vendored files are a temporary measure. The long-term plan is:

1. Publish `element145` to PyPI as a proper Python package
2. Replace this `canonical/` directory with a `pip install element145` dependency
3. Import from `element145.core` instead of `canonical.lattice_ontology_v2`

## Governance

Changes to these files MUST be synchronized with the upstream `aluminum-os` repo.
The ontology-lock CI gate (SHA-256 hash comparison) ensures drift is detected.
Do NOT modify these files directly — update upstream and re-vendor.
