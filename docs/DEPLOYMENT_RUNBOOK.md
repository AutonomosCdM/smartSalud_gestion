# smartSalud RAG Production Deployment Runbook

**Architecture**: Split frontend/backend with custom domains
**Last Updated**: 2024-12-02
**Status**: ✅ PRODUCTION READY

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│ smartsalud.autonomos.dev (Frontend)                 │
│ Open WebUI - Docker Container                       │
│ Image: ghcr.io/open-webui/open-webui:main          │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ HTTPS
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│ api.smartsalud.autonomos.dev (Backend)              │
│ FastAPI + Gemini RAG - Python Application          │
│ Repo: AutonomosCdM/smartSalud-rag                   │
└─────────────────────────────────────────────────────┘
```

## Deployment Status

### ✅ Phase 1: DNS Configuration (COMPLETED - 2024-12-01)
- [x] GoDaddy DNS records configured
- [x] CNAME: api.smartsalud → Railway domain
- [x] DNS propagation verified
- [x] SSL certificates active

### ✅ Phase 2: Railway Backend Configuration (COMPLETED - 2024-12-01)
- [x] Custom domain configured: api.smartsalud.autonomos.dev
- [x] SSL/TLS provisioned automatically
- [x] Health checks passing
- [x] Auto-deploy from GitHub main branch active

### ✅ Phase 3: Railway Frontend Deployment (COMPLETED - 2024-12-01)
- [x] Open WebUI deployed as Docker service
- [x] Custom domain: smartsalud.autonomos.dev
- [x] Railway Private Network configured
- [x] Environment variables set
- [x] CORS configuration updated

### ✅ Phase 4: End-to-End Verification (COMPLETED - 2024-12-02)
- [x] Frontend accessible at https://smartsalud.autonomos.dev
- [x] Backend API responding at https://api.smartsalud.autonomos.dev
- [x] All 4 models available (smartsalud-rag, -medico, -matrona, -secretaria)
- [x] CORS working correctly
- [x] Auto-deploy pipeline functional

### Production Notes

**Auto-Deploy Status**: ✅ Working
- GitHub main branch → Railway automatic deployment
- Commits trigger builds and zero-downtime rollouts

**Fixed Issues** (no longer active):
- slowapi parameter bug (fixed in commit: f9f9cd2)
- Audio stub endpoints (added in commit: c160777)
- CORS production domain (fixed in commit: e2e2448)

---

## Historical Manual Steps (FOR REFERENCE ONLY - Already Completed)

### Phase 1: DNS Configuration (COMPLETED)

**Action Required**: Add DNS record in GoDaddy

1. Navigate to: https://dcc.godaddy.com/control/autonomos.dev/dns
2. Click "Add" → Select "CNAME"
3. Configure:
   ```
   Type:      CNAME
   Host:      api.smartsalud
   Points to: 0s22c821.up.railway.app
   TTL:       600 (10 minutes)
   ```
4. Save

**Verification**:
```bash
# Wait ~10 minutes for propagation
dig api.smartsalud.autonomos.dev CNAME +short
# Expected: 0s22c821.up.railway.app.
```

### ⏳ Phase 2: Railway Backend Reconfiguration (MANUAL REQUIRED)

**Action Required**: Update Railway service domain

1. Navigate to: https://railway.app/project/smartsalud-rag
2. Select service: `smartsalud-api`
3. Go to "Settings" → "Domains"
4. **Remove** domain: `smartsalud.autonomos.dev`
5. **Add** domain: `api.smartsalud.autonomos.dev`
6. Wait for SSL certificate provisioning (~2 minutes)

**Verification**:
```bash
curl https://api.smartsalud.autonomos.dev/health
# Expected: {"status":"healthy","stores_count":3,...}
```

### ⏳ Phase 3: Railway Frontend Deployment (MANUAL REQUIRED)

**Action Required**: Deploy Open WebUI as new Railway service

1. Navigate to: https://railway.app/project/smartsalud-rag
2. Click "New" → "Docker Image"
3. Configure service:
   ```yaml
   Service Name: smartsalud-frontend
   Image Source: ghcr.io/open-webui/open-webui:main
   ```

4. Add environment variables:
   ```env
   OPENAI_API_BASE_URLS=https://api.smartsalud.autonomos.dev
   ENABLE_SIGNUP=false
   OPENAI_API_KEYS=sk-dummy-key-for-custom-backend
   ```

5. Add volume:
   ```
   Mount Path: /app/backend/data
   Size: 1 GB
   ```

6. Add domain:
   ```
   Custom Domain: smartsalud.autonomos.dev
   ```
   - Railway will show DNS instructions
   - DNS is already configured (existing CNAME)
   - Wait for SSL certificate (~2 minutes)

7. Deploy

**Verification**:
```bash
# Frontend accessible
curl -I https://smartsalud.autonomos.dev
# Expected: HTTP/2 200

# Backend API responds
curl https://api.smartsalud.autonomos.dev/health
# Expected: {"status":"healthy",...}
```

### Historical Verification Steps (Already Completed)

**Verification Steps**:

1. **Frontend Access**:
   - Navigate to: https://smartsalud.autonomos.dev
   - Expected: Open WebUI login screen

2. **Backend Connection**:
   - In Open WebUI: Settings → Connections
   - Add connection: `https://api.smartsalud.autonomos.dev`
   - API Key: (from Railway RAG_API_KEY env var)
   - Test connection
   - Expected: Connection successful

