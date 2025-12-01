# smartSalud RAG - Guías Clínicas MINSAL

Sistema RAG basado en Gemini File Search para consulta de guías clínicas del MINSAL Chile.

## Arquitectura

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Open WebUI    │────▶│  RAG API (8100)  │────▶│  Gemini File    │
│   (Docker)      │     │  OpenAI-compat   │     │  Search         │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                         │
                                                         ▼
                                                  ┌─────────────┐
                                                  │ PDFs MINSAL │
                                                  └─────────────┘
```

## Componentes

| Componente | Puerto | Descripción |
|------------|--------|-------------|
| RAG API | 8100 | FastAPI OpenAI-compatible |
| Open WebUI | 3000 | Interface de chat |
| Gemini File Search | Cloud | RAG managed by Google |

## Quick Start

```bash
# 1. Activar entorno
cd /Users/autonomos_dev/Projects/smartSalud_doc
source .venv/bin/activate

# 2. Iniciar API
uvicorn rag.api:app --host 0.0.0.0 --port 8100

# 3. Verificar
curl http://localhost:8100/health
```

## Modelos Disponibles

| Modelo | Rol | Stores |
|--------|-----|--------|
| `smartsalud-rag` | General | Todos |
| `smartsalud-medico` | Médico | Normativas + Medicos |
| `smartsalud-matrona` | Matrona | Normativas + Matronas |
| `smartsalud-secretaria` | Admin | Normativas + Procedimientos |

## Autenticación

```bash
# API Key requerida
curl -H "Authorization: Bearer smartsalud-rag-2024" \
  http://localhost:8100/v1/models
```

## Estructura

```
smartSalud_doc/
├── .env                 # GOOGLE_API_KEY, RAG_API_KEY
├── rag/
│   ├── api.py           # FastAPI server
│   ├── gemini_rag.py    # Gemini client
│   ├── stores.py        # Store management
│   └── .store_cache.json
├── data/minsal/         # PDFs fuente
└── docs/                # Documentación
```

## PDFs Indexados

| Guía | Store | Páginas clave |
|------|-------|---------------|
| Diabetes Mellitus Tipo 2 | MINSAL_Normativas | HbA1c metas p.6, p.17 |
| Guía ACV 2018 | MINSAL_Medicos | Diagnóstico, tratamiento |
| Guía Asma 2024 | MINSAL_Medicos | Clasificación, farmacología |
| Guía Dengue | MINSAL_Medicos | Manejo clínico |
| Cáncer de Mama | MINSAL_Normativas | Screening, estadificación |
| Cuidados Paliativos | MINSAL_Normativas | Protocolos domiciliarios |

## Validación del RAG

El sistema ha sido validado con preguntas complejas:

| Test | Resultado |
|------|-----------|
| Análisis Excel + cruce MINSAL | ✅ Correcto |
| Citas de páginas específicas | ✅ p.6, p.17 DM2 |
| Anti-hallucination ("NO ENCONTRADO") | ✅ Honesto |
| Artifacts (Chart.js) | ✅ Renderiza |
| Clasificación de riesgo clínico | ✅ Alto/Moderado |

## Open WebUI Integration

1. **Settings → Connections → OpenAI API**
2. URL: `http://host.docker.internal:8100/v1`
3. API Key: `smartsalud-rag-2024`

Ver [docs/OPENWEBUI_INTEGRATION.md](docs/OPENWEBUI_INTEGRATION.md) para detalles.

## Documentación Técnica

| Doc | Contenido |
|-----|-----------|
| [AGENT_TEMPLATE.md](docs/AGENT_TEMPLATE.md) | Template estándar agentes, changelog |
| [OPENWEBUI_INTEGRATION.md](docs/OPENWEBUI_INTEGRATION.md) | Conexión Open WebUI |
| [RAG_GEMINI_SETUP.md](docs/RAG_GEMINI_SETUP.md) | Setup File Search |
