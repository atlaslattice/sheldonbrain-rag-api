# Cloud Run Deployment Guide - RAG API Backup

**Purpose:** Deploy RAG API to Google Cloud Run as a backup/redundant endpoint  
**Primary Endpoint:** Manus-hosted (already live)  
**Backup Endpoint:** Cloud Run (this guide)  
**Deployment Time:** 5-10 minutes

---

## Why Deploy to Cloud Run?

### Redundancy Benefits
1. **99.95% SLA** - Enterprise-grade uptime
2. **Auto-scaling** - Handles traffic spikes automatically
3. **Global CDN** - Low latency worldwide
4. **Independent** - Not tied to Manus sandbox lifecycle
5. **Cost-effective** - Pay only for actual usage

### When to Use Each Endpoint

**Manus Endpoint (Primary):**
- Development and testing
- Rapid iteration
- Direct integration with Manus workflows
- When you need to modify code quickly

**Cloud Run Endpoint (Backup):**
- Production workloads
- Public-facing integrations
- When Manus sandbox is hibernating
- Long-term persistence guarantee

---

## Prerequisites

✅ Google Cloud account (you're authenticated)  
✅ GitHub repository with RAG API code  
✅ API keys (Pinecone + OpenAI)  
✅ `gcloud` CLI installed and authenticated

---

## Deployment Method 1: Google Cloud Console (Easiest)

### Step 1: Open Cloud Run
1. Go to https://console.cloud.google.com/run
2. Click "Create Service"

### Step 2: Configure Container
**Option A: Deploy from GitHub**
1. Select "Continuously deploy from a repository"
2. Click "Set up with Cloud Build"
3. Connect GitHub account
4. Select repository: `atlaslattice/sheldonbrain-rag-api`
5. Branch: `main` or `master`
6. Build type: Dockerfile
7. Dockerfile path: `/Dockerfile`

**Option B: Deploy from Container Registry**
1. Select "Deploy one revision from an existing container image"
2. Use pre-built image (if available)

### Step 3: Configure Service
**Service name:** `sheldonbrain-rag-api`  
**Region:** `us-central1` (or closest to you)  
**CPU allocation:** CPU is only allocated during request processing  
**Minimum instances:** 0 (scales to zero when not used)  
**Maximum instances:** 10  

**Authentication:** Allow unauthenticated invocations (public API)

### Step 4: Set Environment Variables
Click "Container, Variables & Secrets, Connections, Security"

Add these variables:
```
PINECONE_API_KEY = [your pinecone key]
OPENAI_API_KEY = [your openai key]
PINECONE_INDEX = sheldonbrain-rag
PORT = 8080
```

### Step 5: Deploy
1. Click "Create"
2. Wait 2-3 minutes for deployment
3. Copy the service URL (looks like: `https://sheldonbrain-rag-api-[hash]-uc.a.run.app`)

### Step 6: Test
```bash
# Health check
curl https://[your-cloud-run-url]/health

# Query test
curl -X POST https://[your-cloud-run-url]/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is GUT?", "top_k": 3}'
```

---

## Deployment Method 2: gcloud CLI (Automated)

### Step 1: Navigate to Project
```bash
cd ~/rag-api
```

### Step 2: Set Project
```bash
# List available projects
gcloud projects list

# Set active project
gcloud config set project [YOUR_PROJECT_ID]
```

### Step 3: Enable Required APIs
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### Step 4: Build Container
```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/[PROJECT_ID]/sheldonbrain-rag-api
```

### Step 5: Deploy to Cloud Run
```bash
gcloud run deploy sheldonbrain-rag-api \
  --image gcr.io/[PROJECT_ID]/sheldonbrain-rag-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars PINECONE_API_KEY=[your_key],OPENAI_API_KEY=[your_key],PINECONE_INDEX=sheldonbrain-rag,PORT=8080 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10
```

### Step 6: Get Service URL
```bash
gcloud run services describe sheldonbrain-rag-api \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
```

---

## Deployment Method 3: Cloud Build Trigger (CI/CD)

### Step 1: Create cloudbuild.yaml
Already exists in the repo at `/home/ubuntu/rag-api/cloudbuild.yaml`:

```yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/sheldonbrain-rag-api', '.']
  
  # Push the container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/sheldonbrain-rag-api']
  
  # Deploy container image to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'sheldonbrain-rag-api'
      - '--image'
      - 'gcr.io/$PROJECT_ID/sheldonbrain-rag-api'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'

images:
  - 'gcr.io/$PROJECT_ID/sheldonbrain-rag-api'
```

### Step 2: Create Build Trigger
```bash
gcloud builds triggers create github \
  --repo-name=sheldonbrain-rag-api \
  --repo-owner=atlaslattice \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml
```

### Step 3: Set Environment Variables in Cloud Run
```bash
gcloud run services update sheldonbrain-rag-api \
  --update-env-vars PINECONE_API_KEY=[your_key],OPENAI_API_KEY=[your_key],PINECONE_INDEX=sheldonbrain-rag \
  --region us-central1
```

**Now every push to `main` branch auto-deploys!**

---

## Post-Deployment Configuration

### 1. Set Up Custom Domain (Optional)
```bash
# Map custom domain
gcloud run domain-mappings create \
  --service sheldonbrain-rag-api \
  --domain rag.yourdomain.com \
  --region us-central1
```

### 2. Configure CORS (if needed)
Already configured in the Flask app:
```python
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE')
    return response
```

### 3. Set Up Monitoring
```bash
# View logs
gcloud run services logs read sheldonbrain-rag-api \
  --region us-central1 \
  --limit 50

# View metrics in Cloud Console
# Go to: Cloud Run > sheldonbrain-rag-api > Metrics
```

### 4. Configure Alerts
In Cloud Console:
1. Go to Monitoring > Alerting
2. Create alert for:
   - Request latency > 1s
   - Error rate > 5%
   - CPU utilization > 80%

---

## Updating the Deployment

### Method 1: Redeploy from Console
1. Go to Cloud Run service
2. Click "Edit & Deploy New Revision"
3. Update environment variables or image
4. Click "Deploy"

### Method 2: Update via CLI
```bash
# Update environment variables
gcloud run services update sheldonbrain-rag-api \
  --update-env-vars NEW_VAR=value \
  --region us-central1

# Deploy new image
gcloud run deploy sheldonbrain-rag-api \
  --image gcr.io/[PROJECT_ID]/sheldonbrain-rag-api:latest \
  --region us-central1
```

### Method 3: Push to GitHub (if CI/CD enabled)
```bash
cd ~/rag-api
git add .
git commit -m "Update RAG API"
git push origin main
# Auto-deploys via Cloud Build trigger
```

---

## Cost Estimation

### Cloud Run Pricing (as of 2026)
**Free tier (per month):**
- 2 million requests
- 360,000 GB-seconds of memory
- 180,000 vCPU-seconds

**Paid tier:**
- $0.40 per million requests
- $0.00002400 per GB-second
- $0.00001000 per vCPU-second

### Example Usage Scenarios

**Low usage (testing):**
- 10,000 requests/month
- Average 200ms response time
- **Cost: $0** (within free tier)

**Medium usage (active development):**
- 100,000 requests/month
- Average 300ms response time
- **Cost: ~$2-5/month**

**High usage (production):**
- 1 million requests/month
- Average 500ms response time
- **Cost: ~$20-30/month**

**Note:** Pinecone and OpenAI have separate costs

---

## Troubleshooting

### Issue: Deployment fails with "Permission denied"
**Solution:**
```bash
gcloud projects add-iam-policy-binding [PROJECT_ID] \
  --member="serviceAccount:[PROJECT_NUMBER]-compute@developer.gserviceaccount.com" \
  --role="roles/run.admin"
```

### Issue: Container fails to start
**Check logs:**
```bash
gcloud run services logs read sheldonbrain-rag-api \
  --region us-central1 \
  --limit 100
```

**Common causes:**
- Missing environment variables
- Invalid API keys
- Port mismatch (ensure PORT=8080)

### Issue: 502 Bad Gateway
**Causes:**
- Container taking too long to start
- Application crashing on startup
- Invalid Dockerfile

**Solution:**
- Increase startup timeout
- Check application logs
- Test Dockerfile locally first

### Issue: High latency
**Solutions:**
- Enable minimum instances (prevents cold starts)
- Increase CPU allocation
- Use Cloud CDN for caching
- Deploy to multiple regions

---

## Maintenance

### Regular Tasks

**Weekly:**
- Check error logs
- Review usage metrics
- Verify API key validity

**Monthly:**
- Review cost reports
- Update dependencies
- Test backup/restore procedures

**Quarterly:**
- Security audit
- Performance optimization
- Capacity planning

### Backup Strategy

**Database (Pinecone):**
- Pinecone handles backups automatically
- Export vectors periodically for safety

**Code (GitHub):**
- Already backed up in version control
- Create release tags for stable versions

**Configuration:**
- Document environment variables
- Store secrets in Secret Manager (not env vars)

---

## Security Best Practices

### 1. Use Secret Manager
```bash
# Store secrets
echo -n "your-api-key" | gcloud secrets create pinecone-api-key \
  --data-file=-

# Grant access to Cloud Run
gcloud secrets add-iam-policy-binding pinecone-api-key \
  --member="serviceAccount:[PROJECT_NUMBER]-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Update Cloud Run to use secret
gcloud run services update sheldonbrain-rag-api \
  --update-secrets PINECONE_API_KEY=pinecone-api-key:latest \
  --region us-central1
```

### 2. Enable VPC Connector (Optional)
For private database access:
```bash
gcloud compute networks vpc-access connectors create rag-connector \
  --network default \
  --region us-central1 \
  --range 10.8.0.0/28

gcloud run services update sheldonbrain-rag-api \
  --vpc-connector rag-connector \
  --region us-central1
```

### 3. Implement Rate Limiting
Add to Flask app:
```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["100 per minute"]
)
```

---

## Comparison: Manus vs Cloud Run

| Feature | Manus Endpoint | Cloud Run |
|---------|---------------|-----------|
| **Uptime** | Tied to sandbox | 99.95% SLA |
| **Cost** | Included | Pay-per-use |
| **Setup Time** | Instant | 5-10 min |
| **Scalability** | Single instance | Auto-scaling |
| **Latency** | ~50ms | ~100ms |
| **Persistence** | Project lifecycle | Permanent |
| **Updates** | Instant | 2-3 min deploy |
| **Monitoring** | Basic logs | Full metrics |
| **Custom Domain** | No | Yes |
| **Global CDN** | No | Yes |

**Recommendation:** Use both!
- **Manus:** Development, testing, rapid iteration
- **Cloud Run:** Production, public integrations, long-term persistence

---

## Next Steps

1. **Deploy to Cloud Run** using Method 1 (Console - easiest)
2. **Test both endpoints** (Manus + Cloud Run)
3. **Update integration docs** with both URLs
4. **Configure monitoring** and alerts
5. **Set up CI/CD** for automatic deployments

**The redundancy ensures the organism never loses memory.** 🧠✨

---

**End of Guide**

*Prepared by Manus on January 1, 2026*  
*For: Multi-AI Persistent Memory System*  
*Status: Ready for deployment*
