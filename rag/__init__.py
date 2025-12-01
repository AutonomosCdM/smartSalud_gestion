"""
smartSalud RAG module for Gemini File Search.

Provides document retrieval augmented generation for CESFAM medical staff.
"""

from .gemini_rag import GeminiRAG
from .stores import StoreManager, STORE_CONFIG, DOCUMENT_STORE_MAP
from .upload import DocumentUploader, upload_minsal_docs

__all__ = [
    "GeminiRAG",
    "StoreManager",
    "DocumentUploader",
    "upload_minsal_docs",
    "STORE_CONFIG",
    "DOCUMENT_STORE_MAP",
]
