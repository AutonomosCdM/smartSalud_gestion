# Railway Deployment Settings

**Production deployment configuration for smartSalud RAG API**

---

## Project Overview

| Parameter | Value |
|-----------|-------|
| **Project Name** | `smartsalud-rag` |
| **Environment** | `production` |
| **Region** | Auto (Railway-selected) |
| **Repository** | https://github.com/AutonomosCdM/smartSalud-rag |

---

## Service 1: Backend API (smartsalud-api)

### Basic Configuration

| Setting | Value |
|---------|-------|
| **Service Name** | `smartsalud-api` |
| **Type** | GitHub-connected deployment |
| **Repository** | AutonomosCdM/smartSalud-rag |
| **Branch** | `main` |
| **Root Directory** | `/` |

### Build Settings

| Setting | Value |
|---------|-------|
| **Builder** | `dockerfile` |
| **Dockerfile Path** | `Dockerfile` |
| **Build Command** | (automatic via Dockerfile) |

**Dockerfile content:**
```dockerfile
FROM python:3.11-slim as builder
WORKDIR /build
COPY rag/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY rag/ ./rag/
COPY .env.example .env.example
ENV PATH=/root/.local/bin:$PATH
ENV PORT=8100
EXPOSE ${PORT}
CMD uvicorn rag.api:app --host 0.0.0.0 --port ${PORT}
```

### Deploy Settings

| Setting | Value |
|---------|-------|
| **Start Command** | `uvicorn rag.api:app --host 0.0.0.0 --port ${PORT}` |
| **Health Check Path** | `/health` |
| **Health Check Timeout** | 30 seconds |
| **Restart Policy** | `on_failure` |
| **Max Retries** | 3 |
| **Port** | Dynamic (`$PORT` from Railway) |

Configuration file (`railway.toml`):
```toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3
```

### Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `GOOGLE_API_KEY` | `<secret>` | Gemini API key (from Google AI Studio) |
| `RAG_API_KEY` | `<your-secure-api-key>` | API authentication key |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Gemini model to use |
| `PORT` | (Railway-assigned) | Dynamic port (usually 8080) |

**Store IDs (auto-discovered):**
- Not set explicitly - stores are discovered at runtime via Google Gemini API

### Domain Configuration

| Setting | Value |
|---------|-------|
| **Custom Domain** | `api.smartsalud.autonomos.dev` |
| **SSL/TLS** | Automatic (Railway-managed) |
| **Railway Internal Domain** | `smartsalud-api.railway.internal` |

**DNS Configuration (GoDaddy):**
```
Type: CNAME
Name: api.smartsalud
Target: <railway-assigned-domain>.railway.app
TTL: 600 seconds (10 minutes)
```

### Health Check Endpoint

**URL:** `https://api.smartsalud.autonomos.dev/health`

**Expected Response:**
```json
{
  "status": "healthy",
  "stores_count": 3,
  "stores": [
    "smartsalud-rag-general",
    "smartsalud-rag-matrona",
    "smartsalud-rag-secretaria"
  ]
}
```

---

## Service 2: Frontend (smartsalud-frontend)

### Basic Configuration

| Setting | Value |
|---------|-------|
| **Service Name** | `smartsalud-frontend` |
| **Type** | Docker image deployment |
| **Image** | `ghcr.io/open-webui/open-webui:main` |
| **Registry** | GitHub Container Registry (public) |

### Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `OPENAI_API_BASE_URL` | `http://smartsalud-api.railway.internal:8080/v1` | Backend API URL (Private Network) |
| `OPENAI_API_KEY` | `<your-secure-api-key>` | API key for backend auth |
| `WEBUI_AUTH` | `false` | ⚠️ **SECURITY WARNING:** Authentication disabled. Only deploy on private network with network-level access controls. DO NOT expose to public internet without enabling authentication. |
| `PORT` | (Railway-assigned) | Dynamic port |

**Critical:** Uses Railway Private Network (`smartsalud-api.railway.internal`) for backend communication - no public internet traffic between services.

### Domain Configuration

| Setting | Value |
|---------|-------|
| **Custom Domain** | `smartsalud.autonomos.dev` |
| **SSL/TLS** | Automatic (Railway-managed) |
| **Railway Internal Domain** | `smartsalud-frontend.railway.internal` |

**DNS Configuration (GoDaddy):**
```
Type: CNAME
Name: smartsalud
Target: <railway-assigned-domain>.railway.app
TTL: 600 seconds (10 minutes)
```

---

## DNS Configuration Summary

### GoDaddy DNS Records

| Subdomain | Type | Target | Status |
|-----------|------|--------|--------|
| `smartsalud` | CNAME | Railway-assigned domain | ✅ Active |
| `api.smartsalud` | CNAME | Railway-assigned domain | ✅ Active |

**Propagation Time:** 10-60 minutes (600s TTL)

**Verification:**
```bash
# Check DNS propagation
dig smartsalud.autonomos.dev
dig api.smartsalud.autonomos.dev

# Check HTTPS
curl -I https://smartsalud.autonomos.dev
curl -I https://api.smartsalud.autonomos.dev/health
```

