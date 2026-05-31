# 🧠 Multi-AI Persistent Memory System (Sheldonbrain RAG API)

**Version:** 2.1 (Gemini Embeddings + Governed Memory)  
**Status:** ✅ Production Ready / Product Spine Active  
**Backup:** 100% Complete (105/105 vectors)

A production-ready RAG (Retrieval-Augmented Generation) API powered by Google Gemini embeddings and Pinecone vector database, enabling persistent memory across multiple AI instances.

---

## Product Spine

Sheldonbrain is more than a vector-search wrapper. It is being shaped into a trusted multi-agent memory substrate with provenance, ontology, lifecycle controls, and explicit execution boundaries.

Read the product spine: [`docs/OPENAI_PRODUCT_SPINE.md`](docs/OPENAI_PRODUCT_SPINE.md)

OpenAI-style agent contract: [`docs/OPENAI_AGENT_TOOL_CONTRACT.md`](docs/OPENAI_AGENT_TOOL_CONTRACT.md)

Machine-readable API contract: [`docs/openapi.yaml`](docs/openapi.yaml)

Governance contract tests: [`tests/test_governance_contract.py`](tests/test_governance_contract.py)

Core product invariant:

```text
Nothing disappears silently.
Nothing becomes canon without provenance.
Nothing executes merely because it was remembered.
```

Operational boundary:

```text
memory != permission
```

---

## Knowledge Graph Foundation

The repo now includes the first knowledge-graph substrate for source-grounded OpenAI integration:

- Clipboard / source inventory: [`archive/knowledge_graph/KG_SOURCE_INVENTORY_2026-05-24.yaml`](archive/knowledge_graph/KG_SOURCE_INVENTORY_2026-05-24.yaml)
- Node and edge schema: [`archive/knowledge_graph/KG_NODE_EDGE_SCHEMA_v0.1.yaml`](archive/knowledge_graph/KG_NODE_EDGE_SCHEMA_v0.1.yaml)
- OpenAI graph extraction spec: [`archive/knowledge_graph/OPENAI_GRAPH_EXTRACTION_AGENT_SPEC_v0.1.md`](archive/knowledge_graph/OPENAI_GRAPH_EXTRACTION_AGENT_SPEC_v0.1.md)
- Claude counter-review queue: [`archive/knowledge_graph/review_queues/CLAUDE_COUNTER_REVIEW_QUEUE_2026-05-24.md`](archive/knowledge_graph/review_queues/CLAUDE_COUNTER_REVIEW_QUEUE_2026-05-24.md)
- Rootglass source packet manifests: [`archive/knowledge_graph/source_packet_manifests/ROOTGLASS_SOURCE_PACKET_MANIFESTS_v0.1.yaml`](archive/knowledge_graph/source_packet_manifests/ROOTGLASS_SOURCE_PACKET_MANIFESTS_v0.1.yaml)

Knowledge-graph doctrine:

```text
The graph is not memory.
The graph is not canon.
The graph is not authority.
The graph is a receipt-indexed map of what exists, what it claims, what supports it, what contradicts it, and what still needs review.
```

---

## 🎯 Overview

This system solves **AI context amnesia** by providing a shared, persistent memory substrate that multiple AI agents (Claude, Gemini, GPT, Grok, etc.) can query and update. Every insight stored is preserved through governed lifecycle states rather than silently erased.

### Key Features

- ✅ **Gemini text-embedding-004** (768 dimensions)
- ✅ **Pinecone vector database** (baseline namespace)
- ✅ **Flask REST API** with CORS support
- ✅ **Dual redundancy** (Pinecone + Notion backup)
- ✅ **Docker deployment** ready
- ✅ **Google Cloud Run** compatible
- ✅ **Lifecycle governance** (`archive`, `quarantine`, `supersede`, `redact_pointer`, `restore`)
- ✅ **Retrieval receipts** for query provenance
- ✅ **OpenAI-style tool contract** for schema-first agent integration
- ✅ **OpenAPI 3.1 contract** for SDK generation and validation
- ✅ **GitHub Actions governance tests** for memory lifecycle invariants
- ✅ **Source-grounded knowledge graph foundation** for raw source → parsed packet → claim → evidence → review → action workflows

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

## 🧪 Governance Tests

Run the non-network governance contract tests:

```bash
pytest tests/test_governance_contract.py -q
```

These tests protect the product-level invariants around lifecycle defaults, content hashes, non-destructive archival states, retrieval receipts, and the `memory != permission` boundary.

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

### `POST /lifecycle`

Apply a non-destructive lifecycle transition instead of hard deletion.

**Request:**
```json
{
  "id": "vec_xyz789",
  "operation": "archive",
  "reason": "Superseded by a corrected memory"
}
```

**Response:**
```json
{
  "id": "vec_xyz789",
  "status": "lifecycle_updated",
  "operation": "archive",
  "lifecycle": "archived",
  "hard_deleted": false
}
```
