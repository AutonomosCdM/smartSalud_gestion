# smartSalud RAG Deployment Runbook

## Architecture Overview

- **Application**: FastAPI server (Python 3.11)
- **API**: OpenAI-compatible endpoints on port 8100
- **Dependencies**: google-genai, fastapi, uvicorn
- **Health Check**: `/health` endpoint (30s interval)
- **Auth**: Bearer token via `RAG_API_KEY`

## Local Development

### Prerequisites
```bash
python 3.11+
docker & docker-compose
```

### Setup

```bash
# Clone repo
cd /Users/autonomos_dev/Projects/smartSalud_doc

# Create .env from template
cp .env.example .env
# Edit .env and add GOOGLE_API_KEY

# Virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r rag/requirements.txt
pip install pytest pytest-cov
```

### Running Locally

**Without Docker:**
```bash
# Start server
uvicorn rag.api:app --host 0.0.0.0 --port 8100

# Test health
curl http://localhost:8100/health

# Test API
curl -X POST http://localhost:8100/v1/chat/completions \
  -H "Authorization: Bearer smartsalud-rag-2024" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "smartsalud-medico",
    "messages": [{"role": "user", "content": "¿Síntomas de dengue?"}]
  }'
```

**With Docker Compose:**
```bash
# Build and start
docker-compose up --build

# View logs
docker-compose logs -f smartsalud-rag

# Test
curl http://localhost:8100/health

# Stop
docker-compose down
```

### Running Tests

```bash
# All tests
pytest rag/test_rag.py -v

# With coverage
pytest rag/test_rag.py --cov=rag --cov-report=html

# Coverage report
open htmlcov/index.html
```

## CI/CD Pipeline

### GitHub Actions Workflow

Triggered on `push` to `main`/`develop` or `pull_request`:

**Phase 1: Lint** (5min)
- Ruff linter: E, W, F checks
- Pylint: code quality (score >= 7.0)

**Phase 2: Test** (10min)
- pytest with coverage (fail if < 70%)
- Security scans (bandit, safety)
- Upload to Codecov

**Phase 3: Build** (15min, only on main)
- Multi-stage Docker build
- Push to registry (requires secrets)
- Cache for faster builds

### Required GitHub Secrets

```yaml
DOCKER_USERNAME: your_docker_username
DOCKER_PASSWORD: your_docker_password
DOCKER_REGISTRY: docker.io/your_registry
GOOGLE_API_KEY: your_gemini_api_key
```

## Staging Deployment

### 1. Pre-deployment Checks

```bash
# Verify CI passed
# Check GitHub Actions tab

# Check health locally
docker-compose up -d
sleep 5
curl http://localhost:8100/health
docker-compose down
```

### 2. Deploy to Staging

```bash
# Pull latest image
docker pull docker.io/your_registry/smartsalud-rag:latest

# Deploy with docker-compose
docker-compose -f docker-compose.yml up -d

# Verify health
curl -f http://localhost:8100/health || echo "Health check failed"

# Run smoke tests
pytest tests/smoke/ -v
```

### 3. Verify Staging

```bash
# Check API endpoints
curl -X POST http://localhost:8100/v1/chat/completions \
  -H "Authorization: Bearer smartsalud-rag-2024" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "smartsalud-medico",
    "messages": [{"role": "user", "content": "Prueba"}]
  }'

# Monitor logs for 5min
docker-compose logs -f --tail=50
```

## Production Deployment

### 1. Deployment Checklist

- [ ] All CI checks pass on main branch
- [ ] Coverage >= 70%
- [ ] No critical security findings
- [ ] Staging deployment verified
- [ ] Rollback plan tested
- [ ] Team notified

### 2. Rolling Deployment

```bash
# Set image version
VERSION=sha256:xyz123

# Update container (zero-downtime)
docker-compose up -d \
  --no-deps \
  --build \
  smartsalud-rag

# Verify health (30s timeout)
timeout 30 bash -c '
  until curl -f http://localhost:8100/health; do
    echo "Waiting for health check..."
    sleep 2
  done
'

# Monitor error rate for 5 minutes
watch -n 5 'curl -s http://localhost:8100/health | jq .'
```

