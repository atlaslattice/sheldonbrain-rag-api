#!/usr/bin/env python3
"""
RAG API with Gemini Embeddings — Lattice-Aware v2.0

Replaces OpenAI with Google's Gemini for embeddings.
Phase 1.1 Migration: All stored vectors now carry canonical 12×12+1
lattice metadata (house, sphere, house_name, sphere_name) via the
vendored ontology in canonical/.

Changes from v1.0:
  - /store auto-classifies text into lattice spheres before storage
  - /query supports house/sphere metadata filters
  - /health reports ontology version
  - New /classify endpoint for standalone classification
  - New /lattice endpoint for ontology introspection
"""
import os
import sys
import logging
from datetime import datetime
from typing import List, Dict, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from pinecone import Pinecone
from nanoid import generate as nanoid

# Add project root to path for canonical imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from canonical.lattice_ontology_v2 import (
    SPHERES, HOUSE_NAMES, HOUSE_IDS,
    classify_text, get_activated_context,
)
from canonical.sphere_classifier_v2 import pinecone_metadata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ontology version tracking
ONTOLOGY_VERSION = os.getenv("LATTICE_VERSION", "12x12+1-v2.0")
ONTOLOGY_SOURCE_COMMIT = os.getenv("ONTOLOGY_SOURCE_COMMIT", "vendored-snapshot")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY environment variable not set")
else:
    genai.configure(api_key=GOOGLE_API_KEY)
    logger.info("Gemini configured successfully")

# Initialize Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "sheldonbrain-rag")

if not PINECONE_API_KEY:
    logger.error("PINECONE_API_KEY environment variable not set")
else:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX)
    logger.info(f"Pinecone index '{PINECONE_INDEX}' initialized")


class GeminiEmbedder:
    """Generate embeddings using Gemini"""

    def __init__(self):
        self.model_name = "models/text-embedding-004"
        logger.info(f"Using Gemini embedding model: {self.model_name}")

    def embed(self, text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> List[float]:
        """Generate embedding for text using Gemini."""
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type=task_type
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def embed_batch(self, texts: List[str], task_type: str = "RETRIEVAL_DOCUMENT") -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=texts,
                task_type=task_type
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise


class RAGMemory:
    """RAG memory system with Gemini embeddings and lattice-aware metadata."""

    def __init__(self):
        self.embedder = GeminiEmbedder()
        self.namespace = "baseline"
        logger.info("RAG Memory initialized with Gemini embeddings + lattice ontology")

    def store(self, text: str, metadata: Optional[Dict] = None) -> str:
        """Store insight in vector database with auto-classification.

        If metadata does not already contain 'house' and 'sphere' fields,
        the text is auto-classified using the canonical 12×12+1 ontology.

        Args:
            text: The insight text to store
            metadata: Optional metadata (sphere, source, novelty, etc.)

        Returns:
            Vector ID of stored insight
        """
        if metadata is None:
            metadata = {}

        # Auto-classify if lattice metadata is missing
        if "house" not in metadata or "sphere" not in metadata:
            lattice_meta = pinecone_metadata(
                text,
                source=metadata.get("source", "rag-api")
            )
            # Merge: user-provided metadata takes precedence
            for key, value in lattice_meta.items():
                if key not in metadata:
                    metadata[key] = value
            logger.info(
                f"Auto-classified: {metadata.get('sphere', '?')} "
                f"({metadata.get('sphere_name', '?')})"
            )

        # Ensure text is in metadata for retrieval
        metadata["text"] = text
        if "timestamp" not in metadata:
            metadata["timestamp"] = datetime.utcnow().isoformat()

        # Generate embedding
        logger.info(f"Generating embedding for text: {text[:50]}...")
        embedding = self.embedder.embed(text, task_type="RETRIEVAL_DOCUMENT")

        # Generate unique ID
        vector_id = f"vec_{nanoid(size=10)}"

        # Store in Pinecone
        logger.info(f"Storing vector {vector_id} in Pinecone")
        index.upsert(
            vectors=[(vector_id, embedding, metadata)],
            namespace=self.namespace
        )

        logger.info(f"Successfully stored insight with ID: {vector_id}")
        return vector_id

    def query(self, query_text: str, top_k: int = 5,
              filter_dict: Optional[Dict] = None) -> List[Dict]:
        """Semantic search over stored insights.

        Supports lattice-aware filtering:
            {"house": {"$eq": "H02"}}
            {"sphere": {"$eq": "H02.S11"}}

        Args:
            query_text: The search query
            top_k: Number of results to return
            filter_dict: Optional metadata filters (Pinecone filter syntax)

        Returns:
            List of matching insights with scores
        """
        # Generate query embedding
        logger.info(f"Generating query embedding for: {query_text[:50]}...")
        query_embedding = self.embedder.embed(query_text, task_type="RETRIEVAL_QUERY")

        # Query Pinecone
        logger.info(f"Querying Pinecone for top {top_k} results")
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            namespace=self.namespace,
            filter=filter_dict
        )

        # Format results
        memories = []
        for match in results.matches:
            memories.append({
                "id": match.id,
                "score": float(match.score),
                "text": match.metadata.get("text", ""),
                "house": match.metadata.get("house", ""),
                "sphere": match.metadata.get("sphere", ""),
                "house_name": match.metadata.get("house_name", ""),
                "sphere_name": match.metadata.get("sphere_name", ""),
                "metadata": {
                    k: v for k, v in match.metadata.items()
                    if k not in ("text",)
                }
            })

        logger.info(f"Found {len(memories)} matching insights")
        return memories

    def delete(self, vector_id: str) -> bool:
        """Delete insight from vector database."""
        try:
            logger.info(f"Deleting vector {vector_id}")
            index.delete(ids=[vector_id], namespace=self.namespace)
            logger.info(f"Successfully deleted vector {vector_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting vector: {e}")
            return False

    def get_stats(self) -> Dict:
        """Get index statistics."""
        try:
            stats = index.describe_index_stats()
            return {
                "total_vector_count": stats.total_vector_count,
                "namespaces": stats.namespaces,
                "dimension": stats.dimension
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}


