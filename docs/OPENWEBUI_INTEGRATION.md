# Integración Open WebUI + RAG MINSAL

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

## Requisitos

| Componente | Estado |
|------------|--------|
| RAG API corriendo | `http://localhost:8100` |
| Open WebUI instalado | Docker o local |

## Paso 1: Iniciar RAG API

```bash
cd /Users/autonomos_dev/Projects/smartSalud_doc
source .venv/bin/activate
uvicorn rag.api:app --host 0.0.0.0 --port 8100
```

Verificar:
```bash
curl -H "Authorization: Bearer smartsalud-rag-2024" http://localhost:8100/v1/models
```

## Paso 2: Configurar Open WebUI

### Opción A: Agregar como "OpenAI Connection"

1. Abrir Open WebUI → **Settings** → **Connections**
2. En "OpenAI API":
   - URL: `http://host.docker.internal:8100/v1` (Docker) o `http://localhost:8100/v1` (local)
   - API Key: `smartsalud-rag-2024`
3. Click **Save**
4. Los modelos aparecerán:
   - `smartsalud-rag` (default)
   - `smartsalud-medico`
   - `smartsalud-matrona`
   - `smartsalud-secretaria`

### Opción B: Docker Compose

```yaml
version: '3.8'
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    environment:
      - OPENAI_API_BASE_URLS=http://host.docker.internal:8100/v1
      - OPENAI_API_KEYS=smartsalud-rag-2024
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

## Paso 3: Usar

1. Abrir Open WebUI
2. Seleccionar modelo `smartsalud-medico` (o el rol correspondiente)
3. Hacer preguntas sobre guías MINSAL:
   - "¿Qué es la diabetes tipo 2?"
   - "¿Tratamiento para asma?"
   - "¿Síntomas de ACV?"

## Modelos Disponibles

| Modelo | Acceso | Uso |
|--------|--------|-----|
| `smartsalud-rag` | Todos los stores | Consultas generales |
| `smartsalud-medico` | MINSAL_Normativas + MINSAL_Medicos | Para médicos |
| `smartsalud-matrona` | MINSAL_Normativas + MINSAL_Matronas | Para matronas |
| `smartsalud-secretaria` | MINSAL_Normativas + CESFAM_Procedimientos | Administrativo |

## Troubleshooting

| Error | Solución |
|-------|----------|
| Connection refused | Verificar RAG API corriendo en puerto 8100 |
| host.docker.internal no resuelve | Agregar `extra_hosts` en docker-compose |
| No models found | Verificar endpoint `/v1/models` responde |
| CORS error | Ya configurado en `api.py`, verificar URL |

## Verificar Conectividad

```bash
# Desde host
curl -H "Authorization: Bearer smartsalud-rag-2024" http://localhost:8100/v1/models

# Desde container Docker
docker exec -it open-webui curl -H "Authorization: Bearer smartsalud-rag-2024" \
  http://host.docker.internal:8100/v1/models
```

## Test Query

```bash
curl -X POST http://localhost:8100/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer smartsalud-rag-2024" \
  -d '{"model":"smartsalud-medico","messages":[{"role":"user","content":"Que es diabetes?"}]}'
```

## Seguridad

| Variable | Valor | Ubicación |
|----------|-------|-----------|
| `RAG_API_KEY` | `smartsalud-rag-2024` | `.env` |

Para cambiar la API Key:

1. Editar `.env` → `RAG_API_KEY=nueva-key`
2. Reiniciar API
3. Actualizar en Open WebUI → Settings → Connections