### 3. Health Metrics

Track these metrics for 5 minutes post-deployment:

| Metric | Threshold | Alert |
|--------|-----------|-------|
| Error Rate | < 1% | CRITICAL if > 5% |
| Latency P95 | < 2s | WARNING if > 1s |
| Available Stores | > 0 | CRITICAL if 0 |
| Health Endpoint | 200 OK | CRITICAL if != 200 |

## Rollback Procedure

### Immediate Rollback (< 2 min)

```bash
# Stop current container
docker-compose down

# Restore previous image
docker pull docker.io/your_registry/smartsalud-rag:previous-tag

# Start with previous version
docker-compose up -d

# Verify health
curl -f http://localhost:8100/health

# Notify team
# POST to Slack with rollback notification
```

### Root Cause Analysis

After rollback, investigate:

```bash
# Check logs
docker-compose logs smartsalud-rag > /tmp/deploy-error.log

# Review changes
git log --oneline -5

# Check API key validity
echo $GOOGLE_API_KEY | wc -c  # Should be ~32+ chars

# Test RAG locally
python -m rag.test_rag
```

## Monitoring & Observability

### Logs

```bash
# View current logs
docker-compose logs smartsalud-rag

# Follow logs
docker-compose logs -f smartsalud-rag

# Last 100 lines
docker-compose logs --tail=100 smartsalud-rag

# Export logs
docker-compose logs smartsalud-rag > deployment.log
```

### Health Checks

**Manual:**
```bash
curl http://localhost:8100/health | jq .
```

**Response (Healthy):**
```json
{
  "status": "healthy",
  "stores_count": 3,
  "stores": ["MINSAL General", "Maternidad", "Secretaría"]
}
```

**Response (Unhealthy):**
```json
{
  "status": "unhealthy",
  "error": "Store configuration missing"
}
```

### Container Stats

```bash
# CPU, memory, network
docker stats smartsalud-rag

# Inspect container
docker inspect smartsalud-rag | jq '.State.Health'
```

## Troubleshooting

### API Returns 401 Unauthorized

**Cause**: Invalid or missing `RAG_API_KEY`

```bash
# Check env
grep RAG_API_KEY .env

# Fix: Update and restart
docker-compose restart smartsalud-rag
```

### Health Check Fails

**Cause**: Gemini API key invalid or stores not initialized

```bash
# Check logs
docker-compose logs smartsalud-rag | tail -50

# Test API key
# Log into your GCP project and verify key is valid

# Reinitialize stores
docker-compose down -v  # Remove volume
docker-compose up -d
```

### High Memory Usage

**Cause**: Large documents cached in memory

```bash
# Monitor memory
docker stats smartsalud-rag

# Restart container (clears cache)
docker-compose restart smartsalud-rag
```

### Slow Response Times

**Cause**: Gemini API rate limiting

```bash
# Check response time
time curl -X POST http://localhost:8100/v1/chat/completions \
  -H "Authorization: Bearer smartsalud-rag-2024" \
  -H "Content-Type: application/json" \
  -d '{"model":"smartsalud-medico","messages":[{"role":"user","content":"Prueba"}]}'

# If > 10s, check Gemini quota in GCP console
```

## Incident Response

### Service Down (health check failing)

**1. Immediate (0-2 min)**
```bash
# Verify container is running
docker-compose ps

# If down, restart
docker-compose up -d

# Check logs for errors
docker-compose logs smartsalud-rag
```

**2. Investigation (2-10 min)**
```bash
# Check dependencies
# 1. GOOGLE_API_KEY valid?
# 2. Gemini API quota available?
# 3. Network connectivity to api.google.com?

# Test connectivity
curl -I https://generativelanguage.googleapis.com/

# Check API key format
test -z "$GOOGLE_API_KEY" && echo "KEY MISSING" || echo "KEY SET"
```

**3. Escalation (> 10 min)**
- [ ] Check Gemini API status dashboard
- [ ] Verify GCP project limits
- [ ] Review recent changes (git log)
- [ ] Contact DevOps team

---

**Last Updated**: 2025-11-30
**Maintained By**: Alex Kumar (DevOps)
