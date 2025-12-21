#!/usr/bin/env bash
set -e # Detener script si hay errores

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Iniciando smartDoc Local - Setup & Run${NC}"

# ==========================================
# 1. Verificación de Entorno Base
# ==========================================
# Asegurar que las rutas comunes de macOS estén en el PATH
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

# Resolve real script path for symlink support
SOURCE=${BASH_SOURCE[0]}
while [ -L "$SOURCE" ]; do
  DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
  SOURCE=$(readlink "$SOURCE")
  [[ $SOURCE != /* ]] && SOURCE=$DIR/$SOURCE
done
SCRIPT_DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
cd "$SCRIPT_DIR"

echo -e "${YELLOW}🔍 Verificando entorno...${NC}"

# Verificar Python 3.11
if ! command -v python3.11 &> /dev/null; then
    echo -e "${RED}❌ Python 3.11 no encontrado. Por favor instálalo.${NC}"
    exit 1
fi

# Verificar Node.js
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ Node.js (npm) no encontrado. Por favor instálalo.${NC}"
    exit 1
fi

# ==========================================
# 2. Setup Backend (Python)
# ==========================================
echo -e "${YELLOW}🐍 Configurando Backend...${NC}"

if [ ! -d ".venv" ]; then
    echo "   Creando virtualenv (.venv)..."
    python3.11 -m venv .venv
fi

source .venv/bin/activate

# Instalar/Actualizar dependencias "in-place"
# echo "   Verificando dependencias Python (esto puede tardar unos segundos)..."
# if ! pip install -e . > /dev/null 2>&1; then
#     echo -e "${RED}⚠️ Error verificando dependencias silenciosamente. Reintentando con logs...${NC}"
#     if ! pip install -e .; then
#          echo -e "${RED}❌ Falló la instalación de dependencias Python.${NC}"
#          exit 1
#     fi
# fi

# Asegurar directorio de datos
mkdir -p backend/data

# ==========================================
# 3. Setup Frontend (Node/Svelte)
# ==========================================
echo -e "${YELLOW}🎨 Configurando Frontend...${NC}"

# Instalar dependencias si node_modules no existe
if [ ! -d "node_modules" ]; then
    echo "   Instalando dependencias NPM (esto puede tardar)..."
    npm install --legacy-peer-deps
    npm install y-protocols --save-dev --legacy-peer-deps
fi

# Compilar si build no existe O si el usuario fuerza rebuild con --rebuild
if [ ! -d "build" ] || [[ "$1" == "--rebuild" ]]; then
    echo "   Compilando Frontend (Build)..."
    npm run build
else
    echo "   ✅ Build frontend detectado (usa --rebuild para forzar recompilación)."
fi

# ==========================================
# 4. Ejecución
# ==========================================
echo -e "${GREEN}✅ Todo listo. Iniciando servidor...${NC}"
echo -e "${GREEN}👉 App disponible en: http://localhost:8080${NC}"

export WEBUI_NAME="smartDoc"
export FRONTEND_BUILD_DIR="$(pwd)/build"
export PORT=8080
export HOST=0.0.0.0
export OPENAI_API_BASE_URLS="https://generativelanguage.googleapis.com/v1beta/openai"
export OPENAI_API_KEYS="AIzaSyDK-gt5Esi0JunS9QtYMwiJKuGNP8U003s"
export DEFAULT_MODELS="gemini-flash-latest"
export RAG_EMBEDDING_ENGINE="openai"
export RAG_EMBEDDING_MODEL="text-embedding-004"
export RAG_OPENAI_API_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai"
export RAG_OPENAI_API_KEY="AIzaSyDK-gt5Esi0JunS9QtYMwiJKuGNP8U003s"
export SRC_LOG_LEVEL_OPENAI="DEBUG"
export SRC_LOG_LEVEL_RAG="DEBUG"
export GLOBAL_LOG_LEVEL="DEBUG"
export TOP_K=3

# Abrir navegador automáticamente (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    (sleep 5 && open http://localhost:8080) &
fi

# Ejecutar servidor
python -m open_webui serve
