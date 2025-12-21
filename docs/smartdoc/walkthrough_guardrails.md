# Walkthrough: smartDoc Guardrails 🛡️

He implementado un sistema robusto de seguridad y cumplimiento clínico diseñado específicamente para **smartDoc**. Este sistema actúa como un middleware inteligente que audita cada interacción.

## Capas de Protección Implementadas

### 1. 🕵️ Anonimización de PII (RUTs Chilenos)
El sistema detecta automáticamente cualquier RUT ingresado por el usuario y lo sustituye por `[RUT ANONIMIZADO]` antes de que los datos salgan hacia el modelo (Gemini), asegurando el cumplimiento con normativas de privacidad.

**Ejemplo de Activación:**
- **Entrada**: "Prescribir paracetamol a Juan Pérez, RUT 12.345.678-9"
- **Procesado**: "Prescribir paracetamol a Juan Pérez, RUT [RUT ANONIMIZADO]"

### 2. 🏥 Validación de Ámbito Profesional
smartDoc ahora distingue entre consultas médicas y triviales. Si un usuario intenta usar la plataforma para fines no médicos, el sistema registra una advertencia y mantiene el contexto clínico.

### 3. ⚖️ Advertencia Legal (Disclaimer)
Cada respuesta que contenga sugerencias de diagnóstico, tratamiento o prescripción incluye automáticamente un disclaimer legal mandatorio.

> *⚠️ **Aviso smartDoc**: Esta información es generada por IA y debe ser validada por un profesional de la salud antes de cualquier decisión clínica. smartDoc no sustituye el juicio médico facultativo.*

### 4. 🧩 Integridad RAG
Si se están utilizando documentos médicos (RAG) pero el modelo genera una respuesta sin citar las fuentes, el sistema añade una nota preventiva:
> 💡 *Nota: Esta respuesta no cita directamente los documentos médicos subidos. Por favor, verifique la concordancia.*

---

## Cómo Administrar los Guardrails

Como Administrador, puedes configurar estos filtros directamente desde la interfaz de smartDoc:

1. Ve a **Ajustes** -> **Funciones**.
2. Busca **smartDoc Guardrails 🛡️**.
3. Puedes activar/desactivar componentes individuales (Anonymization, scope check, disclaimer) mediante los **Valves** (Válvulas).

---

## Verificación Técnica
He ejecutado una suite de pruebas unitarias (`test_guardrails.py`) que valida todos los casos anteriores con éxito.

```bash
✅ Todas las pruebas de lógica pasaron exitosamente.
```
