# 🛠️ Guía de Desarrollo Local Open WebUI

## 🌍 Arquitectura Local

Para simplificar el desarrollo y evitar problemas de CORS, utilizamos una arquitectura unificada servida por FastAPI:

*   **Backend (FastAPI)**: Puerto `8080`.
*   **Frontend**: Servido estáticamente por el backend desde `build/`.

🔥 **Puerto Principal**: `http://localhost:8080` (Usar este para todo)

---

## 🚀 Inicio Rápido

Hemos creado un script de utilidad para iniciar el entorno correctamente:

```bash
./start_dev.sh
```

Este script se encarga de:
1. Activar el entorno virtual Python.
2. Definir `FRONTEND_BUILD_DIR` para que el backend sirva la UI.
3. Iniciar el servidor Uvicorn en el puerto 8080.

---

## 📦 Instalación (Si empiezas desde cero)

1. **Backend**:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   mkdir -p backend/data
   ```

2. **Frontend**:
   ```bash
   npm install --legacy-peer-deps
   # Fix para dependencia faltante
   npm install y-protocols --save-dev --legacy-peer-deps
   npm run build
   ```

---

## ⚠️ Notas Técnicas Importantes

### 1. Bloqueo de Inicialización (Fix Aplicado)
Originalmente, Open WebUI bloqueaba la carga de Python al descargar modelos de embeddings (`get_ef`) en el nivel global.
**Solución**: Se movió esta lógica al `lifespan` de FastAPI en `backend/open_webui/main.py`.

### 2. Frontend Build Injection
El backend no detecta automáticamente la carpeta `frontend/` en modo paquete.
**Solución**: Se debe inyectar la ruta del build compilado vía variable de entorno:
`export FRONTEND_BUILD_DIR=$(pwd)/build`

### 3. Puertos
*   **8080**: Servidor Principal (API + Frontend Estático). **Usar este.**
*   **5173** (Vite Dev Server): **NO USAR** a menos que configures proxies manuales. Causa problemas de CORS y sesión.

---

## 🐛 Solución de Problemas

**El servidor inicia pero se queda "pensando"**:
Revisa los logs. Es probable que esté descargando modelos de HuggingFace (`sentence-transformers`) por primera vez. Esto es normal y solo ocurre en el primer arranque.

**Error "Frontend build directory not found"**:
Asegúrate de haber ejecutado `npm run build` y de definir `export FRONTEND_BUILD_DIR=$(pwd)/build` antes de iniciar el backend (o usa `./start_dev.sh`).
