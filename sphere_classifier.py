#!/usr/bin/env python3
"""
Sphere Classifier for RAG Ingestion Pipeline — Lattice-Aware v2.0

Automatically classifies text content into the 12×12+1 lattice ontological
framework using vector similarity search. Integrates canonical lattice logic
with the Sheldonbrain RAG system.

Phase 1.1 Migration:
  - All outputs now include lattice addresses (H01.S01 format) as primary IDs
  - Legacy S001-S144 codes preserved in output as `legacy_id` for backward compat
  - House/sphere names from canonical ontology
  - Category-specific context uses 12 Houses instead of 12 academic categories

Based on: canonical lattice ontology (12×12+1)
Adapted for: Sheldonbrain Multi-AI Persistent Memory System
"""

import os
import sys
from typing import Dict, List, Optional
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import numpy as np

# Import canonical 12×12+1 lattice ontology
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from canonical.lattice_ontology_v2 import (
    SPHERES, HOUSE_NAMES, HOUSE_IDS, KEYWORDS,
    address_for_index, house_for_sphere,
)


# ============================================================================
# HOUSE CONTEXT DESCRIPTIONS (replaces old category-specific context)
# ============================================================================

HOUSE_CONTEXT = {
    0: "This involves scientific inquiry, empirical observation, and understanding of natural phenomena including physics, chemistry, biology, and earth sciences.",
    1: "This involves engineering design, technological innovation, computing systems, and the application of scientific principles to build solutions.",
    2: "This involves the study of human health, medical practice, clinical research, and healthcare systems.",
    3: "This involves the study of human behavior, society, economics, and social institutions.",
    4: "This involves creative expression, aesthetic practice, cultural production, and artistic innovation across media.",
    5: "This involves governance, legal systems, political structures, and the administration of public affairs.",
    6: "This involves the study of belief systems, philosophical inquiry, spiritual practices, and ethical reasoning.",
    7: "This involves the theory and practice of teaching, learning, educational systems, and knowledge transmission.",
    8: "This involves environmental stewardship, ecological science, sustainability, and the relationship between human systems and natural ecosystems.",
    9: "This involves the study of commerce, markets, economic systems, and business strategy.",
    10: "This involves communication systems, media production, information technology, and digital culture.",
    11: "This involves interdisciplinary integration, systems thinking, and cross-domain synthesis.",
}


# ============================================================================
# SPHERE CLASSIFIER
# ============================================================================

