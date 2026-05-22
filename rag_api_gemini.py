#!/usr/bin/env python3
"""
RAG API with Gemini Embeddings — Lattice-Aware v2.1

Sheldonbrain is a multi-agent persistent memory substrate. This file keeps
semantic retrieval, lattice classification, provenance, and governance in the
same API surface.

v2.1 product-governance patch:
  - Adds lifecycle metadata defaults: active / archived / quarantined / etc.
  - Adds ratification and execution-authority defaults.
  - Adds content hashes and flattened provenance metadata.
  - Adds retrieval receipts to /query responses.
  - Adds /lifecycle endpoint for non-destructive state transitions.
  - Deprecates /delete by mapping it to archive unless ALLOW_HARD_DELETE=true.

Core invariant:
  memory != permission
"""
import hashlib
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from flask import Flask, jsonify, request
from flask_cors import CORS
import google.generativeai as genai
from nanoid import generate as nanoid
from pinecone import Pinecone

# Add project root to path for canonical imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from canonical.lattice_ontology_v2 import (  # noqa: E402
    HOUSE_IDS,
    HOUSE_NAMES,
    SPHERES,
    classify_text,
    get_activated_context,
)
from canonical.sphere_classifier_v2 import pinecone_metadata  # noqa: E402

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ontology version tracking
ONTOLOGY_VERSION = os.getenv("LATTICE_VERSION", "12x12+1-v2.0")
ONTOLOGY_SOURCE_COMMIT = os.getenv("ONTOLOGY_SOURCE_COMMIT", "vendored-snapshot")

# Governance defaults
DEFAULT_LIFECYCLE = "active"
DEFAULT_RATIFICATION = "unratified"
EXECUTION_AUTHORITY_DEFAULT = False
ACTIVE_LIFECYCLES = {"active", "superseded"}
ARCHIVAL_LIFECYCLES = {"archived", "quarantined", "redacted_pointer"}
LIFECYCLE_OPERATIONS = {
    "archive": "archived",
    "quarantine": "quarantined",
    "supersede": "superseded",
    "redact_pointer": "redacted_pointer",
    "restore": "active",
}
ALLOW_HARD_DELETE = os.getenv("ALLOW_HARD_DELETE", "false").lower() == "true"

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
    logger.info("Pinecone index '%s' initialized", PINECONE_INDEX)


def utc_now() -> str:
    """Return an ISO-8601-ish UTC timestamp without local timezone ambiguity."""
    return datetime.utcnow().isoformat() + "Z"


def content_hash(text: str) -> str:
    """Return a stable content receipt for a memory payload."""
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def apply_governance_defaults(text: str, metadata: Dict) -> Dict:
    """Add lifecycle, provenance, and execution-boundary defaults.

    Pinecone metadata is kept flat for compatibility. Nested provenance can be
    reconstructed from fields prefixed with source_/created_/content_hash.
    """
    now = utc_now()

    metadata.setdefault("timestamp", now)
    metadata.setdefault("created_at", metadata.get("timestamp", now))
    metadata.setdefault("created_by_agent", metadata.get("source", "rag-api"))
    metadata.setdefault("created_by_model", metadata.get("model", "unknown"))
    metadata.setdefault("source_type", metadata.get("source_type", "api"))
    metadata.setdefault("source_uri", metadata.get("source_uri", ""))
    metadata.setdefault("lifecycle", DEFAULT_LIFECYCLE)
    metadata.setdefault("ratification", DEFAULT_RATIFICATION)
    metadata.setdefault("execution_authority", EXECUTION_AUTHORITY_DEFAULT)
    metadata.setdefault("content_hash", content_hash(text))

    return metadata


def lifecycle_is_visible(metadata: Dict, include_archived: bool = False) -> bool:
    """Return whether a record should appear in default retrieval results."""
    if include_archived:
        return True

    lifecycle = metadata.get("lifecycle", DEFAULT_LIFECYCLE)
    return lifecycle in ACTIVE_LIFECYCLES


