#!/usr/bin/env python3
"""
Metadata Validator for RAG Ingestion Pipeline -- Lattice-Aware v2.0

Phase 1.1 Migration: Validates and enriches file metadata using the
canonical 12x12+1 lattice ontology instead of hardcoded S001-S144 codes.

Changes from v1.0:
  - VALID_SPHERES now generated from canonical ontology (H01.S01 format)
  - SPHERE_KEYWORDS replaced by canonical keyword tables
  - auto_assign_sphere() uses lattice classify_text()
  - Backward-compatible: still accepts legacy S001-S144 codes and maps them
"""
import os
import re
import yaml
import sys
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path

# Add project root to path for canonical imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from canonical.lattice_ontology_v2 import (
    SPHERES, HOUSE_NAMES, HOUSE_IDS,
    classify_text,
)

# Generate valid sphere addresses from canonical ontology
VALID_SPHERES_LATTICE = []
for h_idx, house_id in enumerate(HOUSE_IDS):
    for s_idx in range(12):
        VALID_SPHERES_LATTICE.append(f"{house_id}.S{s_idx+1:02d}")
VALID_SPHERES_LATTICE.append("E145")

# Legacy S001-S144 codes for backward compatibility
VALID_SPHERES_LEGACY = [f"S{i:03d}" for i in range(1, 145)]

# Combined: accept both formats
VALID_SPHERES = set(VALID_SPHERES_LATTICE + VALID_SPHERES_LEGACY)

# Legacy to Lattice mapping
LEGACY_TO_LATTICE = {}
for i in range(144):
    legacy = f"S{i+1:03d}"
    _h = i // 12
    _s = i % 12
    lattice = f"{HOUSE_IDS[_h]}.S{_s+1:02d}"
    LEGACY_TO_LATTICE[legacy] = lattice