class SphereClassifier:
    """
    Classifies text into 12×12+1 lattice ontological framework using
    vector similarity.

    Uses HuggingFace embeddings and cosine similarity to match content
    against sphere descriptions, returning the best match with confidence
    score and lattice address.
    """

    def __init__(self, embedding_model=None):
        """
        Initialize sphere classifier with embedding model.

        Args:
            embedding_model: Optional pre-initialized embedding model.
                           Defaults to sentence-transformers/all-MiniLM-L6-v2
        """
        if embedding_model is None:
            print("Loading embedding model...")
            self.embedding_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        else:
            self.embedding_model = embedding_model

        # Generate sphere descriptions
        print("Generating 144-sphere reference descriptions...")
        self.sphere_descriptions = self._generate_sphere_descriptions()

        # Pre-compute embeddings for all spheres
        print("Computing sphere embeddings...")
        self.sphere_embeddings = self._compute_sphere_embeddings()

        print("Sphere classifier ready (lattice-aware v2.0)")

    def _generate_sphere_descriptions(self) -> List[str]:
        """
        Generate descriptive text for each of the 144 spheres using
        the canonical lattice ontology.

        Returns:
            List of 144 sphere descriptions
        """
        descriptions = []

        for idx in range(144):
            house_idx, house_name = house_for_sphere(idx)
            sphere_name = SPHERES[idx]
            address = address_for_index(idx)
            keywords = KEYWORDS.get(idx, [])

            # Create rich description from canonical data
            description = f"{sphere_name} ({address}) is a domain within {house_name}. "
            if keywords:
                description += f"It covers topics including {', '.join(keywords[:5])}. "
            description += f"It represents knowledge and research in {sphere_name.lower()}. "

            # Add house-specific context
            context = HOUSE_CONTEXT.get(house_idx, "")
            if context:
                description += context

            descriptions.append(description)

        return descriptions

    def _compute_sphere_embeddings(self) -> np.ndarray:
        """
        Pre-compute embeddings for all 144 sphere descriptions.

        Returns:
            numpy array of shape (144, embedding_dim)
        """
        embeddings = []
        for desc in self.sphere_descriptions:
            emb = self.embedding_model.embed_query(desc)
            embeddings.append(emb)

        return np.array(embeddings)

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def classify(self, text: str, min_confidence: float = 0.0) -> Dict:
        """
        Classify text into 12×12+1 lattice framework.

        Args:
            text: Text content to classify
            min_confidence: Minimum confidence threshold (0-1)

        Returns:
            {
                "address": "H04.S06",       # Lattice address (primary ID)
                "sphere_name": "Cognitive Science",
                "house": "Social Sciences",
                "house_id": "H04",
                "confidence": 0.87,
                "flat_index": 41,            # 0-143
                "house_index": 3,            # 0-11
                "sphere_index": 5,           # 0-11 within house
                "legacy_id": "S042"          # Backward compat
            }
        """
        # Generate embedding for input text
        text_embedding = np.array(self.embedding_model.embed_query(text))

        # Compute similarities with all spheres
        similarities = []
        for sphere_emb in self.sphere_embeddings:
            sim = self._cosine_similarity(text_embedding, sphere_emb)
            similarities.append(sim)

        # Find best match
        best_idx = np.argmax(similarities)
        confidence = float(similarities[best_idx])

        # Check confidence threshold
        if confidence < min_confidence:
            return {
                "address": "E145",
                "sphere_name": "Unclassified",
                "house": "Admin Sphere",
                "house_id": "E145",
                "confidence": confidence,
                "flat_index": -1,
                "house_index": -1,
                "sphere_index": -1,
                "legacy_id": "Unknown",
                "warning": f"Confidence {confidence:.2f} below threshold {min_confidence}"
            }

        # Build result with lattice addresses
        house_idx, house_name = house_for_sphere(best_idx)
        sphere_in_house = best_idx % 12

        return {
            "address": address_for_index(best_idx),
            "sphere_name": SPHERES[best_idx],
            "house": house_name,
            "house_id": HOUSE_IDS[house_idx],
            "confidence": confidence,
            "flat_index": best_idx,
            "house_index": house_idx,
            "sphere_index": sphere_in_house,
            "legacy_id": f"S{best_idx + 1:03d}",
        }

    def batch_classify(self, texts: List[str], min_confidence: float = 0.0) -> List[Dict]:
        """
        Classify multiple texts in batch.

        Args:
            texts: List of text content to classify
            min_confidence: Minimum confidence threshold (0-1)

        Returns:
            List of classification results
        """
        results = []
        for text in texts:
            result = self.classify(text, min_confidence)
            results.append(result)

        return results

    def get_sphere_info(self, sphere_id: str) -> Dict:
        """
        Get detailed information about a specific sphere.

        Args:
            sphere_id: Lattice address (H02.S11), legacy ID (S001-S144),
                       or flat index (0-143)

        Returns:
            Sphere information dictionary
        """
        # Parse sphere ID — support lattice, legacy, and flat index
        if isinstance(sphere_id, str) and "." in sphere_id:
            # Lattice address: H02.S11
            parts = sphere_id.split(".")
            h_idx = HOUSE_IDS.index(parts[0]) if parts[0] in HOUSE_IDS else -1
            s_idx = int(parts[1][1:]) - 1 if len(parts) > 1 else -1
            flat_idx = h_idx * 12 + s_idx if h_idx >= 0 and s_idx >= 0 else -1
        elif isinstance(sphere_id, str) and sphere_id.startswith('S'):
            # Legacy: S001-S144
            flat_idx = int(sphere_id[1:]) - 1
        elif isinstance(sphere_id, str) and sphere_id == "E145":
            return {
                "address": "E145",
                "sphere_name": "Admin Sphere",
                "house": "Element 145",
                "house_id": "E145",
                "description": "Cross-domain meta-coordination and synthesis",
                "flat_index": 144,
            }
        else:
            flat_idx = int(sphere_id)

        if flat_idx < 0 or flat_idx >= 144:
            return {"error": f"Invalid sphere ID: {sphere_id}"}

        house_idx, house_name = house_for_sphere(flat_idx)

        return {
            "address": address_for_index(flat_idx),
            "sphere_name": SPHERES[flat_idx],
            "house": house_name,
            "house_id": HOUSE_IDS[house_idx],
            "description": self.sphere_descriptions[flat_idx],
            "flat_index": flat_idx,
            "house_index": house_idx,
            "sphere_index": flat_idx % 12,
            "legacy_id": f"S{flat_idx + 1:03d}",
        }


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """CLI interface for sphere classifier"""
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Classify text into 12x12+1 lattice framework"
    )
    parser.add_argument("text", nargs="?", help="Text to classify (or use --file)")
    parser.add_argument("--file", help="File to classify")
    parser.add_argument("--batch", action="store_true",
                        help="Batch mode (one text per line)")
    parser.add_argument("--min-confidence", type=float, default=0.0,
                        help="Minimum confidence threshold")
    parser.add_argument("--info",
                        help="Get info about a sphere (H02.S11, S001-S144, or 0-143)")

    args = parser.parse_args()

    # Initialize classifier
    classifier = SphereClassifier()

    # Get sphere info
    if args.info:
        info = classifier.get_sphere_info(args.info)
        print(json.dumps(info, indent=2))
        return

    # Read text
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            if args.batch:
                texts = [line.strip() for line in f if line.strip()]
                results = classifier.batch_classify(texts, args.min_confidence)
                for i, result in enumerate(results):
                    print(f"\n--- Text {i+1} ---")
                    print(json.dumps(result, indent=2))
            else:
                text = f.read()
                result = classifier.classify(text, args.min_confidence)
                print(json.dumps(result, indent=2))
    elif args.text:
        result = classifier.classify(args.text, args.min_confidence)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
