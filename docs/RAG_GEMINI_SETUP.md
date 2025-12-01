# Guía Completa: RAG con Gemini File Search para smartSalud

## Índice

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Arquitectura](#arquitectura)
3. [Requisitos](#requisitos)
4. [Instalación Paso a Paso](#instalación-paso-a-paso)
5. [Configuración de API Key](#configuración-de-api-key)
6. [Estructura de Datos](#estructura-de-datos)
7. [Uso del Sistema](#uso-del-sistema)
8. [Administración de Stores](#administración-de-stores)
9. [Gestión de Documentos](#gestión-de-documentos)
10. [Control de Acceso por Rol](#control-de-acceso-por-rol)
11. [Costos y Límites](#costos-y-límites)
12. [Troubleshooting](#troubleshooting)
13. [Referencias](#referencias)

---

## Resumen Ejecutivo

Sistema de Retrieval-Augmented Generation (RAG) para consulta de guías clínicas MINSAL, implementado con Google Gemini File Search API.

| Aspecto | Detalle |
|---------|---------|
| **Propósito** | Consulta inteligente de protocolos médicos |
| **Tecnología** | Gemini 2.5 Flash + File Search API |
| **Usuarios** | Médicos, Matronas, Secretarias CESFAM |
| **Datos** | Guías clínicas MINSAL (PDF) |

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                      smartSalud RAG                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Usuario    │───▶│  GeminiRAG   │───▶│   Gemini     │  │
│  │  (por rol)   │    │   Client     │    │   2.5 Flash  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                             │                    │          │
│                             ▼                    ▼          │
│                      ┌──────────────┐    ┌──────────────┐  │
│                      │ StoreManager │    │ File Search  │  │
│                      │              │───▶│   Stores     │  │
│                      └──────────────┘    └──────────────┘  │
│                                                 │          │
│                                                 ▼          │
│                                          ┌───────────┐     │
│                                          │  PDFs     │     │
│                                          │  MINSAL   │     │
│                                          └───────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Componentes

| Componente | Archivo | Responsabilidad |
|------------|---------|-----------------|
| `GeminiRAG` | `gemini_rag.py` | Cliente principal, queries |
| `StoreManager` | `stores.py` | CRUD de File Search Stores |
| `DocumentUploader` | `upload.py` | Subida de documentos |

---

## Requisitos

### Sistema

- Python 3.10+
- macOS / Linux / Windows
- Conexión a Internet

### Cuenta Google

1. Cuenta Google con acceso a [AI Studio](https://aistudio.google.com)
2. API Key generada (gratuita)
3. Proyecto con billing habilitado (para uso en producción)

### Dependencias Python

```
google-genai>=0.3.0
python-dotenv>=1.0.0
```

---

## Instalación Paso a Paso

### 1. Clonar/Navegar al Proyecto

```bash
cd /Users/autonomos_dev/Projects/smartSalud_doc
```

### 2. Crear Entorno Virtual

```bash
# Crear venv
python3 -m venv .venv

# Activar (macOS/Linux)
source .venv/bin/activate

# Activar (Windows)
.venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r rag/requirements.txt
```

### 4. Verificar Instalación

```bash
python -c "from google import genai; print('OK')"
```

---

## Configuración de API Key

### Obtener API Key

1. Ir a [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Click "Create API Key"
3. Seleccionar proyecto o crear uno nuevo
4. Copiar la key generada

### Configurar en el Proyecto

**Opción A: Archivo .env (recomendado)**

```bash
# Crear archivo
cp .env.example .env

# Editar
nano .env
```

Contenido:
```
GOOGLE_API_KEY=AIzaSy...tu_key_aqui
```

**Opción B: Variable de entorno**

```bash
export GOOGLE_API_KEY="AIzaSy...tu_key_aqui"
```

### Verificar Conexión

```bash
source .venv/bin/activate
python -c "
from google import genai
import os
from dotenv import load_dotenv
load_dotenv()
client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
r = client.models.generate_content(model='gemini-2.0-flash', contents='Hola')
print('Conexión OK:', r.text[:50])
"
```

---

## Estructura de Datos

### Directorios

```
smartSalud_doc/
├── .env                      # API Key (NO commitear)
├── .env.example              # Template
├── .venv/                    # Entorno virtual
├── data/
│   └── minsal/               # PDFs de guías clínicas
│       ├── DIABETES-MELLITUS-TIPO-2-1.pdf
│       ├── RE-GPC-Ca-de-Mama_06122023.pdf
│       ├── Orientacion-Tecnica-Cuidados-Paliativos-Universales.pdf
│       ├── RES.-EXENTA-N°-741-GUIA-ASMA_2024.pdf
│       ├── 08.-RE_GPC-ACV_2018v3.pdf
│       └── Guia-Practica-Manejo-Clinico-del-DENGUE.pdf
├── docs/
│   └── RAG_GEMINI_SETUP.md   # Esta documentación
└── rag/
    ├── __init__.py
    ├── gemini_rag.py         # Cliente RAG
    ├── stores.py             # Gestión de stores
    ├── upload.py             # Upload de documentos
    ├── test_rag.py           # Tests
    ├── requirements.txt
    ├── README.md
    └── .store_cache.json     # Cache de IDs (auto-generado)
```

### File Search Stores

| Store ID | Display Name | Contenido | Acceso |
|----------|--------------|-----------|--------|
| `fileSearchStores/minsalnormativas-*` | MINSAL_Normativas | Guías generales | Todos |
| `fileSearchStores/minsalmedicos-*` | MINSAL_Medicos | Guías clínicas | Médicos |
| `fileSearchStores/minsalmatronas-*` | MINSAL_Matronas | Protocolos maternidad | Matronas |
| `fileSearchStores/cesfamprocedimientos-*` | CESFAM_Procedimientos | Docs internos | Todos |

---

## Uso del Sistema

### Query Básico (Python)

```python
from rag import GeminiRAG

# Inicializar cliente
rag = GeminiRAG()

# Query simple
result = rag.query_by_role(
    question="¿Cuáles son los síntomas de alerta en diabetes tipo 2?",
    role="medico"
)

print(result['answer'])
print(result['citations'])
```

### Query con Store Específico

```python
from rag import GeminiRAG, StoreManager

rag = GeminiRAG()
manager = StoreManager()

# Obtener ID del store
store_id = manager.get_store_id("MINSAL_Medicos")

# Query directo
result = rag.query(
    question="¿Tratamiento de primera línea para asma?",
    store_ids=[store_id],
    system_prompt="Responde de forma concisa citando la guía."
)
```

### Query Multi-Store

```python
# Buscar en varios stores
store_ids = [
    manager.get_store_id("MINSAL_Normativas"),
    manager.get_store_id("MINSAL_Medicos")
]

result = rag.query(
    question="¿Protocolos de derivación?",
    store_ids=store_ids
)
```

### CLI

```bash
# Activar entorno
source .venv/bin/activate

# Query por rol
python -m rag.gemini_rag "¿Qué es hipoglicemia?" --role medico

# Listar stores
python -m rag.stores list

# Ver stores por rol
python -m rag.stores role --role matrona
```

---

## Administración de Stores

### Crear Stores

```python
from rag import StoreManager

manager = StoreManager()

# Crear todos los stores configurados
stores = manager.create_all_stores()

# Crear uno específico
store_id = manager.create_store("MINSAL_Normativas")
```

### Listar Stores

```python
# Desde cache local
print(manager._store_cache)

# Desde API
stores = manager.list_stores()
for s in stores:
    print(f"{s['display_name']}: {s['name']}")
```

### Eliminar Store

```python
store_id = manager.get_store_id("MINSAL_Matronas")
manager.delete_store(store_id)
```

### Cache de Stores

El archivo `.store_cache.json` mantiene el mapeo nombre → ID:

```json
{
  "MINSAL_Normativas": "fileSearchStores/minsalnormativas-mcsgfa34tpx5",
  "MINSAL_Medicos": "fileSearchStores/minsalmedicos-yvwjate7mq80",
  "MINSAL_Matronas": "fileSearchStores/minsalmatronas-9ez4f4e8xv9o",
  "CESFAM_Procedimientos": "fileSearchStores/cesfamprocedimientos-8yywlm6505bt"
}
```

---

## Gestión de Documentos

### Subir Documento Individual

```python
from rag import DocumentUploader

uploader = DocumentUploader()

# Auto-selección de store según mapping
uploader.upload_file("data/minsal/nueva_guia.pdf")

# Store específico
uploader.upload_file(
    file_path="data/minsal/protocolo.pdf",
    store_name="MINSAL_Matronas",
    display_name="Protocolo Control Prenatal 2024"
)
```

### Subir Directorio Completo

```python
# Subir todos los PDFs
results = uploader.upload_directory("data/minsal/", pattern="*.pdf")

for filename, status in results.items():
    print(f"{filename}: {status}")
```

### Mapping de Documentos

Editar `rag/stores.py`:

```python
DOCUMENT_STORE_MAP = {
    "RE-GPC-Ca-de-Mama_06122023.pdf": "MINSAL_Normativas",
    "Guia-Practica-Manejo-Clinico-del-DENGUE.pdf": "MINSAL_Medicos",
    "RES.-EXENTA-N%C2%B0-741-GUIA-ASMA_2024.pdf": "MINSAL_Medicos",
    # Agregar nuevos documentos aquí
    "nueva_guia_prenatal.pdf": "MINSAL_Matronas",
}
```

### Listar Documentos en Store

```python
files = uploader.list_files_in_store("MINSAL_Normativas")
for f in files:
    print(f"{f['display_name']}: {f['state']}")
```

---

## Control de Acceso por Rol

### Configuración de Roles

En `rag/stores.py`:

```python
STORE_CONFIG = {
    "MINSAL_Normativas": {
        "display_name": "MINSAL Normativas Generales",
        "roles": ["matrona", "medico", "secretaria"],  # Todos
    },
    "MINSAL_Matronas": {
        "display_name": "MINSAL Protocolos Matronas",
        "roles": ["matrona"],  # Solo matronas
    },
    "MINSAL_Medicos": {
        "display_name": "MINSAL Guías Médicos",
        "roles": ["medico"],  # Solo médicos
    },
}
```

### Query por Rol

```python
from rag import GeminiRAG

rag = GeminiRAG()

# El sistema automáticamente filtra los stores según rol
result = rag.query_by_role(
    question="¿Protocolo de control prenatal?",
    role="matrona"  # Solo busca en stores accesibles
)
```

### System Prompts por Rol

```python
# En gemini_rag.py
system_prompts = {
    'matrona': "Eres asistente de maternidad del MINSAL Chile.",
    'medico': "Eres asistente médico con guías clínicas MINSAL.",
    'secretaria': "Eres asistente administrativo del CESFAM."
}
```

---

## Costos y Límites

### Pricing (Nov 2024)

| Operación | Costo | Notas |
|-----------|-------|-------|
| Indexación | $0.15 / 1M tokens | Una vez por documento |
| Storage | Gratis | Hasta 1GB (free tier) |
| Query (Flash) | ~$0.075 / 1M tokens | Por consulta |
| Query (Pro) | ~$1.25 / 1M tokens | Para consultas complejas |

### Límites

| Recurso | Límite Free | Límite Paid |
|---------|-------------|-------------|
| File Search Stores | 10 por proyecto | 10 por proyecto |
| Storage total | 1 GB | 10 GB - 1 TB |
| Archivo individual | 100 MB | 100 MB |
| Requests/minuto | 60 | 1000+ |

### Estimación para smartSalud

```
6 PDFs MINSAL ≈ 50MB ≈ 500K tokens
Indexación única: 500K × $0.15/1M = $0.075

100 queries/día × 1K tokens = 100K tokens/día
Costo diario: 100K × $0.075/1M = $0.0075/día ≈ $0.23/mes
```

---

## Troubleshooting

### Error: GOOGLE_API_KEY not set

```bash
# Verificar variable
echo $GOOGLE_API_KEY

# Cargar .env manualmente
export $(cat .env | xargs)
```

### Error: Store not found

```bash
# Recrear stores
python -m rag.stores create
```

### Error: 500 INTERNAL

- Error temporal de la API
- Solución: Reintentar después de unos segundos

### Error: TIMEOUT en upload

- Documento muy grande
- Solución: Esperar más tiempo o dividir documento

### Error: module 'google.genai.types' has no attribute

```bash
# Actualizar SDK
pip install --upgrade google-genai
```

### Verificar Estado de Stores

```python
from rag import StoreManager

manager = StoreManager()
stores = manager.list_stores()

for s in stores:
    print(f"{s['display_name']}")
    print(f"  ID: {s['name']}")
    print(f"  Created: {s['create_time']}")
```

---

## Referencias

### Documentación Oficial

- [Gemini File Search](https://ai.google.dev/gemini-api/docs/file-search)
- [File Search Stores API](https://ai.google.dev/api/file-search/file-search-stores)
- [Python SDK google-genai](https://pypi.org/project/google-genai/)

### Guías MINSAL Incluidas

| Guía | URL Original |
|------|--------------|
| Diabetes Tipo 2 | [MINSAL](https://diprece.minsal.cl/wrdprss_minsal/wp-content/uploads/2018/01/DIABETES-MELLITUS-TIPO-2-1.pdf) |
| Cáncer de Mama | [MINSAL](https://diprece.minsal.cl/wp-content/uploads/2024/03/RE-GPC-Ca-de-Mama_06122023.pdf) |
| Asma 2024 | [MINSAL](https://diprece.minsal.cl/wp-content/uploads/2024/07/RES.-EXENTA-N%C2%B0-741-GUIA-ASMA_2024.pdf) |
| ACV Isquémico | [MINSAL](https://diprece.minsal.cl/wp-content/uploads/2019/09/08.-RE_GPC-ACV_2018v3.pdf) |
| Dengue | [MINSAL](https://diprece.minsal.cl/wp-content/uploads/2024/03/Guia-Practica-Manejo-Clinico-del-DENGUE.pdf) |
| Cuidados Paliativos | [MINSAL](https://www.minsal.cl/wp-content/uploads/2023/07/Orientacion-Tecnica-Cuidados-Paliativos-Universales.pdf) |

---

*Documento generado: 2024-11-30*
*Versión: 1.0*
