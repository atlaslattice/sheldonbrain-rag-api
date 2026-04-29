# DEPRECATED — grokbrain_parser/

**Status:** Legacy. Superseded by `canonical/` as of Phase 1.1 ontology migration.

**Do not modify these files.** They are preserved for reference and backward
compatibility only. All new development should import from `canonical/`.

## Migration Path

| Old (grokbrain_parser/) | New (canonical/) |
|-------------------------|------------------|
| `grokbrain_v4.py` SPHERES, CATEGORY_NAMES, ELEMENTS | `lattice_ontology_v2.py` SPHERES, HOUSE_NAMES, HOUSE_IDS |
| `grokbrain_core.py` processing functions | `lattice_ontology_v2.py` classify_text() |
| `app.py` Streamlit dashboard | Lattice API endpoints in rag_api_gemini.py |
| `test_suite.py` | `tests/test_ontology_migration.py` |
| `xai_integration.py` | Phase 2 migration target |

## Removal Timeline

This directory will be removed after Phase 2 confirms no production dependencies
remain. Target: v3.14 Phase 2 sprint.