# Initialize RAG memory
rag = RAGMemory()


# ============================================================================
# API Routes
# ============================================================================

@app.route("/", methods=["GET"])
def root():
    """Root endpoint with API information."""
    return jsonify({
        "service": "rag-api",
        "version": "2.0-gemini-lattice",
        "embedding_model": "Gemini text-embedding-004",
        "ontology": ONTOLOGY_VERSION,
        "description": "Multi-AI Persistent Memory System with Gemini embeddings "
                       "and 12×12+1 lattice ontology",
        "endpoints": {
            "GET /health": "System health and statistics",
            "POST /query": "Semantic search over stored insights",
            "POST /store": "Store new insight (auto-classified)",
            "POST /delete": "Delete insight by ID",
            "POST /classify": "Classify text into lattice spheres",
            "GET /lattice": "Ontology introspection"
        },
        "documentation": "https://github.com/atlaslattice/sheldonbrain-rag-api"
    })


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    try:
        stats = rag.get_stats()
        return jsonify({
            "status": "healthy",
            "service": "rag-api-gemini-lattice",
            "embedding_model": "Gemini text-embedding-004",
            "ontology_version": ONTOLOGY_VERSION,
            "ontology_source_commit": ONTOLOGY_SOURCE_COMMIT,
            "houses": len(HOUSE_NAMES),
            "spheres": len(SPHERES),
            "vector_count": stats.get("total_vector_count", 0),
            "index": PINECONE_INDEX,
            "namespace": rag.namespace,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


@app.route("/query", methods=["POST"])
def query():
    """Query endpoint for semantic search.

    Supports lattice-aware filtering via the 'filter' field:
        {"filter": {"house": {"$eq": "H02"}}}
        {"filter": {"sphere": {"$eq": "H02.S11"}}}
    """
    try:
        data = request.json

        if not data or "query" not in data:
            return jsonify({"error": "Missing 'query' field"}), 400

        query_text = data["query"]
        top_k = data.get("top_k", 5)
        filter_dict = data.get("filter")

        # Validate top_k
        if not isinstance(top_k, int) or top_k < 1 or top_k > 100:
            return jsonify({"error": "top_k must be between 1 and 100"}), 400

        # Query RAG
        import time
        start_time = time.time()
        memories = rag.query(query_text, top_k, filter_dict)
        query_time = (time.time() - start_time) * 1000

        return jsonify({
            "memories": memories,
            "query_time_ms": round(query_time, 2),
            "count": len(memories)
        })

    except Exception as e:
        logger.error(f"Query failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/store", methods=["POST"])
def store():
    """Store endpoint for adding insights.

    Text is auto-classified into the 12×12+1 lattice ontology.
    You can override classification by providing 'house' and 'sphere'
    in the metadata field.
    """
    try:
        data = request.json

        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        text = data["text"]
        metadata = data.get("metadata", {})

        # Validate text
        if not text or len(text.strip()) == 0:
            return jsonify({"error": "Text cannot be empty"}), 400

        # Store in RAG (auto-classifies if no lattice metadata provided)
        vector_id = rag.store(text, metadata)
        stats = rag.get_stats()

        return jsonify({
            "id": vector_id,
            "status": "stored",
            "vector_count": stats.get("total_vector_count", 0)
        })

    except Exception as e:
        logger.error(f"Store failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/delete", methods=["POST"])
def delete():
    """Delete endpoint for removing insights."""
    try:
        data = request.json

        if not data or "id" not in data:
            return jsonify({"error": "Missing 'id' field"}), 400

        vector_id = data["id"]

        # Delete from RAG
        success = rag.delete(vector_id)

        if success:
            stats = rag.get_stats()
            return jsonify({
                "status": "deleted",
                "vector_count": stats.get("total_vector_count", 0)
            })
        else:
            return jsonify({"error": "Failed to delete vector"}), 500

    except Exception as e:
        logger.error(f"Delete failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/classify", methods=["POST"])
def classify():
    """Classify text into lattice spheres without storing.

    Request body:
        {"text": "...", "top_k": 5, "with_context": false}

    Returns classification results with optional context activation.
    """
    try:
        data = request.json

        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        text = data["text"]
        top_k = data.get("top_k", 5)
        with_context = data.get("with_context", False)

        if with_context:
            result = get_activated_context(text)
            return jsonify({
                "classification": result["primary_spheres"],
                "activated_houses": result["activated_houses"],
                "edges": result["edges"],
                "ontology_version": ONTOLOGY_VERSION
            })
        else:
            results = classify_text(text, top_k=top_k)
            return jsonify({
                "classification": results,
                "ontology_version": ONTOLOGY_VERSION
            })

    except Exception as e:
        logger.error(f"Classification failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/lattice", methods=["GET"])
def lattice():
    """Ontology introspection endpoint.

    Returns the full lattice structure: 12 Houses, 144 Spheres,
    and Element 145 admin sphere.
    """
    houses = []
    for i, name in enumerate(HOUSE_NAMES):
        house_id = HOUSE_IDS[i]
        spheres_in_house = []
        for j in range(12):
            idx = i * 12 + j
            spheres_in_house.append({
                "address": f"{house_id}.S{j+1:02d}",
                "name": SPHERES[idx],
                "index": idx
            })
        houses.append({
            "id": house_id,
            "name": name,
            "spheres": spheres_in_house
        })

    return jsonify({
        "ontology_version": ONTOLOGY_VERSION,
        "houses": houses,
        "total_spheres": 144,
        "element_145": {
            "id": "E145",
            "name": "Admin Sphere",
            "role": "Cross-domain meta-coordination"
        }
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Starting RAG API with Gemini embeddings + lattice ontology on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