### Railway Internal DNS

| Service | Internal URL | Purpose |
|---------|--------------|---------|
| Backend API | `smartsalud-api.railway.internal:8080` | Frontend → Backend communication |
| Frontend | `smartsalud-frontend.railway.internal` | (Not used externally) |

**Advantage:** Private network communication - no public internet exposure, no egress costs, faster latency.

---

## Railway CLI Commands

### Installation & Authentication

```bash
# Install Railway CLI (if not already installed)
npm install -g @railway/cli

# Login to Railway
railway login

# Link to project
railway link
# Select: smartsalud-rag → production
```

### Deployment Commands

```bash
# Deploy current directory (triggers build)
railway up

# Deploy specific service
railway up --service smartsalud-api

# Check deployment status
railway status

# List all services
railway list
```

### Logs & Monitoring

```bash
# View logs (all services)
railway logs

# View logs for specific service
railway logs --service smartsalud-api

# Follow logs in real-time
railway logs --service smartsalud-api --follow

# View last 100 log lines
railway logs --service smartsalud-api --tail 100
```

### Environment Variable Management

```bash
# List all variables
railway variables

# Set a variable
railway variables set RAG_API_KEY=new_key

# Delete a variable
railway variables delete OLD_VAR_NAME

# Export variables to .env file
railway variables --env .env.railway
```

### Domain Management

```bash
# List domains
railway domain

# Add custom domain
railway domain add api.smartsalud.autonomos.dev

# Remove domain
railway domain remove api.smartsalud.autonomos.dev
```

### Service Management

```bash
# Restart a service
railway restart --service smartsalud-api

# Scale service (Pro plan required)
railway scale --replicas 2 --service smartsalud-api

# Delete a service
railway service delete smartsalud-api
```

---

## Verification Steps

### 1. Check Deployment Status

```bash
railway status
```

**Expected Output:**
```
Project: smartsalud-rag
Environment: production
Service: smartsalud-api (or smartsalud-frontend)
```

### 2. Verify Backend Health

```bash
curl https://api.smartsalud.autonomos.dev/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "stores_count": 3,
  "stores": [...]
}
```

### 3. Test Models Endpoint

```bash
curl -H "Authorization: Bearer <your-secure-api-key>" \
  https://api.smartsalud.autonomos.dev/v1/models
```

**Expected Response:**
```json
{
  "object": "list",
  "data": [
    {"id": "smartsalud-rag", "object": "model", ...},
    {"id": "smartsalud-medico", "object": "model", ...},
    {"id": "smartsalud-matrona", "object": "model", ...},
    {"id": "smartsalud-secretaria", "object": "model", ...}
  ]
}
```

### 4. Test Chat Completion

```bash
curl -X POST https://api.smartsalud.autonomos.dev/v1/chat/completions \
  -H "Authorization: Bearer <your-secure-api-key>" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "smartsalud-medico",
    "messages": [
      {"role": "user", "content": "¿Cuáles son los síntomas de diabetes tipo 2?"}
    ]
  }'
```

**Expected:** JSON response with clinical guidelines answer and citations.

### 5. Verify Frontend Access

```bash
# Check frontend loads
curl -I https://smartsalud.autonomos.dev
```

**Expected:** HTTP 200, HTML response

**Browser Test:** Open https://smartsalud.autonomos.dev → Should load Open WebUI interface

### 6. Check Logs

```bash
# Backend logs
railway logs --service smartsalud-api --tail 50

# Frontend logs
railway logs --service smartsalud-frontend --tail 50
```

**Look for:**
- ✅ No errors or exceptions
- ✅ Health check responses (200 OK)
- ✅ Request/response timing logs
- ✅ "RAG query" and "RAG response" log entries

---

## Troubleshooting

### Backend Not Responding

**Symptom:** Health check fails or 502/503 errors

**Steps:**
1. Check logs: `railway logs --service smartsalud-api`
2. Verify environment variables: `railway variables`
3. Check build status: `railway status`
4. Restart service: `railway restart --service smartsalud-api`

**Common Causes:**
- Missing `GOOGLE_API_KEY` or `RAG_API_KEY`
- Incorrect Dockerfile path
- Port mismatch (ensure using `$PORT` env var)

### Frontend Can't Reach Backend

**Symptom:** Open WebUI shows "API connection error"

**Steps:**
1. Verify Private Network URL: `railway variables --service smartsalud-frontend`
2. Check `OPENAI_API_BASE_URL` uses Railway internal domain: `http://smartsalud-api.railway.internal:8080/v1`
3. Verify backend is healthy: `curl https://api.smartsalud.autonomos.dev/health`

**Common Causes:**
- Using public domain instead of `.railway.internal` for inter-service communication
- Incorrect API key in frontend env vars
- Backend service not running

### DNS Not Resolving

**Symptom:** Domain returns "ERR_NAME_NOT_RESOLVED"

**Steps:**
1. Verify CNAME records in GoDaddy
2. Check DNS propagation: `dig smartsalud.autonomos.dev`
3. Wait 10-60 minutes for full propagation
4. Clear browser DNS cache: `chrome://net-internals/#dns`

