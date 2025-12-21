# 🛠️ Guía de Desarrollo smartDoc

## 🌍 Arquitectura del Proyecto

smartDoc es una plataforma médica basada en la arquitectura unificada de FastAPI + SvelteKit:

*   **Backend (FastAPI)**: Puerto `8080`.
*   **Frontend**: Servido estáticamente por el backend desde `build/`.

🔥 **Acceso Local**: [http://localhost:8080](http://localhost:8080)

---

## 🚀 Inicio Rápido (Comando Global)

Hemos habilitado un comando global para simplificar el flujo de trabajo:

```bash
smartdoc
```
o
```bash
smartDoc
```

Este comando ejecuta `run_local.sh`, que realiza las siguientes tareas:
1. **Verificación de Entorno**: Asegura que Python 3.11 y Node.js estén instalados.
2. **Setup Automático**: Crea el entorno virtual (`.venv`) e instala dependencias si no existen.
3. **Optimización de Frontend**: Verifica si hay un build existente; si no, compila la UI.
4. **Lanzamiento**: Inicia el servidor y **abre automáticamente el navegador**.

> [!TIP]
> Usa `smartdoc --rebuild` para forzar la recompilación del frontend si has hecho cambios en la UI.

---

## 📦 Gestión de Dependencias

### 🐍 Backend (Python)
Se recomienda usar Python 3.11+. Las dependencias se gestionan in-place:
```bash
source .venv/bin/activate
pip install -e .
```

### 🎨 Frontend (SvelteKit)
Usamos `npm` con flags específicos para compatibilidad:
```bash
npm install --legacy-peer-deps
npm run build
```

---

## 📂 Documentación Detallada

Para guías más específicas, consulta nuestra carpeta [docs/smartdoc/](file:///Users/autonomos_dev/Projects/autonomos_ui/docs/smartdoc/):

*   [Guía Técnica](file:///Users/autonomos_dev/Projects/autonomos_ui/docs/smartdoc/SMARTDOC_TECHNICAL_GUIDE.md): Arquitectura, RAG y Modelos Gemini.
*   [Guía de Usuario](file:///Users/autonomos_dev/Projects/autonomos_ui/docs/smartdoc/SMARTDOC_USER_GUIDE.md): Manual para personal clínico.
*   [Auditoría de Telemetría](file:///Users/autonomos_dev/Projects/autonomos_ui/docs/smartdoc/AUDITORIA_TELEMETRIA.md): Detalles sobre privacidad y desactivación de tracking.
*   [Solución de Problemas](file:///Users/autonomos_dev/Projects/autonomos_ui/TROUBLESHOOTING.md): Guía para resolver errores comunes.

---

## ⚠️ Notas de Mantenimiento

1. **Variables de Entorno**: El comando `smartdoc` ya configura automáticamente las API Keys de Gemini y los modelos por defecto. No necesitas un archivo `.env` manual para uso local básico.
2. **Conflicto de Puertos**: El script intenta limpiar los puertos 8080, 5173 y 3000 antes de iniciar para evitar conflictos de "Address already in use".
3. **Módulo ejecutable**: El paquete se puede ejecutar con `python -m open_webui serve` gracias al archivo `__main__.py`.
