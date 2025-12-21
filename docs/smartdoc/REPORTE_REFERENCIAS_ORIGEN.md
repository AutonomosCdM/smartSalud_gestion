# Auditoría de Referencias Externas: smartDoc

Este informe detalla todas las menciones y enlaces al repositorio original de Open WebUI encontradas en la base de código. Estas referencias son puntos clave para la personalización de la identidad de **smartDoc**.

## 1. Interfaz de Usuario (Frontend)
La mayoría de las referencias visibles para el usuario final se encuentran en componentes Svelte:

- **Sección "About"**: `src/lib/components/chat/Settings/About.svelte` contiene enlaces al GitHub oficial, Discord y redes sociales del proyecto original.
- **Menú de Usuario**: `src/lib/components/layout/Sidebar/UserMenu.svelte` tiene enlaces de soporte y comunidad.
- **Toasts de Actualización**: `src/lib/components/layout/UpdateInfoToast.svelte` apunta al repositorio para descargar nuevas versiones.
- **Página de Error**: `src/routes/error/+page.svelte` sugiere contactar al soporte de Open WebUI.
- **Traducciones**: Múltiples archivos en `src/lib/i18n/locales/` (incluyendo `es-ES`) mencionan "Open WebUI" en las cadenas de texto legales o de bienvenida.

## 2. Lógica del Backend
Referencias técnicas que afectan el funcionamiento o la identificación del servidor:

- **Check de Versión**: `backend/open_webui/main.py` consulta `api.github.com/repos/open-webui/open-webui`.
- **Configuración de Entorno**: `backend/open_webui/env.py` define `OTEL_SERVICE_NAME` como "open-webui" por defecto.
- **Proveedores de RAG**: Algunos loaders en `backend/open_webui/retrieval/` contienen URLs de documentación de Open WebUI.
- **Identificación de Instancia**: `backend/open_webui/main.py` usa metadatos del proyecto original para la cabecera de la documentación de la API.

## 3. Infraestructura y Configuración
Archivos esenciales para el despliegue que conservan la nomenclatura original:

- **Docker**: `docker-compose.yaml` y otros archivos Compose usan nombres de imagen y redes basados en `open-webui`.
- **Kubernetes**: Los manifiestos en `kubernetes/` (Helm charts, PVCs, Ingress) están todos nombrados bajo el prefijo `open-webui`.
- **Gestión de Paquetes**: `package.json` y `pyproject.toml` mantienen el nombre del paquete original para compatibilidad con dependencias.

## 4. Seguridad y Documentación
- **SECURITY.md**: Contiene las instrucciones para reportar vulnerabilidades al equipo original.
- **CHANGELOG.md**: Documenta la historia completa del repositorio original.

---
### Recomendación de Acción
Para una identidad de marca "smartDoc" completa, se recomienda:
1. Reemplazar los enlaces en el componente **About** y **UserMenu**.
2. Actualizar las cadenas de traducción en `es-ES/translation.json`.
3. Modificar el endpoint de actualización en `main.py` si se desea un canal propio de updates.

*Auditoría de Referencias smartDoc - 2025*
