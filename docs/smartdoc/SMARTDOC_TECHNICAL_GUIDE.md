# 🏥 Guía Técnica Maestra: smartDoc + Google Gemini

Esta guía documenta la configuración completa, los ajustes técnicos y la arquitectura del sistema **smartDoc**, una versión personalizada de Open WebUI optimizada para el entorno médico con Google Gemini.

---

## 1. Arquitectura del Sistema

- **Frontend**: SvelteKit (Compilado en `/build`).
- **Backend**: FastAPI (Python 3.11).
- **IA**: Google Gemini (v1beta OpenAI-compatible endpoint).
- **RAG**: Google Embeddings (`text-embedding-004`).

---

## 2. Configuración de Entorno (`run_local.sh`)

La base del sistema reside en las variables de entorno configuradas en `run_local.sh`.

### Variables Críticas:
| Variable | Valor / Propósito |
| :--- | :--- |
| `OPENAI_API_BASE_URLS` | `https://generativelanguage.googleapis.com/v1beta/openai` |
| `OPENAI_API_KEYS` | Tu clave de API de Google AI Studio. |
| `DEFAULT_MODELS` | `gemini-flash-latest` (Pre-selección al iniciar). |
| `RAG_OPENAI_API_BASE_URL` | Mismo endpoint que Gemini para embeddings compatibles. |
| `PORT` | `8080` |

---

## 3. Ajustes del Backend (Fixes y Robustez)

Para garantizar la estabilidad en entornos de producción y la compatibilidad total con Gemini, se han implementado los siguientes parches:

### A. Parche de Middleware (Manejo de Errores)
- **Archivo**: `backend/open_webui/utils/middleware.py`
- **Problema**: La API de Gemini a veces devuelve errores en formato de lista, lo que provocaba un crash (`AttributeError`) en el middleware original orientado a diccionarios.
- **Solución**: Se implementó una lógica de "desempaquetado" de listas y validación de tipos antes de procesar la respuesta JSON de los LLMs.

### B. Router de OpenAI Personalizado
- **Archivo**: `backend/open_webui/routers/openai.py`
- **Cambio crítico**: Se inhabilitó la eliminación automática del prefijo `models/`. Gemini requiere este prefijo (ej: `models/gemini-flash-latest`) para identificar correctamente el recurso.
- **Logs**: Se añadieron logs de depuración detallados para capturar la respuesta cruda de la API en caso de fallos de cuota (error 429).

---

## 4. Manejo de Archivos y RAG

SmartDoc trata cada subida como una entidad única para garantizar la integridad de los datos:
- **UUIDs**: Cada archivo recibe un ID único. Subir el mismo archivo varias veces genera múltiples registros en la DB y múltiples colecciones vectoriales (`file-<uuid>`).
- **Deduplicación**: Actualmente no hay deduplicación global por hash. Esto significa que si se seleccionan archivos duplicados en un chat, el sistema recuperará fragmentos redundantes.
- **Recomendación**: Eliminar versiones antiguas desde la sección "Documentos" para optimizar el contexto de la IA y el almacenamiento.

--- 

## 5. Personalización Visual (Silent Luxury)

SmartDoc ha sido transformado visualmente:
- **Logo**: Ubicado en `/Users/autonomos_dev/.gemini/antigravity/brain/733bfcb5-936b-4364-90ec-bc5dcecbbfd1/smartdoc_logo_luxury_1766266059250.png`.
- **Branding**: El nombre "Open WebUI" fue reemplazado por **smartDoc** en el backend y el `index.html`.
- **Artifacts**: Configurado para que Gemini genere interfaces UI Premium (TailwindCSS) automáticamente mediante el System Prompt.

---

## 6. Resolución de Problemas (FAQ Técnico)

### A. El servidor se queda bloqueado al iniciar
- **Causa**: `pip install` intentando verificar dependencias en cada reinicio.
- **Solución**: Se comentó la línea de `pip install -e .` en `run_local.sh` una vez que el entorno es estable para acelerar el arranque.

### B. "Model not found" o 404
- **Causa**: Endpoint mal configurado o falta el prefijo `models/`.
- **Solución**: Asegurarse que la URL en `run_local.sh` termina en `/openai` (sin la `v1` al final).

---

## 7. Próximos Pasos Recomendados
1.  **GCP Migration**: Implementar el [Plan de Migración](file:///Users/autonomos_dev/.gemini/antigravity/brain/733bfcb5-936b-4364-90ec-bc5dcecbbfd1/implementation_plan.md) utilizando Cloud Run.
2.  **Nuevas Herramientas**: Expandir las capacidades de `SmartDoc Medical Assistant` mediante más scripts de herramientas.

---
*Documentación generada automáticamente por Antigravity - 2025*
