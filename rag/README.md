# smartSalud RAG - Gemini File Search

Sistema de consulta de guías clínicas MINSAL usando Google Gemini File Search API.

## Instalación

```bash
cd /Users/autonomos_dev/Projects/smartSalud_doc

# 1. Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 2. Instalar dependencias
pip install -r rag/requirements.txt
```

## Configuración

```bash
# Copiar template
cp .env.example .env

# Editar con tu API key
# Obtener de: https://aistudio.google.com/apikey
```

| Variable | Descripción |
|----------|-------------|
| `GOOGLE_API_KEY` | API key de Google AI Studio |

## Estructura de Stores

| Store | Contenido | Roles |
|-------|-----------|-------|
| `MINSAL_Normativas` | Guías generales (Diabetes, Cáncer, Paliativos) | Todos |
| `MINSAL_Medicos` | Guías clínicas (Asma, ACV, Dengue) | Médicos |
| `MINSAL_Matronas` | Protocolos maternidad | Matronas |
| `CESFAM_Procedimientos` | Procedimientos internos | Todos |

## Datos Incluidos

| Documento | Fuente | Store |
|-----------|--------|-------|
| Guía Diabetes Tipo 2 | MINSAL 2018 | Normativas |
| Guía Cáncer de Mama | MINSAL 2024 | Normativas |
| Cuidados Paliativos | MINSAL 2023 | Normativas |
| Guía Asma | MINSAL 2024 | Medicos |
| Guía ACV Isquémico | MINSAL 2018 | Medicos |
| Guía Dengue | MINSAL 2024 | Medicos |

## Uso

### Query Simple

```python
from rag import GeminiRAG

rag = GeminiRAG()
result = rag.query_by_role(
    question="¿Síntomas de alerta en diabetes?",
    role="medico"
)
print(result['answer'])
```

### Query con Store Específico

```python
from rag import GeminiRAG, StoreManager

rag = GeminiRAG()
manager = StoreManager()

store_id = manager.get_store_id("MINSAL_Medicos")
result = rag.query(
    question="¿Tratamiento primera línea asma?",
    store_ids=[store_id]
)
```

### CLI

```bash
# Query por rol
python -m rag.gemini_rag "¿Qué es la hipoglicemia?" --role medico

# Gestión de stores
python -m rag.stores list
python -m rag.stores role --role matrona

# Upload documentos
python -m rag.upload upload-all
python -m rag.upload upload --file nuevo.pdf --store MINSAL_Normativas
```

## Agregar Documentos

```bash
# 1. Copiar PDF a data/minsal/
cp guia_nueva.pdf data/minsal/

# 2. Editar mapping en rag/stores.py
DOCUMENT_STORE_MAP = {
    ...
    "guia_nueva.pdf": "MINSAL_Normativas",
}

# 3. Subir
python -m rag.upload upload --file data/minsal/guia_nueva.pdf
```

## Costos

| Operación | Costo |
|-----------|-------|
| Indexación | $0.15 / 1M tokens (una vez) |
| Storage | Gratis hasta 1GB |
| Query (Flash) | ~$0.075 / 1M tokens |

## Archivos

```
rag/
├── __init__.py          # Exports
├── gemini_rag.py        # Cliente RAG
├── stores.py            # Gestión stores
├── upload.py            # Upload docs
├── test_rag.py          # Tests
├── requirements.txt     # Dependencias
└── .store_cache.json    # IDs stores (auto)
```

## Dependencias

```
google-genai>=0.3.0      # SDK Gemini
python-dotenv>=1.0.0     # Env vars
```

## Troubleshooting

| Error | Solución |
|-------|----------|
| `GOOGLE_API_KEY not set` | Configurar `.env` |
| `Store not found` | Ejecutar `python -m rag.stores create` |
| `500 INTERNAL` | Error temporal API, reintentar |
| `TIMEOUT` | Documento muy grande, esperar más |
