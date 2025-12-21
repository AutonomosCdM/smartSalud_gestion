# Plan de Rebranding Total: smartDoc

Este plan detalla las acciones necesarias para eliminar todas las referencias al repositorio original y consolidar la marca **smartDoc**.

## Cambios Propuestos

### Frontend
- [ ] **[MODIFY] [About.svelte](file:///Users/autonomos_dev/Projects/autonomos_ui/src/lib/components/chat/Settings/About.svelte)**: Eliminar enlaces a GitHub, Discord y redes sociales originales. Cambiar textos descriptivos.
- [ ] **[MODIFY] [UserMenu.svelte](file:///Users/autonomos_dev/Projects/autonomos_ui/src/lib/components/layout/Sidebar/UserMenu.svelte)**: Eliminar enlaces de soporte externo.
- [ ] **[MODIFY] [UpdateInfoToast.svelte](file:///Users/autonomos_dev/Projects/autonomos_ui/src/lib/components/layout/UpdateInfoToast.svelte)**: Ocultar o redirigir notificaciones de actualización.
- [ ] **[MODIFY] [translation.json](file:///Users/autonomos_dev/Projects/autonomos_ui/src/lib/i18n/locales/es-ES/translation.json)**: Reemplazar todas las ocurrencias de "Open WebUI" por "smartDoc".

### Backend
- [ ] **[MODIFY] [main.py](file:///Users/autonomos_dev/Projects/autonomos_ui/backend/open_webui/main.py)**: Inhabilitar por defecto `ENABLE_VERSION_UPDATE_CHECK` y limpiar cabeceras de API.
- [ ] **[MODIFY] [env.py](file:///Users/autonomos_dev/Projects/autonomos_ui/backend/open_webui/env.py)**: Cambiar `OTEL_SERVICE_NAME` y otros valores predeterminados.

### Documentación y Limpieza
- [ ] **[DELETE] [SECURITY.md](file:///Users/autonomos_dev/Projects/autonomos_ui/docs/SECURITY.md)**: Eliminar ya que apunta al equipo original.
- [ ] **[DELETE] [CHANGELOG.md](file:///Users/autonomos_dev/Projects/autonomos_ui/CHANGELOG.md)**: Opcional, o resumir para smartDoc.

## Plan de Verificación
1. **Inspección Visual**: Verificar que la sección "Acerca de" y los menús no muestren enlaces externos.
2. **Logs del Backend**: Asegurar que no haya errores al intentar contactar a GitHub si se inhabilitó el check.
3. **Búsqueda Global**: Ejecutar un `grep` final para confirmar 0 ocurrencias de "open-webui".
