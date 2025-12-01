# Plan de Ingesta MINSAL

Plan para selección y carga de guías clínicas por departamento CESFAM.

---

## Fase 1: Entrevistas por Departamento

### Objetivo
Cada departamento define qué guías MINSAL necesita en su agente.

### Template Entrevista

| Pregunta | Respuesta |
|----------|-----------|
| Departamento | |
| Entrevistado | |
| Fecha | |
| ¿Qué consultas hacen más frecuentemente? | |
| ¿Qué guías MINSAL usan actualmente (papel/PDF)? | |
| ¿Qué información les falta hoy? | |
| Top 5 guías prioritarias | |

### Departamentos a Entrevistar

| Departamento | Responsable | Agente Destino | Estado |
|--------------|-------------|----------------|--------|
| Medicina General | | smartsalud-medico | ⏳ Pendiente |
| Maternidad/Gineco | | smartsalud-matrona | ⏳ Pendiente |
| Admisión/SOME | | smartsalud-secretaria | ⏳ Pendiente |
| Enfermería | | smartsalud-medico | ⏳ Pendiente |
| Dental | | (nuevo agente?) | ⏳ Pendiente |

---

## Fase 2: Agente DeepResearch

### Propósito
Agente para investigación profunda SIN acceso a datos de pacientes.

| Agente | Propósito | Stores | Acceso Pacientes |
|--------|-----------|--------|------------------|
| smartsalud-deepresearch | Análisis cruzado guías | Todos MINSAL | ❌ NO |

### Configuración

| Campo | Valor |
|-------|-------|
| NOMBRE_AGENTE | Analista Clínico MINSAL |
| ESPECIALIDAD | análisis comparativo y síntesis de múltiples guías |
| STORES | Todos MINSAL (NO pacientes) |
| MODELO | gemini-2.5-pro |
| MAX_TOKENS | 8192 |
| CAPACIDADES | Tablas comparativas, análisis cruzado, síntesis multi-documento |

### Casos de Uso

- "Compara protocolos de diabetes tipo 1 vs tipo 2"
- "¿Qué guías mencionan metformina?"
- "Resume las contraindicaciones de X en todas las guías"

---

## Fase 3: Clasificación de Documentos

### Store Mapping Post-Entrevistas

| Store | Tipo Documentos | Roles con Acceso |
|-------|-----------------|------------------|
| MINSAL_Normativas | Guías GES, normas generales | Todos |
| MINSAL_Medicos | Guías clínicas especializadas | medico, deepresearch |
| MINSAL_Matronas | Protocolos maternidad/gineco | matrona, deepresearch |
| CESFAM_Procedimientos | Flujos internos, admin | secretaria, matrona |
| MINSAL_DeepResearch | Guías completas para análisis | deepresearch |

### Regla de Oro
> **Datos de pacientes = Store separado, NUNCA en deepresearch**

---

## Fase 4: Workflow de Ingesta

```text
1. Entrevista departamento → Lista priorizada
2. Descargar PDFs de minsal.cl
3. Clasificar → Store destino
4. Subir batch (10-15 docs)
5. Test con query de validación
6. Confirmar con departamento
7. Siguiente batch
```

---

## Timeline

| Semana | Actividad |
|--------|-----------|
| 1 | Entrevistas departamentos |
| 2 | Consolidar lista, descargar PDFs |
| 3 | Crear stores faltantes, subir batch 1 |
| 4 | Crear agentes research/deepresearch |
| 5 | Validación con usuarios reales |

---

## Checklist

- [ ] Agendar entrevistas con cada departamento
- [ ] Crear template de entrevista (Google Form?)
- [ ] Definir store MINSAL_DeepResearch
- [ ] Configurar agente deepresearch en Open WebUI
- [ ] Documentar restricción de acceso a datos pacientes
- [ ] Primer batch de ingesta post-entrevistas

---

## Changelog

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2024-11-30 | Plan inicial | Claude/César |
| 2024-11-30 | Eliminar research, solo deepresearch | Claude/César |
