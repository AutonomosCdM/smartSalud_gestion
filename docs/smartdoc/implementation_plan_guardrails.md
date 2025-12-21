# Plan de Implementación: smartDoc Guardrails 🛡️

Este plan detalla la creación de un sistema de seguridad y cumplimiento para smartDoc, diseñado para proteger la privacidad del paciente y asegurar la responsabilidad clínica del asistente.

## Propuesta de Guardrails

### 1. Sistema de Anonimización (Guardrail de Entrada)
- **Objetivo**: Detectar y anonimizar datos sensibles como RUTs chilenos y nombres completos antes de que salgan al modelo (Gemini).
- **Lógica**: Uso de Regex para RUT (`XX.XXX.XXX-X`) y procesamiento de lenguaje natural básico para nombres.

### 2. Clasificador de Ámbito (Guardrail de Entrada)
- **Objetivo**: Asegurar que smartDoc se utilice exclusivamente para fines profesionales/clínicos.
- **Lógica**: Si la consulta es trivial o fuera de contexto (ej. "dame una receta de pizza"), el sistema responderá: *"smartDoc está optimizado exclusivamente para consultas clínicas y administrativas de salud."*

### 3. Disclaimer Médico Dinámico (Guardrail de Salida)
- **Objetivo**: Cumplir con normativas legales añadiendo avisos de responsabilidad.
- **Lógica**: Se añade automáticamente al final de cada respuesta que contenga sugerencias clínicas.

### 4. Filtro de Integridad RAG (Guardrail de Salida)
- **Objetivo**: Mitigar alucinaciones comparando la respuesta con las fuentes recuperadas.
- **Lógica**: Si el modelo afirma algo que no está en los documentos (o lo contradice), se marca una alerta visual.

## Modificaciones Propuestas

### [Backend]

#### [NEW] [guardrails.py](file:///Users/autonomos_dev/Projects/autonomos_ui/backend/open_webui/utils/guardrails.py)
Creación de un módulo centralizado de lógica de seguridad.

#### [MODIFY] [middleware.py](file:///Users/autonomos_dev/Projects/autonomos_ui/backend/open_webui/utils/middleware.py)
Integración de los guardrails en el flujo de peticiones.

#### [NEW] [smartdoc_guardrails_plugin.py](file:///Users/autonomos_dev/Projects/autonomos_ui/backend/open_webui/functions/smartdoc_guardrails_plugin.py)
Creación de un "Filter Plugin" que el usuario puede activar/desactivar desde la UI.

## Plan de Verificación

### Pruebas Manuales
1. **Privacidad**: Intentar ingresar un RUT y verificar que el log (o la entrada al modelo) esté anonimizada.
2. **Ámbito**: Preguntar algo no médico y verificar el bloqueo.
3. **Legal**: Verificar que el disclaimer aparezca en todas las respuestas clínicas.