def build_retrieval_receipt(
    query_text: str,
    top_k: int,
    filter_dict: Optional[Dict],
    include_archived: bool,
    elapsed_ms: float,
) -> Dict:
    """Build an auditable receipt for a query operation."""
    return {
        "timestamp": utc_now(),
        "query_hash": content_hash(query_text),
        "index": PINECONE_INDEX,
        "namespace": rag.namespace,
        "filters": filter_dict or {},
        "top_k": top_k,
        "include_archived": include_archived,
        "ontology_version": ONTOLOGY_VERSION,
        "ontology_source_commit": ONTOLOGY_SOURCE_COMMIT,
        "query_time_ms": round(elapsed_ms, 2),
    }


class GeminiEmbedder:
    """Generate embeddings using Gemini."""

    def __init__(self):
        self.model_name = "models/text-embedding-004"
        logger.info("Using Gemini embedding model: %s", self.model_name)

    def embed(self, text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> List[float]:
        """Generate embedding for text using Gemini."""
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type=task_type,
            )
            return result["embedding"]
        except Exception as e:
            logger.error("Error generating embedding: %s", e)
            raise

    def embed_batch(
        self,
        texts: List[str],
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=texts,
                task_type=task_type,
            )
            return result["embedding"]
        except Exception as e:
            logger.error("Error generating batch embeddings: %s", e)
            raise


