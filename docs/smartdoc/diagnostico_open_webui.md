# 🔍 Diagnóstico del Proyecto Open WebUI

## Resumen Ejecutivo

El proyecto Open WebUI **NO está diseñado para ejecutarse en modo desarrollo local de la forma en que lo estábamos intentando**. Está optimizado para **Docker** o instalación vía **pip** como paquete Python.

---

## Problemas Identificados

### 1. 🐳 **Arquitectura del Proyecto**

Open WebUI tiene una arquitectura donde:
- El **frontend** (SvelteKit) se compila a archivos estáticos (`npm run build`)
- El **backend** (FastAPI) sirve esos archivos estáticos desde `/app/build`
- En producción, **NO hay servidor de desarrollo Vite separado**

El modo `npm run dev` solo funciona si el backend también está corriendo **Y** configurado para permitir CORS desde `localhost:5173`.

### 2. ⚠️ **Cambios Pendientes en Git**

```diff
 backend/open_webui/main.py                         |   4 +-
 backend/open_webui/static/apple-touch-icon.png     | Bin 1658 -> 0 bytes
 backend/open_webui/static/favicon-dark.png         | Bin 15919 -> 0 bytes
 ... (múltiples archivos estáticos eliminados)
 package-lock.json                                  | 666 ++++--
 package.json                                       |   3 +-
 19 files changed, 119 insertions(+), 579 deletions(-)
```

El repositorio tiene:
- Archivos estáticos **eliminados** (favicons, logos, etc.)
- `main.py` modificado (comentamos la función de instalación de dependencias)
- `package.json` modificado (se agregó `y-protocols`)

### 3. 🔌 **Backend No Se Vincula al Puerto**

El backend de Uvicorn aparentemente inicia pero **nunca llega a escuchar en un puerto**:
- El log muestra solo mensajes de inicialización
- Nunca aparece "Uvicorn running on http://0.0.0.0:8080"
- `lsof -i :8080` siempre devuelve vacío

**Causa probable**: El proceso de inicialización se queda bloqueado descargando modelos de embeddings o ejecutando migraciones de base de datos.

### 4. 📦 **Dependencias de NPM con Conflictos**

```
npm error peer @tiptap/core@"^2.7.0" from @tiptap/extension-bubble-menu@2.26.1
Conflicting peer dependency: @tiptap/core@2.27.1
```

El `package.json` tiene conflictos de peer dependencies que solo se resuelven con `--legacy-peer-deps`, lo cual puede causar comportamientos inesperados.

### 5. 🐍 **Módulo Python No Instalable Directamente**

`open_webui` no se puede importar como módulo porque no está instalado como paquete. El proyecto espera que se ejecute desde Docker o se instale vía pip (`pip install open-webui`).

---

## Opciones de Solución

### Opción A: 🐳 **Usar Docker (Recomendado)**

```bash
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main
```

✅ **Ventajas**: Funciona garantizado, sin configuración
❌ **Desventajas**: Más difícil de modificar el código

### Opción B: 📦 **Instalar vía pip**

```bash
pip install open-webui
open-webui serve
```

✅ **Ventajas**: Simple, usa la instalación oficial
❌ **Desventajas**: No permite modificar el código fuente

### Opción C: 🔧 **Desarrollo Local Completo (Complejo)**

1. Resetear el repositorio:
   ```bash
   git checkout .
   git clean -fd
   ```

2. Instalar el backend como paquete editable:
   ```bash
   pip install -e .
   ```

3. Compilar el frontend:
   ```bash
   npm install --legacy-peer-deps
   npm run build
   ```

4. Ejecutar el backend (que sirve el frontend compilado):
   ```bash
   open-webui serve
   ```

✅ **Ventajas**: Control total del código
❌ **Desventajas**: Más pasos, más propenso a errores

---

## Recomendación

Para tu objetivo de **modificar la UI y migrar a GCP**, te recomiendo:

1. **Usar Docker para desarrollo** con un volumen montado para los archivos que quieras modificar
2. O usar la **Opción C** haciendo `pip install -e .` en lugar de intentar ejecutar Uvicorn manualmente

---

## ¿Cómo Proceder?

Por favor indica cuál opción prefieres:
1. **Docker**: Levanto el contenedor oficial
2. **pip install**: Instalo el paquete y lo ejecuto
3. **Desarrollo local completo**: Reseteo el repo y hago la instalación correcta