**Common Causes:**
- CNAME not pointing to correct Railway domain
- DNS propagation delay (TTL 600s)
- Typo in domain name

### Rate Limiting Issues

**Symptom:** 429 Too Many Requests

**Fix:** Backend has rate limit of 20 requests/minute per IP

**Solution:**
- Reduce request frequency
- Implement client-side rate limiting
- Contact if legitimate high traffic (can adjust limits)

---

## Production Checklist

Before going live:

- [ ] `GOOGLE_API_KEY` set and valid
- [ ] `RAG_API_KEY` set to secure value (not default)
- [ ] Health check returning 200 OK: `/health`
- [ ] Models endpoint accessible: `/v1/models`
- [ ] Chat completions working: `/v1/chat/completions`
- [ ] Custom domains configured and DNS propagated
- [ ] SSL/TLS certificates active (automatic)
- [ ] Backend logs showing no errors
- [ ] Frontend loading and connecting to backend
- [ ] CORS allowing frontend domain
- [ ] Rate limiting tested and appropriate

---

## Deployment Workflow

**Standard deployment flow:**

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   ```

2. **Railway auto-deploys:**
   - Detects push to `main` branch
   - Builds Docker image
   - Runs health checks
   - Deploys if healthy
   - Zero-downtime rollout

3. **Monitor deployment:**
   ```bash
   railway logs --follow
   ```

4. **Verify deployment:**
   ```bash
   curl https://api.smartsalud.autonomos.dev/health
   ```

**Rollback (if needed):**
```bash
# Railway automatically keeps previous deployments
# Rollback via Railway dashboard: Deployments → Select previous → Deploy
```

---

## Cost Optimization

**Railway Pricing (as of Dec 2024):**
- **Hobby Plan:** $5/month
- **Pro Plan:** $20/month + usage

**Current Usage (Estimated):**
- **Backend:** ~$3-5/month (single instance, low traffic)
- **Frontend:** ~$2-3/month (Docker container)
- **Total:** ~$5-8/month + Railway base plan

**Optimization Tips:**
- Use Railway Private Network (no egress costs)
- Enable health checks to prevent unnecessary restarts
- Monitor logs to avoid excessive logging costs
- Use Gemini flash models (cheaper than pro)

---

## Security Notes

| Layer | Security Measure |
|-------|------------------|
| **API Authentication** | Bearer token (`RAG_API_KEY`) required for all endpoints |
| **Transport** | HTTPS only (Railway-managed TLS) |
| **Rate Limiting** | 20 requests/minute per IP |
| **CORS** | Whitelist only allowed origins |
| **Private Network** | Backend-frontend communication over Railway internal network |
| **Secrets** | Environment variables never logged or exposed |

**Environment Variable Security:**
- Never commit `.env` files to Git
- Rotate `RAG_API_KEY` periodically
- Use strong, unique keys (minimum 32 characters)
- Review Railway access logs regularly

---

## Related Documentation

- **API Reference:** `DEPLOYMENT.md`
- **Quick Start:** `QUICK_START.md`
- **Infrastructure:** `INFRASTRUCTURE_SUMMARY.md`
- **Open WebUI Setup:** `docs/OPENWEBUI_INTEGRATION.md`
- **RAG Architecture:** `docs/RAG_GEMINI_SETUP.md`

---

## Security Considerations

### Production Security Checklist

Before deploying to production or exposing services publicly:

- [ ] Change default API key from setup
- [ ] Enable `WEBUI_AUTH=true` if publicly accessible
- [ ] Implement rate limiting at network level
- [ ] Monitor access logs for suspicious activity
- [ ] Rotate API keys regularly (monthly recommended)
- [ ] Use HTTPS only (enforced by Railway)
- [ ] Restrict CORS origins to known domains

### API Key Security

**⚠️ CRITICAL:**

- The example API key `smartsalud-rag-2024` in this document is for **demonstration only**
- **NEVER use this key in production**
- Generate strong, unique keys (minimum 32 characters, use random generator)
- Store keys in Railway environment variables ONLY (never commit to Git)
- Rotate keys if compromised or on regular schedule

### Authentication Warnings

**WEBUI_AUTH=false:**

- Disables all Open WebUI authentication
- Anyone with URL can access the system
- **ONLY safe for:**
  - Private networks with network-level access controls
  - VPN-protected environments
  - Internal development/testing

**For production with public access:**

- Set `WEBUI_AUTH=true`
- Configure user accounts via Open WebUI admin panel
- Implement additional network-level protections (firewall rules, IP whitelist)

### Monitoring & Incident Response

**Regular security reviews:**

- Review Railway access logs weekly
- Monitor for unusual traffic patterns
- Check for failed authentication attempts (if auth enabled)
- Audit API key usage in application logs

**If security incident suspected:**

1. Rotate API keys immediately via `railway variables`
2. Review logs for unauthorized access patterns
3. Enable authentication if disabled
4. Audit CORS configuration and allowed origins
5. Consider implementing additional rate limiting

---

**Last Updated:** 2024-12-02
**Maintainer:** Autonomos Lab (Applied Sciences Division)
