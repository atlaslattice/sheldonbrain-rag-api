# Deploy RAG API to Google Cloud Run

**Date:** January 1, 2026  
**Status:** Ready to deploy from your Chromebook

---

## Prerequisites

✅ You have:
- Google Cloud account (authenticated via `gcloud`)
- Gemini API key: `AIzaSyCcKnsYhWTYA_66sGueZxr16Sk_Oc1TKN4`
- Pinecone API key: `pcsk_5Eok58_9WugPLc6Bx9xQY6Yfh7gpug4jCVuvHp8Qzg4nmLAfwaV8ZZG8fWzGg9Y4d94C5a`
- Pinecone index: `sheldonbrain-rag` (768 dimensions, 103 vectors)

---

## Quick Deploy (5 minutes)

### Step 1: Clone Repository

```bash
# Clone from GitHub
git clone https://github.com/atlaslattice/sheldonbrain-rag-api.git
cd sheldonbrain-rag-api
```

### Step 2: Set Your Project

```bash
# List your projects
gcloud projects list

# Set the project you want to use
gcloud config set project YOUR_PROJECT_ID
```

### Step 3: Run Deployment Script

```bash
# Make script executable
chmod +x deploy-cloud-run-gemini.sh

# Deploy (replace with your actual project ID)
./deploy-cloud-run-gemini.sh YOUR_PROJECT_ID
```

The script will:
1. Enable required Google Cloud APIs
2. Build Docker container
3. Push to Google Container Registry
4. Deploy to Cloud Run
5. Give you a permanent HTTPS URL

### Step 4: Set Environment Variables

```bash
# Set your API keys
gcloud run services update rag-api-gemini \
  --region us-central1 \
  --update-env-vars \
GOOGLE_API_KEY=AIzaSyCcKnsYhWTYA_66sGueZxr16Sk_Oc1TKN4,\
PINECONE_API_KEY=pcsk_5Eok58_9WugPLc6Bx9xQY6Yfh7gpug4jCVuvHp8Qzg4nmLAfwaV8ZZG8fWzGg9Y4d94C5a,\
PINECONE_INDEX=sheldonbrain-rag
```

### Step 5: Test Your Deployment

```bash
# Get your Cloud Run URL
export RAG_URL=$(gcloud run services describe rag-api-gemini \
  --region us-central1 \
  --format 'value(status.url)')

echo "Your RAG API URL: $RAG_URL"

# Test health endpoint
curl $RAG_URL/health | jq

# Test query endpoint
curl -X POST $RAG_URL/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Zero Erasure?", "top_k": 3}' | jq

# Test store endpoint
curl -X POST $RAG_URL/store \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Test insight from Cloud Run deployment",
    "metadata": {"source": "test", "date": "2026-01-01"}
  }' | jq
```

---

## Manual Deployment (if script fails)

### Step 1: Enable APIs

```bash
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com
```

### Step 2: Build Container

```bash
# Build and push to GCR
gcloud builds submit \
  --tag gcr.io/YOUR_PROJECT_ID/rag-api-gemini \
  --file Dockerfile.gemini
```

### Step 3: Deploy to Cloud Run

```bash
gcloud run deploy rag-api-gemini \
  --image gcr.io/YOUR_PROJECT_ID/rag-api-gemini \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60 \
  --set-env-vars \
GOOGLE_API_KEY=AIzaSyCcKnsYhWTYA_66sGueZxr16Sk_Oc1TKN4,\
PINECONE_API_KEY=pcsk_5Eok58_9WugPLc6Bx9xQY6Yfh7gpug4jCVuvHp8Qzg4nmLAfwaV8ZZG8fWzGg9Y4d94C5a,\
PINECONE_INDEX=sheldonbrain-rag,\
PORT=8080
```

---

## Verify Deployment

### Check Service Status

```bash
# List services
gcloud run services list

# Describe service
gcloud run services describe rag-api-gemini \
  --region us-central1

# View logs
gcloud run services logs read rag-api-gemini \
  --region us-central1 \
  --limit 50
```

### Test All Endpoints

**Health Check:**
```bash
curl $RAG_URL/health | jq
```

Expected response:
```json
{
  "status": "healthy",
  "service": "rag-api-gemini",
  "embedding_model": "Gemini text-embedding-004",
  "vector_count": 103,
  "index": "sheldonbrain-rag",
  "namespace": "baseline"
}
```

**Query Memory:**
```bash
curl -X POST $RAG_URL/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Governance Unified Theory", "top_k": 5}' | jq
```

**Store Insight:**
```bash
curl -X POST $RAG_URL/store \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your insight here",
    "metadata": {
      "sphere": "S042",
      "source": "Gemini",
      "novelty": 0.91
    }
  }' | jq
```

