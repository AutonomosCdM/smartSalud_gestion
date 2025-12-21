# Auditoría de Privacidad y Telemetría: smartDoc

He realizado un recorrido exhaustivo por el código fuente para identificar cualquier forma de monitoreo externo o envío de telemetría. Este informe detalla los hallazgos para smartDoc.

## 1. Telemetría de Backend (OpenTelemetry)
- **Estado**: **DESACTIVADO por defecto**.
- **Detalle**: El sistema tiene capacidad para integrarse con OpenTelemetry (OTEL) para métricas y trazas, pero la variable `ENABLE_OTEL` en `env.py` está configurada como `False`. 
- **Conexión**: Si se activara, intentaría contactar a `http://localhost:4317` (un recolector local) a menos que se configure una URL externa.

## 2. Conexiones Externas Identificadas
Existen tres puntos específicos donde la aplicación puede contactar servidores externos:

| Servicio | Destino | Disparador | Privacidad |
| :--- | :--- | :--- | :--- |
| **Check de Versión** | GitHub API | Manual (Sección Versión) | No envía datos sensibles, solo pide la última versión. |
| **Licencias** | openwebui.com | Opcional | Solo ocurre si el usuario ingresa una `LICENSE_KEY`. |
| **RAG / Search** | Google/Tavily/etc. | Opcional | Solo si el administrador activa "Web Search" y añade sus propias API Keys. |

## 3. Auditoría de Frontend (Browser)
- **Scripts de Seguimiento**: No se detectaron scripts de terceros como Google Analytics, Hotjar, Sentry o PostHog en el archivo principal `app.html` ni en la configuración de construcción `vite.config.ts`.
- **Modo Offline**: El sistema está diseñado para soportar `OFFLINE_MODE`, lo que inhabilita incluso la verificación de versiones en GitHub.

## 4. Conclusión de Seguridad Médica
La arquitectura actual de smartDoc es **altamente privada**. No existe ningún mecanismo de "phone home" o reporte de uso anónimo automático hacia los desarrolladores originales. Los datos de los pacientes y las interacciones médicas permanecen dentro de tu infraestructura local.

**Recomendación**: Mantener `ENABLE_OTEL=False` y no configurar `LICENSE_KEY` para garantizar un aislamiento total.

---
*Reporte de Auditoría smartDoc - 2025*