class MetadataValidator:
    """Validates and enriches file metadata for RAG ingestion.
    Phase 1.1: Uses canonical 12x12+1 lattice ontology."""

    def __init__(self):
        self.required_fields = ["source", "sphere", "novelty", "category", "timestamp"]
        self.optional_fields = ["file_path", "word_count", "tags", "references",
                                "house", "house_name", "sphere_name"]

    def extract_frontmatter(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    return yaml.safe_load(parts[1].strip()) or {}
            return {}
        except Exception as e:
            print(f"Warning: Could not extract frontmatter from {file_path}: {e}")
            return {}

    def normalize_sphere(self, sphere):
        """Normalize sphere identifier to lattice format.
        Accepts H02.S11 (returned as-is), S023 (mapped), E145 (as-is)."""
        if sphere in VALID_SPHERES_LATTICE:
            return sphere
        if sphere in LEGACY_TO_LATTICE:
            return LEGACY_TO_LATTICE[sphere]
        return sphere

    def auto_assign_sphere(self, file_path, content):
        """Auto-assign sphere using canonical lattice classifier."""
        filename = Path(file_path).stem.replace('_', ' ').replace('-', ' ')
        classify_input = f"{filename} {content[:2000]}"
        results = classify_text(classify_input, top_k=1)
        if results:
            best = results[0]
            # classify_text returns address directly
            return best["address"]
        return "E145"

    def count_words(self, content):
        text = re.sub(r'[#*`\[\]()]', '', content)
        return len(text.split())

    def validate_metadata(self, file_path, auto_enrich=True):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise ValueError(f"Could not read file {file_path}: {e}")

        metadata = self.extract_frontmatter(file_path)

        if auto_enrich:
            if "source" not in metadata:
                metadata["source"] = "sheldonbrain_os"

            if "sphere" not in metadata:
                auto_sphere = self.auto_assign_sphere(file_path, content)
                metadata["sphere"] = auto_sphere if auto_sphere else "E145"
            else:
                metadata["sphere"] = self.normalize_sphere(metadata["sphere"])

            # Enrich with house info if sphere is in lattice format
            sphere = metadata["sphere"]
            if "." in sphere:
                parts = sphere.split(".")
                house_id = parts[0]
                metadata["house"] = house_id
                h_idx = HOUSE_IDS.index(house_id) if house_id in HOUSE_IDS else -1
                if h_idx >= 0:
                    metadata["house_name"] = HOUSE_NAMES[h_idx]
                    s_num = int(parts[1][1:]) - 1
                    sphere_idx = h_idx * 12 + s_num
                    if 0 <= sphere_idx < 144:
                        metadata["sphere_name"] = SPHERES[sphere_idx]

            if "novelty" not in metadata:
                wc = self.count_words(content)
                if wc > 5000:
                    metadata["novelty"] = 0.85
                elif wc > 2000:
                    metadata["novelty"] = 0.75
                elif wc > 500:
                    metadata["novelty"] = 0.65
                else:
                    metadata["novelty"] = 0.50

            if "category" not in metadata:
                fn = Path(file_path).stem.lower()
                if "phd" in fn or "research" in fn:
                    metadata["category"] = "Research"
                elif "guide" in fn or "tutorial" in fn:
                    metadata["category"] = "Documentation"
                elif "manifesto" in fn or "theory" in fn:
                    metadata["category"] = "Theory"
                else:
                    metadata["category"] = "General"

            if "timestamp" not in metadata:
                metadata["timestamp"] = datetime.utcnow().isoformat()
            metadata["file_path"] = file_path
            metadata["word_count"] = self.count_words(content)

        missing = [f for f in self.required_fields if f not in metadata]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        if metadata["sphere"] not in VALID_SPHERES:
            raise ValueError(f"Invalid sphere: {metadata['sphere']}")

        try:
            novelty = float(metadata["novelty"])
            if not 0.0 <= novelty <= 1.0:
                raise ValueError(f"Novelty must be 0.0-1.0, got {novelty}")
            metadata["novelty"] = novelty
        except (ValueError, TypeError):
            raise ValueError(f"Invalid novelty: {metadata.get('novelty')}")

        return metadata

    def validate_batch(self, file_paths, auto_enrich=True):
        valid, invalid = [], []
        for fp in file_paths:
            try:
                valid.append((fp, self.validate_metadata(fp, auto_enrich)))
            except Exception as e:
                invalid.append((fp, str(e)))

        houses, spheres, categories, total_words = {}, {}, {}, 0
        for _, m in valid:
            h = m.get("house", "Unknown")
            s = m.get("sphere", "Unknown")
            c = m.get("category", "Unknown")
            w = m.get("word_count", 0)
            houses[h] = houses.get(h, 0) + 1
            spheres[s] = spheres.get(s, 0) + 1
            categories[c] = categories.get(c, 0) + 1
            total_words += w

        return {
            "valid": valid, "invalid": invalid,
            "stats": {
                "total_files": len(file_paths),
                "valid_files": len(valid), "invalid_files": len(invalid),
                "success_rate": len(valid) / len(file_paths) if file_paths else 0,
                "total_words": total_words,
                "avg_words_per_file": total_words / len(valid) if valid else 0,
                "houses": houses, "spheres": spheres, "categories": categories,
                "ontology_version": "12x12+1-v2.0"
            }
        }


def main():
    import sys as _sys
    if len(_sys.argv) < 2:
        print("Running self-test...")
        v = MetadataValidator()
        assert v.normalize_sphere("H02.S11") == "H02.S11"
        assert v.normalize_sphere("E145") == "E145"
        legacy = v.normalize_sphere("S023")
        assert "." in legacy, f"Legacy S023 should map to lattice, got {legacy}"
        print(f"  S023 -> {legacy}")
        sphere = v.auto_assign_sphere("quantum_computing.md", "quantum entanglement qubits")
        print(f"  quantum_computing -> {sphere}")
        assert "H01.S01" in VALID_SPHERES
        assert "E145" in VALID_SPHERES
        assert "S001" in VALID_SPHERES
        assert len(VALID_SPHERES_LATTICE) == 145
        print("  All self-tests PASSED")
        return
    v = MetadataValidator()
    for fp in _sys.argv[1:]:
        try:
            m = v.validate_metadata(fp)
            print(f"OK {fp}: {m.get('sphere')} ({m.get('sphere_name', '')})")
        except Exception as e:
            print(f"FAIL {fp}: {e}")

if __name__ == "__main__":
    main()
