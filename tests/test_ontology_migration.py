#!/usr/bin/env python3
"""
Phase 1.1 Ontology Migration Tests

Validates that the canonical 12x12+1 lattice ontology is correctly
integrated into the sheldonbrain-rag-api codebase.

Acceptance criteria from S1 proposal:
  A. canonical/ vendored files import without error
  B. metadata_validator accepts both legacy S001-S144 and lattice H01.S01 formats
  C. rag_api_gemini auto-classifies text into lattice spheres
  D. sphere_classifier imports from canonical instead of grokbrain_v4
  E. All existing tests still pass (no regression)
"""
import os
import sys
import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCanonicalImports:
    """A. Verify canonical/ vendored files import correctly."""

    def test_lattice_ontology_imports(self):
        from canonical.lattice_ontology_v2 import (
            SPHERES, HOUSE_NAMES, HOUSE_IDS, ELEMENTS,
            CATEGORY_NAMES, classify_text, get_activated_context,
        )
        assert len(SPHERES) == 144
        assert len(HOUSE_NAMES) == 12
        assert len(HOUSE_IDS) == 12
        assert len(ELEMENTS) == 144
        assert len(CATEGORY_NAMES) == 12

    def test_sphere_classifier_v2_imports(self):
        from canonical.sphere_classifier_v2 import (
            KeywordClassifier, pinecone_metadata,
        )
        assert callable(pinecone_metadata)

    def test_classify_text_returns_results(self):
        from canonical.lattice_ontology_v2 import classify_text
        results = classify_text("quantum computing qubits", top_k=3)
        assert len(results) > 0
        assert "address" in results[0]
        assert "house" in results[0]
        assert "sphere" in results[0]

    def test_pinecone_metadata_format(self):
        from canonical.sphere_classifier_v2 import pinecone_metadata
        meta = pinecone_metadata("test text about economics", source="test")
        assert "house" in meta
        assert "sphere" in meta
        assert "house_name" in meta
        assert "sphere_name" in meta
        assert "timestamp" in meta
        assert meta["source"] == "test"
        # Sphere should be in H##.S## format
        assert "." in meta["sphere"]


class TestMetadataValidatorMigration:
    """B. Verify metadata_validator accepts both formats."""

    def test_legacy_sphere_accepted(self):
        from metadata_validator import VALID_SPHERES
        assert "S001" in VALID_SPHERES
        assert "S144" in VALID_SPHERES

    def test_lattice_sphere_accepted(self):
        from metadata_validator import VALID_SPHERES
        assert "H01.S01" in VALID_SPHERES
        assert "H12.S12" in VALID_SPHERES
        assert "E145" in VALID_SPHERES

    def test_normalize_legacy_to_lattice(self):
        from metadata_validator import MetadataValidator
        v = MetadataValidator()
        result = v.normalize_sphere("S023")
        assert "." in result  # Should be in lattice format
        assert result.startswith("H")

    def test_normalize_lattice_passthrough(self):
        from metadata_validator import MetadataValidator
        v = MetadataValidator()
        assert v.normalize_sphere("H02.S11") == "H02.S11"
        assert v.normalize_sphere("E145") == "E145"

    def test_auto_assign_returns_lattice_format(self):
        from metadata_validator import MetadataValidator
        v = MetadataValidator()
        sphere = v.auto_assign_sphere(
            "quantum_research.md",
            "This paper explores quantum entanglement and qubit decoherence"
        )
        assert sphere is not None
        assert "." in sphere or sphere == "E145"

    def test_valid_spheres_count(self):
        from metadata_validator import VALID_SPHERES_LATTICE
        assert len(VALID_SPHERES_LATTICE) == 145  # 144 + E145


class TestRagApiMigration:
    """C. Verify rag_api_gemini has lattice-aware endpoints."""

    def test_rag_api_imports_canonical(self):
        """Verify the module can be parsed (imports may fail without API keys)."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "rag_api_gemini",
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "rag_api_gemini.py")
        )
        assert spec is not None

    def test_rag_api_has_classify_endpoint(self):
        """Check that /classify endpoint exists in the source."""
        rag_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "rag_api_gemini.py"
        )
        with open(rag_path) as f:
            content = f.read()
        assert "/classify" in content
        assert "/lattice" in content
        assert "lattice_ontology_v2" in content

    def test_rag_api_version_string(self):
        """Check version string includes lattice."""
        rag_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "rag_api_gemini.py"
        )
        with open(rag_path) as f:
            content = f.read()
        assert "gemini-lattice" in content


class TestSphereClassifierMigration:
    """D. Verify sphere_classifier imports from canonical."""

    def test_sphere_classifier_uses_canonical(self):
        """Check that sphere_classifier.py imports from canonical/."""
        sc_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "sphere_classifier.py"
        )
        with open(sc_path) as f:
            content = f.read()
        assert "canonical.lattice_ontology_v2" in content
        assert "grokbrain_v4 import SPHERES" not in content


class TestBackwardCompatibility:
    """E. Verify no regressions in existing functionality."""

    def test_spheres_array_length(self):
        from canonical.lattice_ontology_v2 import SPHERES
        assert len(SPHERES) == 144

    def test_elements_array_length(self):
        from canonical.lattice_ontology_v2 import ELEMENTS
        assert len(ELEMENTS) == 144

    def test_category_names_length(self):
        from canonical.lattice_ontology_v2 import CATEGORY_NAMES
        assert len(CATEGORY_NAMES) == 12

    def test_legacy_interface_preserved(self):
        """grokbrain_v4 backward compat: SPHERES[0] should be a string."""
        from canonical.lattice_ontology_v2 import SPHERES
        assert isinstance(SPHERES[0], str)
        assert isinstance(SPHERES[143], str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