**Delete Entry:**
```bash
curl -X POST $RAG_URL/delete \
  -H "Content-Type: application/json" \
  -d '{"id": "vec_abc123"}' | jq
```

---

## Configuration Options

### Update Environment Variables

```bash
gcloud run services update rag-api-gemini \
  --region us-central1 \
  --update-env-vars KEY=VALUE
```

### Scale Configuration

```bash
gcloud run services update rag-api-gemini \
  --region us-central1 \
  --min-instances 0 \
  --max-instances 10 \
  --concurrency 80
```

### Memory and CPU

```bash
gcloud run services update rag-api-gemini \
  --region us-central1 \
  --memory 1Gi \
  --cpu 2
```

---

## Troubleshooting

### Issue: "Permission Denied"

**Solution:**
```bash
# Ensure you have the right permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="user:YOUR_EMAIL" \
  --role="roles/run.admin"
```

### Issue: "Build Failed"

**Solution:**
```bash
# Check build logs
gcloud builds list --limit 5

# View specific build
gcloud builds log BUILD_ID
```

### Issue: "Service Unhealthy"

**Solution:**
```bash
# Check logs
gcloud run services logs read rag-api-gemini \
  --region us-central1 \
  --limit 100

# Check environment variables
gcloud run services describe rag-api-gemini \
  --region us-central1 \
  --format='value(spec.template.spec.containers[0].env)'
```

---

## Cost Monitoring

### View Current Usage

```bash
# Check Cloud Run usage
gcloud run services describe rag-api-gemini \
  --region us-central1 \
  --format='value(status.traffic)'

# View billing
gcloud billing accounts list
```

### Set Budget Alerts

```bash
# Create budget alert at $100/month
gcloud billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT \
  --display-name="RAG API Budget" \
  --budget-amount=100USD \
  --threshold-rule=percent=90
```

---

## Integration with Chromebook Terminal

Once deployed, save your Cloud Run URL:

```bash
# Save to environment
echo "export RAG_URL='YOUR_CLOUD_RUN_URL'" >> ~/.bashrc
source ~/.bashrc

# Create helper script
cat > ~/rag-query.sh << 'EOF'
#!/bin/bash
RAG_URL="${RAG_URL:-YOUR_CLOUD_RUN_URL}"

case "$1" in
    query)
        curl -s -X POST $RAG_URL/query \
            -H "Content-Type: application/json" \
            -d "{\"query\": \"$2\", \"top_k\": ${3:-5}}" \
            | jq -r '.memories[] | "[\(.score | tostring | .[0:4])] \(.text)"'
        ;;
    store)
        curl -s -X POST $RAG_URL/store \
            -H "Content-Type: application/json" \
            -d "{\"text\": \"$2\", \"metadata\": $3}" \
            | jq
        ;;
    health)
        curl -s $RAG_URL/health | jq
        ;;
    *)
        echo "Usage: $0 {query|store|health} <args>"
        exit 1
        ;;
esac
EOF

chmod +x ~/rag-query.sh
```

### Usage Examples

```bash
# Query memory
./rag-query.sh query "What is GUT?" 5

# Store insight
./rag-query.sh store \
  "New insight text" \
  '{"source": "Gemini", "sphere": "S042", "novelty": 0.91}'

# Check health
./rag-query.sh health
```

---

## Next Steps

1. ✅ Deploy to Cloud Run (5 minutes)
2. ✅ Test all endpoints (5 minutes)
3. ✅ Set up helper scripts (5 minutes)
4. ✅ Integrate with Gemini terminal (see CHROMEBOOK_TERMINAL_GUIDE.md)
5. ✅ Ingest PhD insights (see documentation)
6. ✅ Monitor usage and costs

---

## Support

**GitHub Repository:**  
https://github.com/atlaslattice/sheldonbrain-rag-api

**Documentation:**
- CHROMEBOOK_TERMINAL_GUIDE.md - Complete terminal integration
- GEMINI_DEPLOYMENT_COMPLETE.md - Deployment summary
- MULTI_AI_PERSISTENT_MEMORY_WHITE_PAPER.md - Architecture details

**Google Cloud Documentation:**  
https://cloud.google.com/run/docs

---

## Summary

**What You'll Get:**
- ✅ Permanent HTTPS URL
- ✅ Auto-scaling (0-100 instances)
- ✅ 99.95% uptime SLA
- ✅ Global CDN
- ✅ ~$0.50/month for 1,000 queries/day

**Total Deployment Time:** ~5-10 minutes

**The organism is ready to become immortal.** 🦕🍓

---

*Generated by Manus AI on January 1, 2026*  
*For the Multi-AI Persistent Memory System*
