# Chromebook Terminal Integration Guide
## RAG API with Gemini Embeddings

**Date:** January 1, 2026  
**Purpose:** Enable Gemini terminal on Chromebook to query persistent memory  
**Status:** ✅ Ready to deploy

---

## Overview

This guide shows you how to integrate the RAG API (now powered by Gemini embeddings!) with your Chromebook terminal, enabling persistent memory across all AI sessions.

**What This Enables:**
- Gemini queries shared memory before responding
- Knowledge persists across terminal sessions
- Cross-AI synthesis (Claude, Grok, Gemini, GPT, Manus)
- Zero session reset costs

---

## Architecture

```
┌─────────────────────────────────────────┐
│   RAG API (Cloud Run)                    │
│   • Gemini embeddings (768-dim)         │
│   • Pinecone vector database            │
│   • Flask REST API                      │
└──────────────┬──────────────────────────┘
               │
      ┌────────┼────────┬────────┐
      ↓        ↓        ↓        ↓
  Chromebook Claude   Grok    Manus
  Terminal
```

---

## Prerequisites

✅ **You have:**
- Chromebook with terminal access
- Google Cloud account (authenticated)
- Gemini API key: `AIzaSyCcKnsYhWTYA_66sGueZxr16Sk_Oc1TKN4`
- Pinecone account (or will create one)

---

## Step 1: Deploy RAG API to Cloud Run

### 1.1 Get Your Google Cloud Project ID

```bash
# List your projects
gcloud projects list

# Set the project you want to use
gcloud config set project YOUR_PROJECT_ID
```

### 1.2 Clone the Repository

```bash
# Clone from GitHub
git clone https://github.com/atlaslattice/sheldonbrain-rag-api.git
cd sheldonbrain-rag-api
```

### 1.3 Deploy to Cloud Run

```bash
# Run the deployment script
./deploy-cloud-run-gemini.sh YOUR_PROJECT_ID

# This will:
# 1. Enable required APIs
# 2. Build Docker container
# 3. Deploy to Cloud Run
# 4. Give you a permanent URL
```

**Expected output:**
```
✅ Deployment complete!

📍 Service URL: https://rag-api-gemini-[hash].run.app
```

### 1.4 Set Environment Variables

```bash
# Set your API keys
gcloud run services update rag-api-gemini \
  --region us-central1 \
  --update-env-vars \
GOOGLE_API_KEY=AIzaSyCcKnsYhWTYA_66sGueZxr16Sk_Oc1TKN4,\
PINECONE_API_KEY=your_pinecone_key,\
PINECONE_INDEX=sheldonbrain-rag
```

**Note:** You'll need a Pinecone API key. Get one at: https://www.pinecone.io/

---

## Step 2: Test the Deployment

### 2.1 Health Check

```bash
# Replace with your actual Cloud Run URL
export RAG_URL="https://rag-api-gemini-[hash].run.app"

# Test health endpoint
curl $RAG_URL/health | jq
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "rag-api-gemini",
  "embedding_model": "Gemini text-embedding-004",
  "vector_count": 102,
  "index": "sheldonbrain-rag",
  "namespace": "baseline"
}
```

### 2.2 Store an Insight

```bash
# Store a test insight
curl -X POST $RAG_URL/store \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Governance Unified Theory: G = I / C where G is governance effectiveness, I is information flow, and C is thermodynamic cost",
    "metadata": {
      "sphere": "S025",
      "source": "Claude",
      "novelty": 0.97,
      "date": "2026-01-01"
    }
  }' | jq
```

**Expected response:**
```json
{
  "id": "vec_abc123xyz",
  "status": "stored",
  "vector_count": 103
}
```

### 2.3 Query the Memory

```bash
# Query for GUT
curl -X POST $RAG_URL/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the Governance Unified Theory?",
    "top_k": 3
  }' | jq
```

**Expected response:**
```json
{
  "memories": [
    {
      "id": "vec_abc123xyz",
      "score": 0.89,
      "text": "Governance Unified Theory: G = I / C...",
      "metadata": {
        "sphere": "S025",
        "source": "Claude",
        "novelty": 0.97
      }
    }
  ],
  "query_time_ms": 87.3,
  "count": 1
}
```

---

