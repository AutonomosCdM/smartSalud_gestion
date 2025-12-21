# Auditoría Técnica de SmartDoc (Open WebUI)

## 1. Visión General del Proyecto
**smartDoc** es una plataforma de interfaz de chat avanzada y extensible, construida sobre la arquitectura de **Open WebUI**. Su objetivo es proporcionar una experiencia de usuario premium ("Silent Luxury") e integración profunda con modelos LLM de vanguardia (Google Gemini).

## 2. Arquitectura del Sistema

### 2.1 Backend (API & Lógica)
*   **Framework**: Python **FastAPI** (Alto rendimiento, asíncrono).
*   **Gestión de Datos**: **SQLAlchemy** (ORM) con SQLite (`webui.db`) para persistencia relacional (Usuarios, Chats, Config).
*   **Migraciones**: **Alembic** para control de versiones del esquema de base de datos.
*   **Vector Database (RAG)**: **ChromaDB** (integrado) para almacenamiento y búsqueda de embeddings de documentos.
*   **Cola de Tareas/Caché**: **Redis** (para caché de modelos, sesiones y colas de tareas asíncronas).
*   **Conectividad LLM**:
    *   Soporte nativo para **Ollama** (modelos locales).
    *   Capa de compatibilidad **OpenAI** (usada para integrar **Google Gemini**).
*   **Punto de Entrada**: `run_local.sh` -> `backend/open_webui/main.py` (Comando `smartdoc serve`).

### 2.2 Frontend (UI/UX)
*   **Framework**: **SvelteKit** (Node.js). Reactivo, ligero y compilado.
*   **Estilos**: Tailwind CSS (utilidades) + CSS personalizado (`static/custom.css` para el tema "Silent Luxury").
*   **Estado**: Gestión de estado reactiva propia de Svelte.
*   **Build**: Vite.
*   **Ubicación**: código fuente en `src/`, compilación en `build/`.

## 3. Sistema RAG (Retrieval-Augmented Generation)

### 3.1 Estado Actual
*   **Motor de Embeddings**: Configurado como `openai` (apuntando a Google Gemini API).
*   **Modelo de Embeddings**: `text-embedding-004` (Google).
*   **Infraestructura**: Se ha migrado de modelos locales pesados (`sentence-transformers`) a API remota de Google para reducir consumo de RAM y evitar bloqueos en el inicio.
*   **Embeddings Endpoint**: `https://generativelanguage.googleapis.com/v1beta/openai/embeddings`.

### 3.2 Flujo de Datos RAG
1.  **Ingesta**: El usuario sube documentos (PDF, TXT, etc.).
2.  **Procesamiento**: El backend divide el texto en chunks.
3.  **Embedding**: Los chunks se envían a Google (`text-embedding-004`) para obtener vectores.
4.  **Almacenamiento**: Vectores se guardan en ChromaDB (local en `backend/data`).
5.  **Recuperación**: Al chatear, la consulta del usuario se vectoriza y busca similitud en ChromaDB.

## 4. Personalizaciones "SmartDoc"
*   **Branding**: Renombrado de "Open WebUI" a "SmartDoc". Logo y favicon personalizados.
*   **Seguridad**: API Keys gestionadas vía variables de entorno (`.env`, `run_local.sh`).
*   **Configuración de Modelos**:
    *   Filtro estricto para mostrar solo **Gemini 2.5 Pro** (y compatibles).
    *   System Prompt inyectado programáticamente para funcionalidad "Gemini Canvas" (generación de artefactos HTML/JS).
*   **Scripts de Utilidad**:
    *   `run_local.sh`: Orquestador de inicio robusto (Backend + Frontend).
    *   `seed_gemini_config.py`: Script para inyección automática de configuración de modelos en DB.

## 5. Recomendaciones de Infraestructura
*   **Cloud Run**: Arquitectura ideal para despliegue. Stateless, escalable.
    *   Requiere persistencia de `backend/data` (SQLite/Chroma) vía **Cloud Storage FUSE** o migrar DB a **Cloud SQL (Postgres)** y RAG a **Vector Search**.
*   **Firebase**: Ideal para hosting del Frontend estático y Auth (si se desacopla del backend).