class RAGMemory:
    """RAG memory system with Gemini embeddings and lattice-aware metadata."""

    def __init__(self):
        self.embedder = GeminiEmbedder()
        self.namespace = "baseline"
        logger.info("RAG Memory initialized with Gemini embeddings + lattice ontology")

    def store(self, text: str, metadata: Optional[Dict] = None) -> str:
        """Store insight in vector database with auto-classification and governance.

        If metadata does not already contain 'house' and 'sphere' fields, the
        text is auto-classified using the canonical 12x12+1 ontology.
        """
        if metadata is None:
            metadata = {}
        else:
            metadata = dict(metadata)

        # Auto-classify if lattice metadata is missing.
        if "house" not in metadata or "sphere" not in metadata:
            lattice_meta = pinecone_metadata(
                text,
                source=metadata.get("source", "rag-api"),
            )
            # Merge: user-provided metadata takes precedence.
            for key, value in lattice_meta.items():
                if key not in metadata:
                    metadata[key] = value
            logger.info(
                "Auto-classified: %s (%s)",
                metadata.get("sphere", "?"),
                metadata.get("sphere_name", "?"),
            )

        # Ensure text and governance metadata are available for retrieval.
        metadata["text"] = text
        metadata = apply_governance_defaults(text, metadata)

        # Generate embedding.
        logger.info("Generating embedding for text: %s...", text[:50])
        embedding = self.embedder.embed(text, task_type="RETRIEVAL_DOCUMENT")

        # Generate unique ID.
        vector_id = f"vec_{nanoid(size=10)}"

        # Store in Pinecone.
        logger.info("Storing vector %s in Pinecone", vector_id)
        index.upsert(
            vectors=[(vector_id, embedding, metadata)],
            namespace=self.namespace,
        )

        logger.info("Successfully stored insight with ID: %s", vector_id)
        return vector_id

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        filter_dict: Optional[Dict] = None,
        include_archived: bool = False,
    ) -> Tuple[List[Dict], int]:
        """Semantic search over stored insights.

        Supports lattice-aware Pinecone filters and applies non-destructive
        lifecycle visibility in the application layer for backwards
        compatibility with legacy records that do not yet carry lifecycle data.
        """
        logger.info("Generating query embedding for: %s...", query_text[:50])
        query_embedding = self.embedder.embed(query_text, task_type="RETRIEVAL_QUERY")

        # Over-fetch so archived/quarantined records can be filtered without
        # starving the caller's requested top_k too aggressively.
        pinecone_top_k = min(max(top_k * 3, top_k), 100)

        logger.info("Querying Pinecone for top %s results", pinecone_top_k)
        results = index.query(
            vector=query_embedding,
            top_k=pinecone_top_k,
            include_metadata=True,
            namespace=self.namespace,
            filter=filter_dict,
        )

        memories = []
        hidden_by_lifecycle = 0
        for match in results.matches:
            metadata = match.metadata or {}
            if not lifecycle_is_visible(metadata, include_archived=include_archived):
                hidden_by_lifecycle += 1
                continue

            lifecycle = metadata.get("lifecycle", DEFAULT_LIFECYCLE)
            ratification = metadata.get("ratification", DEFAULT_RATIFICATION)
            execution_authority = bool(
                metadata.get("execution_authority", EXECUTION_AUTHORITY_DEFAULT)
            )

            warnings = []
            if execution_authority:
                warnings.append(
                    "Memory result claims execution authority; callers must still require current user consent."
                )
            if ratification == "unratified":
                warnings.append("Memory is unratified context, not canon.")
            if lifecycle != "active":
                warnings.append(f"Memory lifecycle is {lifecycle}.")

            memories.append({
                "id": match.id,
                "score": float(match.score),
                "text": metadata.get("text", ""),
                "house": metadata.get("house", ""),
                "sphere": metadata.get("sphere", ""),
                "house_name": metadata.get("house_name", ""),
                "sphere_name": metadata.get("sphere_name", ""),
                "lifecycle": lifecycle,
                "ratification": ratification,
                "execution_authority": execution_authority,
                "provenance": {
                    "created_at": metadata.get("created_at", metadata.get("timestamp", "")),
                    "created_by_agent": metadata.get("created_by_agent", metadata.get("source", "")),
                    "created_by_model": metadata.get("created_by_model", metadata.get("model", "")),
                    "source_type": metadata.get("source_type", ""),
                    "source_uri": metadata.get("source_uri", ""),
                    "content_hash": metadata.get("content_hash", ""),
                },
                "warnings": warnings,
                "metadata": {
                    k: v for k, v in metadata.items()
                    if k not in (
                        "text",
                        "created_at",
                        "created_by_agent",
                        "created_by_model",
                        "source_type",
                        "source_uri",
                        "content_hash",
                    )
                },
            })

            if len(memories) >= top_k:
                break

        logger.info("Found %s matching insights", len(memories))
        return memories, hidden_by_lifecycle

    def lifecycle(self, vector_id: str, operation: str, reason: str = "") -> bool:
        """Apply a non-destructive lifecycle transition to a memory record."""
        if operation not in LIFECYCLE_OPERATIONS:
            raise ValueError(
                f"Unsupported lifecycle operation '{operation}'. "
                f"Allowed: {sorted(LIFECYCLE_OPERATIONS)}"
            )

        target_state = LIFECYCLE_OPERATIONS[operation]
        now = utc_now()
        metadata = {
            "lifecycle": target_state,
            "lifecycle_operation": operation,
            "lifecycle_updated_at": now,
            "lifecycle_reason": reason,
        }

        logger.info(
            "Applying lifecycle operation %s -> %s for vector %s",
            operation,
            target_state,
            vector_id,
        )
        index.update(
            id=vector_id,
            set_metadata=metadata,
            namespace=self.namespace,
        )
        return True

    def delete(self, vector_id: str) -> bool:
        """Hard-delete insight from vector database when explicitly enabled.

        Normal product flows should call lifecycle(..., 'archive') instead.
        """
        try:
            logger.warning("Hard deleting vector %s", vector_id)
            index.delete(ids=[vector_id], namespace=self.namespace)
            logger.info("Successfully deleted vector %s", vector_id)
            return True
        except Exception as e:
            logger.error("Error deleting vector: %s", e)
            return False

    def get_stats(self) -> Dict:
        """Get index statistics."""
        try:
            stats = index.describe_index_stats()
            return {
                "total_vector_count": stats.total_vector_count,
                "namespaces": stats.namespaces,
                "dimension": stats.dimension,
            }
        except Exception as e:
            logger.error("Error getting stats: %s", e)
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
        "version": "2.1-gemini-lattice-governed",
        "embedding_model": "Gemini text-embedding-004",
        "ontology": ONTOLOGY_VERSION,
        "description": "Multi-AI Persistent Memory System with Gemini embeddings, "
                       "12x12+1 lattice ontology, lifecycle governance, "
                       "and retrieval receipts",
        "core_invariant": "memory != permission",
        "endpoints": {
            "GET /health": "System health and statistics",
            "POST /query": "Semantic search over stored insights with retrieval receipt",
            "POST /store": "Store new insight with provenance and auto-classification",
            "POST /lifecycle": "Apply non-destructive lifecycle transition",
            "POST /delete": "Deprecated; archives by default unless ALLOW_HARD_DELETE=true",
            "POST /classify": "Classify text into lattice spheres",
            "GET /lattice": "Ontology introspection",
        },
        "documentation": "https://github.com/atlaslattice/sheldonbrain-rag-api",
    })


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    try:
        stats = rag.get_stats()
        return jsonify({
            "status": "healthy",
            "service": "rag-api-gemini-lattice",
            "version": "2.1-gemini-lattice-governed",
            "embedding_model": "Gemini text-embedding-004",
            "ontology_version": ONTOLOGY_VERSION,
            "ontology_source_commit": ONTOLOGY_SOURCE_COMMIT,
            "houses": len(HOUSE_NAMES),
            "spheres": len(SPHERES),
            "vector_count": stats.get("total_vector_count", 0),
            "index": PINECONE_INDEX,
            "namespace": rag.namespace,
            "allow_hard_delete": ALLOW_HARD_DELETE,
            "lifecycle_operations": sorted(LIFECYCLE_OPERATIONS.keys()),
            "core_invariant": "memory != permission",
            "timestamp": utc_now(),
        })
    except Exception as e:
        logger.error("Health check failed: %s", e)
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
        }), 500


