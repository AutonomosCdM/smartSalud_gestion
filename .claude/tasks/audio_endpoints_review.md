# Audio Endpoints Architectural Review

**Date**: 2025-12-02
**Reviewer**: sarah-chen
**Status**: PENDING

## Request

Add stub audio endpoints to rag/api.py to fix Open WebUI 50s latency issue.

## Proposed Changes

```python
@app.get("/v1/audio/voices")
def list_audio_voices(authenticated: bool = Depends(verify_api_key)):
    """Stub endpoint for Open WebUI compatibility. Returns empty voice list."""
    return {"data": []}

@app.get("/v1/audio/models")
def list_audio_models(authenticated: bool = Depends(verify_api_key)):
    """Stub endpoint for Open WebUI compatibility. Returns empty model list."""
    return {"data": []}
```

## Context

- Open WebUI expects these endpoints even when TTS/STT disabled
- Missing endpoints cause 50s timeout on view switching
- Backend responds in <12ms, frontend is the blocker
- Research confirms this is a known Open WebUI issue (#15079)

## Architectural Questions

1. Does this violate Single Responsibility (API serving audio metadata)?
2. Should stub endpoints be in a separate router module?
3. Security implications of empty responses with API key auth?
4. Alignment with OpenAI compatibility pattern?

## Current Architecture

- FastAPI with OpenAI-compatible endpoints
- API key auth on all /v1/* endpoints
- Existing: /v1/models, /v1/chat/completions
- CORS configured for Open WebUI

---

**Review Required**: APPROVE | APPROVE_WITH_CONDITIONS | REJECT
