#!/usr/bin/env bash

# Script de inicio rápido para Open WebUI en modo desarrollo local
# Evita tener que recordar todos los comandos y variables de entorno

echo "🚀 Iniciando entorno de desarrollo Open WebUI..."

# 1. Configurar directorio base
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR" || exit

# 2. Configurar variables de entorno críticas
export FRONTEND_BUILD_DIR="$(pwd)/build"
export PORT=8080
export HOST=0.0.0.0

# 3. Verificar si build existe
if [ ! -d "$FRONTEND_BUILD_DIR" ]; then
    echo "❌ Error: No se encuentra el directorio build/."
    echo "   Por favor ejecuta primero: npm install && npm run build"
    exit 1
fi

# 4. Iniciar servidor
echo "✨ Build frontend detectado en: $FRONTEND_BUILD_DIR"
echo "🔌 Iniciando servidor en http://localhost:$PORT"

source .venv/bin/activate
exec open-webui serve