@app.route("/query", methods=["POST"])
def query():
    """Query endpoint for semantic search.

    Supports lattice-aware filtering via the 'filter' field:
        {"filter": {"house": {"$eq": "H02"}}}
        {"filter": {"sphere": {"$eq": "H02.S11"}}}

    Archived/quarantined memories are hidden by default unless
    include_archived=true is provided.
    """
    try:
        data = request.json

        if not data or "query" not in data:
            return jsonify({"error": "Missing 'query' field"}), 400

        query_text = data["query"]
        top_k = data.get("top_k", 5)
        filter_dict = data.get("filter")
        include_archived = bool(data.get("include_archived", False))

        if not isinstance(top_k, int) or top_k < 1 or top_k > 100:
            return jsonify({"error": "top_k must be between 1 and 100"}), 400

        start_time = time.time()
        memories, hidden_by_lifecycle = rag.query(
            query_text,
            top_k,
            filter_dict,
            include_archived=include_archived,
        )
        elapsed_ms = (time.time() - start_time) * 1000

        retrieval_receipt = build_retrieval_receipt(
            query_text=query_text,
            top_k=top_k,
            filter_dict=filter_dict,
            include_archived=include_archived,
            elapsed_ms=elapsed_ms,
        )

        return jsonify({
            "memories": memories,
            "retrieval_receipt": retrieval_receipt,
            "query_time_ms": round(elapsed_ms, 2),
            "count": len(memories),
            "hidden_by_lifecycle": hidden_by_lifecycle,
            "core_invariant": "memory != permission",
        })

    except Exception as e:
        logger.error("Query failed: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route("/store", methods=["POST"])
def store():
    """Store endpoint for adding insights.

    Text is auto-classified into the 12x12+1 lattice ontology. You can override
    classification by providing 'house' and 'sphere' in the metadata field.
    """
    try:
        data = request.json

        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        text = data["text"]
        metadata = data.get("metadata", {})

        if not text or len(text.strip()) == 0:
            return jsonify({"error": "Text cannot be empty"}), 400
        if not isinstance(metadata, dict):
            return jsonify({"error": "metadata must be an object"}), 400

        vector_id = rag.store(text, metadata)
        stats = rag.get_stats()

        return jsonify({
            "id": vector_id,
            "status": "stored",
            "lifecycle": metadata.get("lifecycle", DEFAULT_LIFECYCLE),
            "ratification": metadata.get("ratification", DEFAULT_RATIFICATION),
            "execution_authority": metadata.get(
                "execution_authority",
                EXECUTION_AUTHORITY_DEFAULT,
            ),
            "content_hash": content_hash(text),
            "vector_count": stats.get("total_vector_count", 0),
            "core_invariant": "memory != permission",
        })

    except Exception as e:
        logger.error("Store failed: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route("/lifecycle", methods=["POST"])
def lifecycle():
    """Apply a non-destructive lifecycle transition.

    Request body:
        {"id": "vec_...", "operation": "archive", "reason": "optional"}

    Supported operations: archive, quarantine, supersede, redact_pointer, restore.
    """
    try:
        data = request.json

        if not data or "id" not in data:
            return jsonify({"error": "Missing 'id' field"}), 400
        if "operation" not in data:
            return jsonify({"error": "Missing 'operation' field"}), 400

        vector_id = data["id"]
        operation = data["operation"]
        reason = data.get("reason", "")

        if operation not in LIFECYCLE_OPERATIONS:
            return jsonify({
                "error": "Unsupported lifecycle operation",
                "allowed_operations": sorted(LIFECYCLE_OPERATIONS.keys()),
            }), 400

        rag.lifecycle(vector_id, operation, reason)

        return jsonify({
            "id": vector_id,
            "status": "lifecycle_updated",
            "operation": operation,
            "lifecycle": LIFECYCLE_OPERATIONS[operation],
            "hard_deleted": False,
            "timestamp": utc_now(),
        })

    except Exception as e:
        logger.error("Lifecycle update failed: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route("/delete", methods=["POST"])
def delete():
    """Deprecated delete endpoint.

    By default, this endpoint archives instead of hard-deleting. Hard delete is
    available only when ALLOW_HARD_DELETE=true is set in the environment.
    """
    try:
        data = request.json

        if not data or "id" not in data:
            return jsonify({"error": "Missing 'id' field"}), 400

        vector_id = data["id"]
        reason = data.get("reason", "Deprecated /delete endpoint called")

        if not ALLOW_HARD_DELETE:
            rag.lifecycle(vector_id, "archive", reason)
            stats = rag.get_stats()
            return jsonify({
                "status": "archived",
                "deprecated": True,
                "hard_deleted": False,
                "message": "/delete is deprecated. Memory was archived non-destructively.",
                "vector_count": stats.get("total_vector_count", 0),
            })

        success = rag.delete(vector_id)
        if success:
            stats = rag.get_stats()
            return jsonify({
                "status": "deleted",
                "deprecated": True,
                "hard_deleted": True,
                "vector_count": stats.get("total_vector_count", 0),
            })

        return jsonify({"error": "Failed to delete vector"}), 500

    except Exception as e:
        logger.error("Delete failed: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route("/classify", methods=["POST"])
def classify():
    """Classify text into lattice spheres without storing.

    Request body:
        {"text": "...", "top_k": 5, "with_context": false}
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
                "ontology_version": ONTOLOGY_VERSION,
            })

        results = classify_text(text, top_k=top_k)
        return jsonify({
            "classification": results,
            "ontology_version": ONTOLOGY_VERSION,
        })

    except Exception as e:
        logger.error("Classification failed: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route("/lattice", methods=["GET"])
def lattice():
    """Ontology introspection endpoint."""
    houses = []
    for i, name in enumerate(HOUSE_NAMES):
        house_id = HOUSE_IDS[i]
        spheres_in_house = []
        for j in range(12):
            idx = i * 12 + j
            spheres_in_house.append({
                "address": f"{house_id}.S{j + 1:02d}",
                "name": SPHERES[idx],
                "index": idx,
            })
        houses.append({
            "id": house_id,
            "name": name,
            "spheres": spheres_in_house,
        })

    return jsonify({
        "ontology_version": ONTOLOGY_VERSION,
        "houses": houses,
        "total_spheres": 144,
        "element_145": {
            "id": "E145",
            "name": "Admin Sphere",
            "role": "Cross-domain meta-coordination",
        },
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logger.info(
        "Starting RAG API with Gemini embeddings + lattice ontology on port %s",
        port,
    )
    app.run(host="0.0.0.0", port=port, debug=False)
