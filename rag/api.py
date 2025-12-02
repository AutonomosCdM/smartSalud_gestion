"""
FastAPI REST API for Gemini RAG - OpenAI Compatible.

Exposes the RAG as an OpenAI-compatible API endpoint for Open WebUI integration.

Usage:
    # Start server
    cd /Users/autonomos_dev/Projects/smartSalud_doc
    source .venv/bin/activate
    uvicorn rag.api:app --host 0.0.0.0 --port 8100

    # Test
    curl http://localhost:8100/v1/chat/completions \
      -H "Content-Type: application/json" \
      -d '{"model": "smartsalud-rag", "messages": [{"role": "user", "content": "¿Síntomas de diabetes?"}]}'
"""

import os
import time
import uuid
import secrets
import logging
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Key for authentication
API_KEY = os.getenv("RAG_API_KEY")
if not API_KEY:
    raise ValueError("RAG_API_KEY environment variable must be set")
security = HTTPBearer(auto_error=False)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
request_start_times = {}


async def verify_api_key(
    authorization: Optional[str] = Header(None),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> bool:
    """Verify API key from Authorization header."""
    # Accept Bearer token or direct API key
    token = None
    if credentials:
        token = credentials.credentials
    elif authorization:
        if authorization.startswith("Bearer "):
            token = authorization[7:]
        else:
            token = authorization

    if not token:
        raise HTTPException(status_code=401, detail="API key required")

    if not secrets.compare_digest(token, API_KEY):
        raise HTTPException(status_code=401, detail="Invalid API key")

    return True

# Import RAG components
from .gemini_rag import GeminiRAG
from .stores import StoreManager

app = FastAPI(
    title="smartSalud RAG API",
    description="OpenAI-compatible API for MINSAL clinical guidelines",
    version="1.0.0"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS for Open WebUI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "https://smartsalud.autonomos.dev",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG client (lazy)
_rag: Optional[GeminiRAG] = None
_manager: Optional[StoreManager] = None


def get_rag() -> GeminiRAG:
    global _rag
    if _rag is None:
        _rag = GeminiRAG()
    return _rag


def get_manager() -> StoreManager:
    global _manager
    if _manager is None:
        _manager = StoreManager()
    return _manager


# --- Pydantic Models (OpenAI-compatible) ---

class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = "smartsalud-rag"
    messages: list[Message]
    temperature: float = 0.7
    max_tokens: int = 2048
    # Custom fields for role-based access
    user_role: str = "medico"  # matrona, medico, secretaria


class ChatCompletionChoice(BaseModel):
    index: int
    message: Message
    finish_reason: str


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[ChatCompletionChoice]
    usage: Usage


class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str


class ModelsResponse(BaseModel):
    object: str = "list"
    data: list[ModelInfo]


# --- Endpoints ---

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing."""
    request_id = str(uuid.uuid4())
    start_time = time.time()

    logger.info(
        f"Request started - ID: {request_id} - Method: {request.method} - Path: {request.url.path}"
    )

    response = await call_next(request)

    duration = time.time() - start_time
    logger.info(
        f"Request completed - ID: {request_id} - Method: {request.method} - "
        f"Path: {request.url.path} - Status: {response.status_code} - Duration: {duration:.3f}s"
    )

    return response


@app.get("/")
def root():
    """Health check."""
    return {"status": "ok", "service": "smartSalud RAG API"}


@app.get("/v1/models", response_model=ModelsResponse)
def list_models(authenticated: bool = Depends(verify_api_key)):
    """List available models (OpenAI-compatible). Requires API key."""
    return ModelsResponse(
        data=[
            ModelInfo(
                id="smartsalud-rag",
                created=int(time.time()),
                owned_by="smartsalud"
            ),
            ModelInfo(
                id="smartsalud-medico",
                created=int(time.time()),
                owned_by="smartsalud"
            ),
            ModelInfo(
                id="smartsalud-matrona",
                created=int(time.time()),
                owned_by="smartsalud"
            ),
            ModelInfo(
                id="smartsalud-secretaria",
                created=int(time.time()),
                owned_by="smartsalud"
            ),
        ]
    )


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
@limiter.limit("20/minute")
def chat_completions(
    request: Request,
    body: ChatCompletionRequest,
    authenticated: bool = Depends(verify_api_key)
):
    """OpenAI-compatible chat completions endpoint. Requires API key. Rate limited to 20 requests/minute."""
    rag_start_time = time.time()
    try:
        rag = get_rag()

        # Extract question from last user message
        question = None
        for msg in reversed(body.messages):
            if msg.role == "user":
                question = msg.content
                break

        if not question:
            raise HTTPException(status_code=400, detail="No user message found")

        # Determine role from model name or explicit field
        role = body.user_role
        if "medico" in body.model:
            role = "medico"
        elif "matrona" in body.model:
            role = "matrona"
        elif "secretaria" in body.model:
            role = "secretaria"

        # Query RAG
        logger.info(
            f"RAG query - Role: {role} - Question length: {len(question)} chars"
        )
        result = rag.query_by_role(question=question, role=role)
        rag_duration = time.time() - rag_start_time

        logger.info(
            f"RAG response - Role: {role} - Response time: {rag_duration:.3f}s - "
            f"Citations: {len(result.get('citations', []))}"
        )

        # Format response - Gemini already includes ## Fuentes via system instruction
        answer = result["answer"]

        # Estimate tokens (rough)
        prompt_tokens = len(question.split()) * 2
        completion_tokens = len(answer.split()) * 2

        return ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
            created=int(time.time()),
            model=body.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=Message(role="assistant", content=answer),
                    finish_reason="stop"
                )
            ],
            usage=Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens
            )
        )

    except Exception as e:
        logger.error(f"Chat completion error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    """Detailed health check."""
    try:
        manager = get_manager()
        stores = manager.list_stores()
        return {
            "status": "healthy",
            "stores_count": len(stores),
            "stores": [s["display_name"] for s in stores]
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# CLI runner
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)
