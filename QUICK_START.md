# smartSalud RAG - Quick Start Guide

## 5-Minute Setup

### 1. Environment Setup (2 min)
```bash
cd /Users/autonomos_dev/Projects/smartSalud_doc

# Create .env from template
cp .env.example .env

# Edit .env - add your Google API key
# Get key from: https://aistudio.google.com/apikey
nano .env
# OR
export GOOGLE_API_KEY=your_key_here
```

### 2. Start Container (1 min)
```bash
# Build and start
docker-compose up --build

# Expected output:
# smartsalud-rag | INFO:     Application startup complete
```

### 3. Test API (1 min)
```bash
# In another terminal:

# Health check
curl http://localhost:8100/health

# Test query
curl -X POST http://localhost:8100/v1/chat/completions \
  -H "Authorization: Bearer smartsalud-rag-2024" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "smartsalud-medico",
    "messages": [{"role": "user", "content": "¿Síntomas de dengue?"}]
  }'
```

### 4. View Logs (1 min)
```bash
# Follow logs in real-time
docker-compose logs -f smartsalud-rag
```

## Common Commands

| Task | Command |
|------|---------|
| Start | `docker-compose up` |
| Stop | `docker-compose down` |
| Rebuild | `docker-compose up --build` |
| Logs | `docker-compose logs -f` |
| Stats | `docker stats smartsalud-rag` |
| Shell | `docker-compose exec smartsalud-rag bash` |
| Health | `curl http://localhost:8100/health` |
| Test | `pytest rag/test_rag.py -v` |

## Deployment Checklist

### Before Committing
- [ ] `docker-compose up --build` succeeds
- [ ] `curl http://localhost:8100/health` returns 200
- [ ] Tests pass: `pytest rag/test_rag.py --cov=rag --cov-report=html`
- [ ] Coverage >= 70%
- [ ] No lint errors: `ruff check rag/`

### Before Pushing to Main
- [ ] All local tests pass
- [ ] `.env` file not committed (add to .gitignore if needed)
- [ ] Commit message is clear
- [ ] GitHub Actions secrets configured

### Before Production Deploy
- [ ] CI/CD pipeline passed on main branch
- [ ] Health check verified in staging
- [ ] Rollback plan documented and tested
- [ ] Team notified of deployment

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs smartsalud-rag

# Common issues:
# 1. GOOGLE_API_KEY missing → Edit .env
# 2. Port 8100 in use → docker-compose down
# 3. Invalid .env format → Check syntax
```

### API returns 401 (Unauthorized)
```bash
# Check API key header
curl -X POST http://localhost:8100/v1/chat/completions \
  -H "Authorization: Bearer smartsalud-rag-2024" \
  ...
```

### Health check failing
```bash
# Verify stores are initialized
docker-compose exec smartsalud-rag python -m rag.test_rag

# Check logs for errors
docker-compose logs smartsalud-rag | grep -i error
```

### Slow responses (>10 seconds)
```bash
# Could be Gemini API rate limiting
# Check usage: https://console.cloud.google.com/
# Wait 1 minute and retry
```

## File Locations

| File | Purpose | Access |
|------|---------|--------|
| `Dockerfile` | Container image | Read-only |
| `docker-compose.yml` | Local orchestration | Read-only |
| `.env` | Configuration (secrets) | Never commit |
| `.env.example` | Configuration template | Template |
| `DEPLOYMENT.md` | Full runbook | Reference |
| `rag/api.py` | FastAPI server | Source |
| `rag/requirements.txt` | Dependencies | Source |

## Architecture

```
Client
  ↓
HTTP (port 8100)
  ↓
FastAPI (rag/api.py)
  ↓
GeminiRAG (rag/gemini_rag.py)
  ↓
Google Gemini File Search API
  ↓
MINSAL Clinical Guidelines (PDFs in Gemini Store)
```

## Support

For detailed documentation, see:
- **DEPLOYMENT.md** - Full deployment runbook
- **INFRASTRUCTURE_SUMMARY.md** - Architecture decisions
- **rag/api.py** - API documentation
- **CLAUDE.md** - Project standards

## Next Steps

1. **Local Development**
   - Start container: `docker-compose up`
   - Make changes to `rag/` directory
   - Changes auto-reload (if you mount code volume)

2. **Testing**
   - Run tests: `pytest rag/test_rag.py -v`
   - Check coverage: `pytest rag/ --cov=rag --cov-report=html`

3. **Commit & Push**
   - Verify all tests pass locally
   - Push to develop branch for staging
   - Push to main branch for production

4. **Monitor**
   - GitHub Actions will run CI/CD
   - Check build status in Actions tab
   - Monitor health metrics post-deployment

---

**Questions?** See DEPLOYMENT.md troubleshooting section or review CLAUDE.md project standards.
