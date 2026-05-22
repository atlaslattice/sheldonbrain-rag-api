# 🧠 Multi-AI Persistent Memory System (Sheldonbrain RAG API)

**Version:** 2.0 (Gemini Embeddings)  
**Status:** ✅ Production Ready  
**Backup:** 100% Complete (105/105 vectors)

A production-ready RAG (Retrieval-Augmented Generation) API powered by Google Gemini embeddings and Pinecone vector database, enabling persistent memory across multiple AI instances.

---

## Product Spine

Sheldonbrain is more than a vector-search wrapper. It is being shaped into a trusted multi-agent memory substrate with provenance, ontology, lifecycle controls, and explicit execution boundaries.

Read the product spine: [`docs/OPENAI_PRODUCT_SPINE.md`](docs/OPENAI_PRODUCT_SPINE.md)

Core product invariant:

```text
Nothing disappears silently.
Nothing becomes canon without provenance.
Nothing executes merely because it was remembered.
```

---

## 🎯 Overview

This system solves **AI context amnesia** by providing a shared, persistent memory substrate that multiple AI agents (Claude, Gemini, GPT, Grok, etc.) can query and update. Every insight stored is never erased - implementing the **Zero Erasure** principle.

### Key Features

- ✅ **Gemini text-embedding-004** (768 dimensions)
- ✅ **Pinecone vector database** (baseline namespace)
- ✅ **Flask REST API** with CORS support
- ✅ **Dual redundancy** (Pinecone + Notion backup)
- ✅ **Docker deployment** ready
- ✅ **Google Cloud Run** compatible

---

## 🏗️ Architecture

```
┌─────────────────┐
│   AI Agents     │
│ (Claude, Gemini,│
│  GPT, Grok...)  │
└────────┬────────┘
         │
         │ HTTP/REST
         │
┌────────▼────────┐
│   RAG API       │
│  (Flask + CORS) │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼───┐
│Gemini│  │Pinecone│
│Embed │  │ Vector │
│ API  │  │   DB   │
└──────┘  └────────┘
            │
            │ Backup
            │
        ┌───▼───┐
        │ Notion│
        │  DB   │
        └───────┘
```

---

## 🔧 Installation

### Prerequisites

- Python 3.11+
- Google Cloud API key (for Gemini)
- Pinecone API key
- (Optional) Docker for containerized deployment

### Local Setup

```bash
# Clone repository
git clone https://github.com/splitmerge420/sheldonbrain-rag-api.git
cd sheldonbrain-rag-api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_API_KEY="your-gemini-api-key"
export PINECONE_API_KEY="your-pinecone-api-key"
export PINECONE_INDEX="sheldonbrain-rag"

# Run the API
python3 rag_api_gemini.py
```

The API will start on `http://localhost:8080`

---

## 🚀 Deployment

### Google Cloud Run

```bash
# Deploy using the provided script
chmod +x deploy-cloud-run-gemini.sh
./deploy-cloud-run-gemini.sh YOUR_PROJECT_ID
```

### Docker

```bash
# Build image
docker build -f Dockerfile.gemini -t rag-api-gemini .

# Run container
docker run -p 8080:8080 \
  -e GOOGLE_API_KEY="your-key" \
  -e PINECONE_API_KEY="your-key" \
  -e PINECONE_INDEX="sheldonbrain-rag" \
  rag-api-gemini
```

---

## 📡 API Endpoints

### `GET /health`

Health check and system statistics.

**Response:**
```json
{
  "status": "healthy",
  "service": "rag-api-gemini",
  "embedding_model": "Gemini text-embedding-004",
  "vector_count": 105,
  "index": "sheldonbrain-rag",
  "namespace": "baseline",
  "timestamp": "2026-01-02T16:30:00Z"
}
```

### `POST /query`

Semantic search over stored insights.

**Request:**
```json
{
  "query": "What is the Governance Unified Theory?",
  "top_k": 5,
  "filter": {
    "sphere": "S144"
  }
}
```

**Response:**
```json
{
  "memories": [
    {
      "id": "vec_abc123",
      "score": 0.87,
      "text": "The Governance Unified Theory (GUT)...",
      "metadata": {
        "source": "Claude",
        "sphere": "S144",
        "novelty": 0.95
      }
    }
  ],
  "query_time_ms": 342.5,
  "count": 5
}
```

### `POST /store`

Store new insight in the memory substrate.

**Request:**
```json
{
  "text": "New insight about zero erasure...",
  "metadata": {
    "source": "Gemini",
    "sphere": "S042",
    "novelty": 0.92,
    "category": "Meta-cognition"
  }
}
```

**Response:**
```json
{
  "id": "vec_xyz789",
  "status": "stored",
  "vector_count": 106
}
```