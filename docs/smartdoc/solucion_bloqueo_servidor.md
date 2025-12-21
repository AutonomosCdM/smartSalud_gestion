# ✅ Solución Técnica: Bloqueo de Servidor Open WebUI

## 🎯 El Problema
El servidor Uvicorn se iniciaba pero se quedaba "colgado" indefinidamente, sin llegar nunca a ejecutarse ni escuchar en el puerto 8080.
`lsof -i :8080` devolvía vacío.

### Causa Raíz
La aplicación usa un patrón de inicialización global en `backend/open_webui/main.py` donde intenta cargar/descargar modelos de embeddings (`sentence-transformers/all-MiniLM-L6-v2`) en el nivel superior del módulo:

```python
# main.py (Original)
try:
    app.state.ef = get_ef(...) # <--- ESTO BLOQUEA EL IMPORT
except Exception: ...
```

Al ejecutar `open-webui serve` (desde `__init__.py`), se importaba `main`, lo que disparaba esta descarga **antes** de que Uvicorn pudiera tomar el control. Si la descarga tardaba o fallaba silenciosamente, todo el proceso moría por timeout.

## 🛠️ La Solución

### 1. Lazy Loading con Lifespan
Movimos la lógica de inicialización de modelos **dentro del evento `lifespan`** de FastAPI. Esto asegura que:
1. Python importa el módulo instantáneamente.
2. Uvicorn inicia y muestra logs.
3. FastAPI comienza su ciclo de vida.
4. La descarga pesada ocurre de manera controlada (y asíncrona/trazable) sin bloquear el arranque del proceso.

```python
# main.py (Modificado)
@asynccontextmanager
async def lifespan(app: FastAPI):
    ...
    # Lógica movida aquí
    try:
        print("DEBUG: [Lifespan] Inicializando embedding function...", flush=True)
        app.state.ef = get_ef(...)
    ...
```

### 2. Configuración de Frontend
El backend no encontraba los archivos estáticos del frontend. Se solucionó inyectando la variable de entorno correcta apuntando al build que generamos previamente:

```bash
export FRONTEND_BUILD_DIR=$(pwd)/build
```

## 🚀 Resultado
El servidor ahora inicia correctamente y se vincula al puerto 8080.

```
INFO:     Started server process [10710]
INFO:     Waiting for application startup.
DEBUG: [Lifespan] Entrando a lifespan...
...
DEBUG: [Lifespan] Embedding function inicializada.
...
TCP *:8080 (LISTEN)
```

## 📋 Cómo Ejecutar (Development)

Para desarrollo local futuro, usar este comando:

```bash
source .venv/bin/activate
export FRONTEND_BUILD_DIR=$(pwd)/build
open-webui serve
```
