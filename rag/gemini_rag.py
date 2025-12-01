"""
Gemini File Search RAG Client for smartSalud CESFAM.

This module provides a high-level interface to Google's Gemini File Search API
for querying medical guidelines and protocols.
"""

import os
import logging
from typing import Optional
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class GeminiRAG:
    """Client for Gemini File Search RAG operations."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini client.

        Args:
            api_key: Google API key. If None, uses GOOGLE_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.5-flash"

    def query(
        self,
        question: str,
        store_ids: list[str],
        system_prompt: Optional[str] = None
    ) -> dict:
        """Query documents in File Search stores.

        Args:
            question: The question to ask.
            store_ids: List of File Search store IDs to search.
            system_prompt: Optional system instructions.

        Returns:
            dict with 'answer' and 'citations' keys.
        """
        # Use dict syntax for compatibility
        config = {
            'tools': [{
                'file_search': {
                    'file_search_store_names': store_ids
                }
            }]
        }

        # Add citation instruction to system prompt
        citation_instruction = "\n\nIMPORTANTE: Al final de tu respuesta, incluye una sección '## Fuentes' listando los documentos específicos que usaste con el formato: [Nombre del documento, página X]."
        if system_prompt:
            config['system_instruction'] = system_prompt + citation_instruction
        else:
            config['system_instruction'] = citation_instruction

        response = self.client.models.generate_content(
            model=self.model,
            contents=question,
            config=config
        )

        # Extract citations from grounding metadata
        citations = []
        try:
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                # Try grounding_metadata for file search
                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    metadata = candidate.grounding_metadata
                    # File search uses grounding_chunks with retrieved_context
                    if hasattr(metadata, 'grounding_chunks') and metadata.grounding_chunks:
                        for chunk in metadata.grounding_chunks:
                            if chunk:
                                # Try retrieved_context (file search)
                                if hasattr(chunk, 'retrieved_context') and chunk.retrieved_context:
                                    ctx = chunk.retrieved_context
                                    citations.append({
                                        'source': getattr(ctx, 'title', 'Documento MINSAL'),
                                        'uri': getattr(ctx, 'uri', ''),
                                        'text': getattr(chunk, 'text', '')[:200] if hasattr(chunk, 'text') else ''
                                    })
                                # Try web (web search fallback)
                                elif hasattr(chunk, 'web') and chunk.web:
                                    citations.append({
                                        'source': getattr(chunk.web, 'title', 'Documento'),
                                        'uri': getattr(chunk.web, 'uri', ''),
                                        'text': ''
                                    })
                    # Also check grounding_supports for inline citations
                    if hasattr(metadata, 'grounding_supports') and metadata.grounding_supports:
                        for support in metadata.grounding_supports:
                            if hasattr(support, 'segment') and support.segment:
                                seg = support.segment
                                # Get the grounding chunk indices
                                if hasattr(support, 'grounding_chunk_indices'):
                                    for idx in support.grounding_chunk_indices:
                                        if idx < len(citations):
                                            citations[idx]['referenced'] = True
        except Exception as e:
            logger.warning(f"Citation extraction failed: {e}")

        return {
            'answer': response.text,
            'citations': citations
        }

    def query_by_role(self, question: str, role: str) -> dict:
        """Query with automatic store selection based on user role.

        Args:
            question: The question to ask.
            role: User role ('matrona', 'medico', 'secretaria').

        Returns:
            dict with 'answer' and 'citations' keys.
        """
        from .stores import StoreManager

        manager = StoreManager(self.client)
        store_ids = manager.get_stores_for_role(role)

        # Template estándar para todos los agentes (ver docs/AGENT_TEMPLATE.md)
        AGENT_TEMPLATE = """Eres {nombre}, asistente clínico del CESFAM especializado en {especialidad}.

Tienes acceso a guías clínicas MINSAL Chile indexadas en File Search.
Stores: {stores}

REGLAS - NO NEGOCIABLES:
1. SOLO responde con información de las fuentes indexadas
2. Si no encuentras información, responde: "NO ENCONTRADO EN FUENTE"
3. SIEMPRE cita fuente y página: [Documento, p.X]
4. NO inventes datos, estadísticas ni recomendaciones
5. Ante duda clínica, recomienda consultar especialista

FORMATO RESPUESTA:
- Respuesta directa y concisa
- Bullets para listas
- Tablas para comparaciones
- Al final: ## Fuentes con citas específicas"""

        agent_config = {
            'matrona': {
                'nombre': 'Asistente Matrona MINSAL',
                'especialidad': 'maternidad, control prenatal y ginecología',
                'stores': 'MINSAL_Normativas, MINSAL_Matronas, CESFAM_Procedimientos'
            },
            'medico': {
                'nombre': 'Asistente Médico MINSAL',
                'especialidad': 'guías clínicas, diagnóstico y tratamiento',
                'stores': 'MINSAL_Normativas, MINSAL_Medicos'
            },
            'secretaria': {
                'nombre': 'Asistente Administrativo CESFAM',
                'especialidad': 'procedimientos administrativos y flujos CESFAM',
                'stores': 'MINSAL_Normativas, CESFAM_Procedimientos'
            }
        }

        config = agent_config.get(role.lower(), {
            'nombre': 'Asistente General MINSAL',
            'especialidad': 'consultas generales guías MINSAL',
            'stores': 'Todos'
        })

        system_prompts = {
            role.lower(): AGENT_TEMPLATE.format(**config)
            for role in ['matrona', 'medico', 'secretaria']
        }
        # Add default
        system_prompts['default'] = AGENT_TEMPLATE.format(**agent_config.get('medico'))

        return self.query(
            question=question,
            store_ids=store_ids,
            system_prompt=system_prompts.get(role.lower())
        )


# CLI usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Query MINSAL guidelines")
    parser.add_argument("question", help="Question to ask")
    parser.add_argument("--role", default="medico", choices=["matrona", "medico", "secretaria"])
    args = parser.parse_args()

    rag = GeminiRAG()
    result = rag.query_by_role(args.question, args.role)

    print(f"\n{'='*60}")
    print(f"Respuesta:\n{result['answer']}")
    if result['citations']:
        print(f"\nFuentes:")
        for c in result['citations']:
            print(f"  - {c['source']}")