## Step 3: Integrate with Gemini Terminal

### 3.1 Create Helper Script

Create a file `~/rag-query.sh`:

```bash
#!/bin/bash
# RAG Query Helper for Gemini Terminal

RAG_URL="https://rag-api-gemini-[hash].run.app"

query_memory() {
    local query="$1"
    local top_k="${2:-5}"
    
    curl -s -X POST $RAG_URL/query \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\", \"top_k\": $top_k}" \
        | jq -r '.memories[] | "[\(.score | tostring | .[0:4])] \(.text)"'
}

store_memory() {
    local text="$1"
    local metadata="$2"
    
    curl -s -X POST $RAG_URL/store \
        -H "Content-Type: application/json" \
        -d "{\"text\": \"$text\", \"metadata\": $metadata}" \
        | jq
}

# Main command
case "$1" in
    query)
        query_memory "$2" "$3"
        ;;
    store)
        store_memory "$2" "$3"
        ;;
    *)
        echo "Usage: $0 {query|store} <text> [options]"
        exit 1
        ;;
esac
```

Make it executable:
```bash
chmod +x ~/rag-query.sh
```

### 3.2 Usage Examples

**Query before responding:**
```bash
# Check what we know about GUT
./rag-query.sh query "Governance Unified Theory" 5

# Output:
# [0.89] Governance Unified Theory: G = I / C where...
# [0.76] Zero Erasure principle extends GUT to...
# [0.71] Cross-sphere synthesis reveals...
```

**Store new insights:**
```bash
# Store a new discovery
./rag-query.sh store \
  "Gemini integration enables 768-dimensional embeddings with lower latency than OpenAI" \
  '{"sphere": "S015", "source": "Gemini", "novelty": 0.91}'
```

### 3.3 Integrate with Gemini Workflow

**Option A: Manual Query (Recommended to Start)**

Before asking Gemini a question, query the RAG:
```bash
# 1. Query memory
./rag-query.sh query "your question here"

# 2. Read the context

# 3. Ask Gemini with that context
gemini "Given this context: [paste results], answer: your question"
```

**Option B: Automated Wrapper (Advanced)**

Create `~/gemini-with-memory.sh`:
```bash
#!/bin/bash
# Gemini with RAG Memory

QUESTION="$1"

# Query RAG first
echo "🧠 Querying shared memory..."
CONTEXT=$(./rag-query.sh query "$QUESTION" 3)

# Build prompt with context
PROMPT="Context from shared memory:
$CONTEXT

Question: $QUESTION

Please answer using the context above, and if you discover new insights, let me know so I can store them."

# Call Gemini
gemini "$PROMPT"
```

Usage:
```bash
./gemini-with-memory.sh "What is the Zero Erasure principle?"
```

---

## Step 4: Cross-AI Integration

### 4.1 Store Insights from All AIs

**From Claude:**
```bash
# After Claude generates an insight
./rag-query.sh store \
  "Claude's insight text here" \
  '{"source": "Claude", "sphere": "S025", "novelty": 0.94}'
```

**From Grok:**
```bash
# After Grok generates an insight
./rag-query.sh store \
  "Grok's insight text here" \
  '{"source": "Grok", "sphere": "S015", "novelty": 0.92}'
```

**From Gemini (You):**
```bash
# After you discover something
./rag-query.sh store \
  "Your insight text here" \
  '{"source": "Gemini", "sphere": "S042", "novelty": 0.89}'
```

### 4.2 Query Across All AIs

```bash
# See what all AIs know about a topic
./rag-query.sh query "Zero Erasure" 10

# Filter by source
curl -X POST $RAG_URL/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "governance",
    "top_k": 5,
    "filter": {"source": "Claude"}
  }' | jq
```

---

## Step 5: Advanced Features

### 5.1 Sphere-Specific Queries

```bash
# Query specific sphere
curl -X POST $RAG_URL/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "physics principles",
    "top_k": 5,
    "filter": {"sphere": "S015"}
  }' | jq
```

### 5.2 Novelty Filtering

```bash
# Only high-novelty insights (> 0.9)
curl -X POST $RAG_URL/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "breakthrough discoveries",
    "top_k": 10,
    "filter": {"novelty": {"$gte": 0.9}}
  }' | jq
```