3. **Model Selection**:
   - Navigate to: New Chat
   - Select model dropdown
   - Expected models:
     - smartsalud-rag
     - smartsalud-medico
     - smartsalud-matrona
     - smartsalud-secretaria

4. **Chat Test**:
   - Select model: `smartsalud-medico`
   - Send message: "¿Síntomas de diabetes tipo 2?"
   - Expected: Response with clinical guidelines + citations

5. **CORS Verification**:
   - Check browser console (F12)
   - Expected: No CORS errors

6. **Health Monitoring**:
   ```bash
   # Backend health
   watch -n 5 'curl -s https://api.smartsalud.autonomos.dev/health | jq'

   # Frontend health
   curl -I https://smartsalud.autonomos.dev
   ```

## Configuration Files

### Backend Environment Variables (Railway)
```env
# Gemini API
GOOGLE_API_KEY=<from-railway-secrets>

# Authentication
RAG_API_KEY=<from-railway-secrets>

# Gemini Vector Store IDs
SMARTSALUD_MEDICO_STORE_ID=<from-railway-secrets>
SMARTSALUD_MATRONA_STORE_ID=<from-railway-secrets>
SMARTSALUD_SECRETARIA_STORE_ID=<from-railway-secrets>

# Railway auto-configured
PORT=<dynamic>
```

### Frontend Environment Variables (Railway)
```env
# Backend connection (using Railway Private Network)
OPENAI_API_BASE_URLS=http://smartsalud-api.railway.internal/v1

# Authentication
OPENAI_API_KEYS=sk-dummy-key-for-custom-backend

# Security
ENABLE_SIGNUP=false

# Railway auto-configured
PORT=<dynamic>
```

## Rollback Plan

**Scenario**: Deployment fails or introduces issues

### Immediate Rollback (< 2 minutes)

1. **Railway Console**:
   - Navigate to: https://railway.app/project/smartsalud-rag
   - Select service: `smartsalud-api`
   - Click "Deployments"
   - Select previous successful deployment
   - Click "Redeploy"

2. **Git Rollback**:
   ```bash
   git revert e2e2448  # Revert CORS changes
   git push origin main  # Triggers auto-deploy
   ```

### DNS Rollback (if needed)

1. **GoDaddy**:
   - Remove CNAME: `api.smartsalud`
   - Update CNAME: `smartsalud` → `0s22c821.up.railway.app`

2. **Railway**:
   - Restore `smartsalud.autonomos.dev` to backend service
   - Remove frontend service

## Monitoring & Observability

### Health Checks

```bash
# Backend health (detailed)
curl https://api.smartsalud.autonomos.dev/health

# Backend health (simple)
curl https://api.smartsalud.autonomos.dev/

# Frontend health
curl -I https://smartsalud.autonomos.dev
```

### Logs

```bash
# Railway CLI - Backend logs
railway logs -s smartsalud-api --tail 100

# Railway CLI - Frontend logs
railway logs -s smartsalud-frontend --tail 100
```

### Metrics

Monitor in Railway dashboard:
- CPU usage (target: <50%)
- Memory usage (target: <80%)
- Request rate
- Error rate (target: <1%)
- P95 latency (target: <2s)

### Alerts

Set up in Railway:
- Deployment failures
- High error rate (>5%)
- High latency (P95 >3s)
- Service downtime

## Security Checklist

- [x] API key authentication enabled
- [x] CORS restricted to production domain
- [x] Rate limiting active (20 req/min)
- [x] HTTPS enforced
- [x] Signup disabled on frontend
- [ ] Regular security scans (schedule monthly)
- [ ] Dependency updates (schedule weekly)

## Production Status

**Current State**: ✅ Fully deployed and operational

**Services Running**:
- Backend API: https://api.smartsalud.autonomos.dev/health
- Frontend UI: https://smartsalud.autonomos.dev
- Auto-deploy: Active (GitHub main → Railway)

**Models Available**: 4 (smartsalud-rag, smartsalud-medico, smartsalud-matrona, smartsalud-secretaria)

## Ongoing Maintenance

1. **Monitor for 1 hour**:
   - Watch Railway logs for errors
   - Monitor health endpoints
   - Test all models

2. **User Acceptance Testing**:
   - Test with real CESFAM users
   - Validate clinical guidelines responses
   - Check citation accuracy

3. **Performance Baseline**:
   - Measure P95 latency
   - Record error rate
   - Document typical usage patterns

4. **Documentation**:
   - Update user guides with new URL
   - Add troubleshooting section
   - Document backup procedures

## Contact

- **DevOps Lead**: alex-kumar (Railway/Infrastructure)
- **Security**: victoria-frost (Audit/Compliance)
- **Backend**: liam-obrien (FastAPI/Gemini)
- **On-Call**: Lucius Fox (Coordinator)

---

**Last Deployment**: 2024-12-01 (Production deployment completed)
**Next Review**: Weekly monitoring or after significant changes
**Runbook Version**: 1.1 (Updated 2024-12-02)
