#!/usr/bin/env python3
"""
RAG API with Gemini Embeddings
Replaces OpenAI with Google's Gemini for embeddings
"""
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from pinecone import Pinecone
from nanoid import generate as nanoid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        """
        Generate embedding for text using Gemini
        
        Args:
            text: Text to embed
            task_type: One of:
                - RETRIEVAL_QUERY: For search queries
                - RETRIEVAL_DOCUMENT: For documents to be searched
                - SEMANTIC_SIMILARITY: For similarity comparison
                - CLASSIFICATION: For text classification
                - CLUSTERING: For clustering
        
        Returns:
            List of floats representing the embedding
        """
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
        """Generate embeddings for multiple texts"""
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
    """RAG memory system with Gemini embeddings"""
    
    def __init__(self):
        self.embedder = GeminiEmbedder()
        self.namespace = "baseline"
        logger.info("RAG Memory initialized with Gemini embeddings")
    
    def store(self, text: str, metadata: Optional[Dict] = None) -> str:
        """
        Store insight in vector database
        
        Args:
            text: The insight text to store
            metadata: Optional metadata (sphere, source, novelty, etc.)
        
        Returns:
            Vector ID of stored insight
        """
        if metadata is None:
            metadata = {}
        
        # Add text to metadata for retrieval
        metadata["text"] = text
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
    
    def query(self, query_text: str, top_k: int = 5, filter_dict: Optional[Dict] = None) -> List[Dict]:
        """
        Semantic search over stored insights
        
        Args:
            query_text: The search query
            top_k: Number of results to return
            filter_dict: Optional metadata filters
        
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
                "metadata": {k: v for k, v in match.metadata.items() if k != "text"}
            })
        
        logger.info(f"Found {len(memories)} matching insights")
        return memories
    
    def delete(self, vector_id: str) -> bool:
        """Delete insight from vector database"""
        try:
            logger.info(f"Deleting vector {vector_id}")
            index.delete(ids=[vector_id], namespace=self.namespace)
            logger.info(f"Successfully deleted vector {vector_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting vector: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get index statistics"""
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


# API Routes

@app.route("/", methods=["GET"])
def root():
    """Root endpoint with API information"""
    return jsonify({
        "service": "rag-api",
        "version": "2.0-gemini",
        "embedding_model": "Gemini text-embedding-004",
        "description": "Multi-AI Persistent Memory System with Gemini embeddings",
        "endpoints": {
            "GET /health": "System health and statistics",
            "POST /query": "Semantic search over stored insights",
            "POST /store": "Store new insight",
            "POST /delete": "Delete insight by ID"
        },
        "documentation": "https://github.com/atlaslattice/sheldonbrain-rag-api"
    })


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    try:
        stats = rag.get_stats()
        return jsonify({
            "status": "healthy",
            "service": "rag-api-gemini",
            "embedding_model": "Gemini text-embedding-004",
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
    """Query endpoint for semantic search"""
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
    """Store endpoint for adding insights"""
    try:
        data = request.json
        
        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400
        
        text = data["text"]
        metadata = data.get("metadata", {})
        
        # Validate text
        if not text or len(text.strip()) == 0:
            return jsonify({"error": "Text cannot be empty"}), 400
        
        # Store in RAG
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
    """Delete endpoint for removing insights"""
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


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Starting RAG API with Gemini embeddings on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