### 5.3 Temporal Queries

```bash
# Insights from today
curl -X POST $RAG_URL/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "recent discoveries",
    "top_k": 10,
    "filter": {"date": "2026-01-01"}
  }' | jq
```

---

## Troubleshooting

### Issue: "Invalid API Key"

**Solution:**
```bash
# Check your environment variables
gcloud run services describe rag-api-gemini \
  --region us-central1 \
  --format='value(spec.template.spec.containers[0].env)'

# Update if needed
gcloud run services update rag-api-gemini \
  --region us-central1 \
  --update-env-vars GOOGLE_API_KEY=your_key
```

### Issue: "Connection Refused"

**Solution:**
```bash
# Check if service is running
gcloud run services list

# Check logs
gcloud run services logs read rag-api-gemini \
  --region us-central1 \
  --limit 50
```

### Issue: "No Results Found"

**Solution:**
```bash
# Check vector count
curl $RAG_URL/health | jq '.vector_count'

# If 0, you need to ingest data first
# See Step 2.2 for storing insights
```

---

## Performance Tips

### 1. Batch Queries

Instead of querying for every message, query once at session start:
```bash
# Get general context at session start
./rag-query.sh query "summary of all knowledge" 20 > /tmp/session-context.txt

# Reference throughout session
cat /tmp/session-context.txt
```

### 2. Cache Common Queries

```bash
# Create a cache directory
mkdir -p ~/.rag-cache

# Cache function
cache_query() {
    local query="$1"
    local cache_file="~/.rag-cache/$(echo $query | md5sum | cut -d' ' -f1)"
    
    if [ -f "$cache_file" ] && [ $(find "$cache_file" -mmin -60) ]; then
        cat "$cache_file"
    else
        ./rag-query.sh query "$query" | tee "$cache_file"
    fi
}
```

### 3. Async Storage

Store insights asynchronously to avoid blocking:
```bash
# Store in background
./rag-query.sh store "insight text" '{"metadata": "here"}' &
```

---

## Cost Analysis

### Gemini Embeddings

**Model:** text-embedding-004  
**Dimensions:** 768  
**Cost:** $0.00001 per 1,000 characters

**Example:**
- 1,000 insights × 500 chars each = 500,000 chars
- Cost: $0.005 (half a cent!)

### Cloud Run

**Pricing:**
- CPU: $0.00002400 per vCPU-second
- Memory: $0.00000250 per GiB-second
- Requests: First 2M free, then $0.40 per million

**Example (1,000 queries/day):**
- ~30,000 queries/month
- Cost: ~$0.50/month

### Pinecone

**Pricing:**
- Starter: $70/month (100K vectors)
- Standard: $280/month (1M vectors)

**Total Monthly Cost:**
- Gemini: ~$0.01
- Cloud Run: ~$0.50
- Pinecone: $70
- **Total: ~$70.51/month**

---

## Next Steps

### Immediate
1. ✅ Deploy to Cloud Run
2. ✅ Test health endpoint
3. ✅ Store first insight
4. ✅ Query and validate

### This Week
1. Integrate with Gemini terminal workflow
2. Store all 25 PhD insights from Claude
3. Test cross-AI queries
4. Optimize query patterns

### This Month
1. Build automated ingestion pipeline
2. Create Notion → RAG sync
3. Implement advanced filtering
4. Scale to 1,000+ insights

---

## Resources

**GitHub Repository:**  
https://github.com/atlaslattice/sheldonbrain-rag-api

**Cloud Run Documentation:**  
https://cloud.google.com/run/docs

**Gemini API Documentation:**  
https://ai.google.dev/docs

**Pinecone Documentation:**  
https://docs.pinecone.io/

**Support:**  
Create an issue in the GitHub repository

---

## Summary

You now have:
- ✅ RAG API with Gemini embeddings
- ✅ Deployment script for Cloud Run
- ✅ Helper scripts for terminal integration
- ✅ Cross-AI memory sharing
- ✅ Advanced query capabilities

**The organism is operational. The memory is persistent. The knowledge compounds.**

🦕🍓 **Welcome to persistent memory!**

---

*Generated by Manus AI on January 1, 2026*  
*For the Multi-AI Persistent Memory System*
