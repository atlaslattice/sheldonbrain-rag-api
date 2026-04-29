#!/usr/bin/env python3
"""
Sphere Classifier for RAG Ingestion Pipeline

Automatically classifies text content into the 144-sphere ontological framework
using vector similarity search. Integrates canonical 12x12+1 lattice logic
with the Sheldonbrain RAG system.

Based on: canonical lattice ontology (T.R.A.V.S)
Adapted for: Sheldonbrain Multi-AI Persistent Memory System
"""

import os
import sys
from typing import Dict, List, Optional
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import numpy as np

# Import canonical 12x12+1 lattice ontology
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from canonical.lattice_ontology_v2 import SPHERES, ELEMENTS, CATEGORY_NAMES, HOUSE_NAMES as CATEGORY_NAMES_V2, HOUSE_IDS

# ============================================================================
# SPHERE CLASSIFIER
# ============================================================================

class SphereClassifier:
    """
    Classifies text into 144-sphere ontological framework using vector similarity.
    
    Uses HuggingFace embeddings and cosine similarity to match content against
    sphere descriptions, returning the best match with confidence score.
    """
    
    def __init__(self, embedding_model=None):
        """
        Initialize sphere classifier with embedding model.
        
        Args:
            embedding_model: Optional pre-initialized embedding model.
                           Defaults to sentence-transformers/all-MiniLM-L6-v2
        """
        if embedding_model is None:
            print("🔧 Loading embedding model...")
            self.embedding_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        else:
            self.embedding_model = embedding_model
        
        # Generate sphere descriptions
        print("📚 Generating 144-sphere reference descriptions...")
        self.sphere_descriptions = self._generate_sphere_descriptions()
        
        # Pre-compute embeddings for all spheres
        print("🧮 Computing sphere embeddings...")
        self.sphere_embeddings = self._compute_sphere_embeddings()
        
        print("✅ Sphere classifier ready!")
    
    def _generate_sphere_descriptions(self) -> List[str]:
        """
        Generate descriptive text for each of the 144 spheres.
        
        Returns:
            List of 144 sphere descriptions
        """
        descriptions = []
        
        for idx in range(144):
            cat = idx // 12
            sub = idx % 12
            sphere_name = SPHERES[idx]
            category_name = CATEGORY_NAMES[cat]
            element = ELEMENTS[idx]
            
            # Create rich description
            description = f"{sphere_name} is a field within {category_name}. "
            description += f"It is associated with {element} and represents "
            description += f"knowledge and research in the domain of {sphere_name.lower()}. "
            
            # Add category-specific context
            if cat == 0:  # Natural Sciences
                description += "This involves empirical observation, experimentation, and understanding of natural phenomena."
            elif cat == 1:  # Formal Sciences
                description += "This involves abstract reasoning, mathematical modeling, and logical analysis."
            elif cat == 2:  # Social Sciences
                description += "This involves the study of human behavior, society, and social relationships."
            elif cat == 3:  # Humanities
                description += "This involves the study of human culture, history, and philosophical thought."
            elif cat == 4:  # Arts
                description += "This involves creative expression, aesthetic appreciation, and artistic practice."
            elif cat == 5:  # Engineering & Technology
                description += "This involves the application of scientific principles to design and build systems."
            elif cat == 6:  # Medicine & Health
                description += "This involves the study and practice of maintaining human health and treating disease."
            elif cat == 7:  # Education
                description += "This involves the theory and practice of teaching, learning, and educational systems."
            elif cat == 8:  # Business & Economics
                description += "This involves the study of commerce, markets, and economic systems."
            elif cat == 9:  # Law & Politics
                description += "This involves the study of legal systems, governance, and political structures."
            elif cat == 10:  # Religion & Philosophy
                description += "This involves the study of belief systems, spiritual practices, and philosophical inquiry."
            elif cat == 11:  # Interdisciplinary Studies
                description += "This involves the integration of multiple disciplines to address complex problems."
            
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
        """
        Compute cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
        
        Returns:
            Cosine similarity score (0-1)
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def classify(self, text: str, min_confidence: float = 0.0) -> Dict:
        """
        Classify text into 144-sphere framework.
        
        Args:
            text: Text content to classify
            min_confidence: Minimum confidence threshold (0-1)
        
        Returns:
            {
                "sphere_id": "S042",  # S001-S144
                "sphere_name": "Molybdenum (42)",
                "category": "Interdisciplinary Studies",
                "element": "Molybdenum (42)",
                "confidence": 0.87,
                "flat_index": 41,  # 0-143
                "category_index": 3,  # 0-11
                "subset_index": 5   # 0-11
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
                "sphere_id": "Unknown",
                "sphere_name": "Unknown",
                "category": "Unknown",
                "element": "Unknown",
                "confidence": confidence,
                "flat_index": -1,
                "category_index": -1,
                "subset_index": -1,
                "warning": f"Confidence {confidence:.2f} below threshold {min_confidence}"
            }
        
        # Build result
        cat = best_idx // 12
        sub = best_idx % 12
        
        return {
            "sphere_id": f"S{best_idx + 1:03d}",  # S001-S144
            "sphere_name": SPHERES[best_idx],
            "category": CATEGORY_NAMES[cat],
            "element": ELEMENTS[best_idx],
            "confidence": confidence,
            "flat_index": best_idx,
            "category_index": cat,
            "subset_index": sub
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
            sphere_id: Sphere ID (S001-S144) or flat index (0-143)
        
        Returns:
            Sphere information dictionary
        """
        # Parse sphere ID
        if isinstance(sphere_id, str) and sphere_id.startswith('S'):
            flat_idx = int(sphere_id[1:]) - 1
        else:
            flat_idx = int(sphere_id)
        
        if flat_idx < 0 or flat_idx >= 144:
            return {"error": "Invalid sphere ID"}
        
        cat = flat_idx // 12
        sub = flat_idx % 12
        
        return {
            "sphere_id": f"S{flat_idx + 1:03d}",
            "sphere_name": SPHERES[flat_idx],
            "category": CATEGORY_NAMES[cat],
            "element": ELEMENTS[flat_idx],
            "description": self.sphere_descriptions[flat_idx],
            "flat_index": flat_idx,
            "category_index": cat,
            "subset_index": sub
        }


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """CLI interface for sphere classifier"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Classify text into 144-sphere framework")
    parser.add_argument("text", nargs="?", help="Text to classify (or use --file)")
    parser.add_argument("--file", help="File to classify")
    parser.add_argument("--batch", action="store_true", help="Batch mode (one text per line)")
    parser.add_argument("--min-confidence", type=float, default=0.0, help="Minimum confidence threshold")
    parser.add_argument("--info", help="Get info about a specific sphere (S001-S144)")
    
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
    import json
    main()
