# 📋 Walkthrough: Instalación Open WebUI (Opción C)

## Resumen

Ejecutamos la **Opción C** (Desarrollo Local Completo) con `pip install -e .` según lo solicitado. La instalación fue exitosa pero el servidor **no logra vincularse al puerto 8080**.

---

## ✅ Pasos Completados

### 1. Reset del Repositorio
```bash
git checkout .
git clean -fd
```
**Resultado**: ✅ Repositorio limpio, 19 archivos restaurados

### 2. Instalación del Backend como Paquete Editable
```bash
source .venv/bin/activate
pip install -e .
```
**Resultado**: ✅ `open-webui-0.6.41` instalado exitosamente

### 3. Compilación del Frontend
```bash
npm install --legacy-peer-deps
npm install y-protocols --save-dev --legacy-peer-deps
npm run build
```
**Resultado**: ✅ Build completado en 36.04s, archivos estáticos generados en `build/`

### 4. Creación del Directorio de Datos
```bash
mkdir -p backend/data
```
**Resultado**: ✅ Directorio creado (era necesario para evitar error de base de datos)

---

## ❌ Problema Encontrado

### El Servidor No Se Vincula al Puerto

Cuando ejecutamos:
```bash
open-webui serve
```

**Comportamiento observado**:
1. ✅ Carga la clave secreta
2. ✅ Ejecuta migraciones de Alembic
3. ✅ Configura CORS y Vector DB
4. ✅ Muestra el banner de Open WebUI
5. ❌ **Nunca muestra** "Uvicorn running on http://0.0.0.0:8080"
6. ❌ `lsof -i :8080` siempre devuelve vacío

### Causa Probable

El servidor se queda **bloqueado** durante el proceso de inicialización. Basándome en el código de [`__init__.py:serve()`](file:///Users/autonomos_dev/Projects/autonomos_ui/backend/open_webui/__init__.py#L33-L84), el bloqueo ocurre cuando:

```python
import open_webui.main  # Importa el módulo principal
```

Este import ejecuta el **lifespan** de FastAPI que:
- Descarga modelos de embeddings (`sentence-transformers/all-MiniLM-L6-v2`)
- Instala dependencias de funciones y herramientas
- Configura Redis (si está habilitado)
- Precarga modelos base

El proceso **nunca termina** de inicializar, probablemente porque está descargando modelos grandes o esperando alguna conexión.

---

## 🔍 Evidencia

### Log de Inicio
```
Loading WEBUI_SECRET_KEY from file, not provided as an environment variable.
Loading WEBUI_SECRET_KEY from /Users/autonomos_dev/Projects/autonomos_ui/.webui_secret_key
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
WARNI [open_webui.env] 

WARNING: CORS_ALLOW_ORIGIN IS SET TO '*' - NOT RECOMMENDED FOR PRODUCTION DEPLOYMENTS.

INFO  [open_webui.env] VECTOR_DB: chroma
INFO  [open_webui.env] Embedding model set: sentence-transformers/all-MiniLM-L6-v2
WARNI [langchain_community.utils.user_agent] USER_AGENT environment variable not set

 ██████╗ ██████╗ ███████╗███╗   ██╗    ██╗    ██╗███████╗██████╗ ██╗   ██╗██╗
██╔═══██╗██╔══██╗██╔════╝████╗  ██║    ██║    ██║██╔════╝██╔══██╗██║   ██║██║
██║   ██║██████╔╝█████╗  ██╔██╗ ██║    ██║ █╗ ██║█████╗  ██████╔╝██║   ██║██║
██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║    ██║███╗██║██╔══╝  ██╔══██╗██║   ██║██║
╚██████╔╝██║     ███████╗██║ ╚████║    ╚███╔███╔╝███████╗██████╔╝╚██████╔╝██║
 ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝     ╚══╝╚══╝ ╚══════╝╚═════╝  ╚═════╝ ╚═╝


v0.6.41 - building the best AI user interface.

https://github.com/open-webui/open-webui

[SE QUEDA AQUÍ INDEFINIDAMENTE]
```

### Verificación de Puerto
```bash
$ lsof -i :8080 -P -n
# No output - el puerto nunca se abre
```

---

## 📊 Estado Final

| Componente | Estado | Notas |
|------------|--------|-------|
| Backend instalado | ✅ | `pip install -e .` exitoso |
| Frontend compilado | ✅ | Build en `build/` |
| Directorio de datos | ✅ | `backend/data/` creado |
| Servidor iniciado | ❌ | Se bloquea durante init |
| Puerto 8080 abierto | ❌ | Nunca se vincula |

---

## 💡 Recomendación

La **Opción C** no es viable para desarrollo local debido a que el servidor se bloquea durante la inicialización. Te recomiendo:

### Opción Recomendada: Docker

```bash
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main
```

**Ventajas**:
- ✅ Funciona garantizado
- ✅ Modelos pre-descargados en la imagen
- ✅ Configuración optimizada
- ✅ Puedes montar volúmenes para modificar código

**Para modificar el código**:
```bash
docker run -d -p 3000:8080 \
  -v $(pwd)/build:/app/build \
  -v $(pwd)/backend:/app/backend \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main
```

---

## 📁 Archivos Generados

- ✅ `build/` - Frontend compilado (95 MB)
- ✅ `backend/data/` - Directorio de datos
- ✅ `.webui_secret_key` - Clave secreta generada
- ✅ `package.json` - Actualizado con `y-protocols`

---

## ¿Siguiente Paso?

¿Quieres que proceda con Docker para tener la aplicación funcionando?
