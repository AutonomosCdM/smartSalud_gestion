# Guía de Uso: smartDoc + Gemini

¡Bienvenido a la nueva experiencia de **smartDoc**! Esta guía te ayudará a configurar y aprovechar al máximo la integración con Google Gemini y el nuevo modo "Canvas".

## 1. Verificación Inicial
Asegúrate de que tu servidor local esté corriendo (`http://localhost:8080`) y que hayas iniciado sesión.

## 2. Selección del Modelo
Para activar la inteligencia de Gemini, es crucial seleccionar el modelo correcto:

1.  En la interfaz de chat (o en "Notes"), busca el **selector de modelos** en la parte superior izquierda.
2.  Despliega la lista y selecciona **`gemini-1.5-flash`** (rápido, ideal para chat) o **`gemini-1.5-pro`** (razonamiento complejo).
    *   *Nota: Si no ves estos modelos, reinicia el servidor y verifica tu conexión a internet.*

## 3. Activando "Gemini Canvas" (Artifacts)
smartDoc tiene la capacidad de generar interfaces gráficas, dashboards y documentos vivos. Para activar esto, recomendamos configurar un **System Prompt** específico.

### Paso A: Configuración
1.  Ve a **Ajustes** (ícono de engranaje) > **Funciones** o **Personalización**.
2.  O bien, al crear un **Nuevo Chat**, busca la configuración de "System Prompt" (Instrucciones del Sistema).
3.  Copia y pega el siguiente prompt:

> **Ver archivo adjunto: `gemini_canvas_prompt.md`**

### Paso B: Cómo usarlo
Una vez configurado, simplemente pídele a Gemini que cree visualizaciones. Ejemplos:
*   *"Crea un dashboard financiero para una clínica con gráficos de barras."*
*   *"Genera una landing page minimalista para un nuevo servicio médico."*
*   *"Dibuja un diagrama de flujo del proceso de triaje."*

Gemini generará un bloque de código HTML que smartDoc renderizará automáticamente como una aplicación interactiva.

## 4. Uso del Módulo "Notes"
El módulo "Notes" sirve para edición colaborativa de documentos largos.
1.  Haz clic en **"Notes"** en la barra lateral.
2.  Escribe `/` para invocar comandos de IA o simplemente pide ayuda en el chat lateral.
3.  **Tip:** Usa `gemini-1.5-pro` en Notes para mejor redacción de informes extensos.

## Solución de Problemas Comunes

| Problema | Solución |
| :--- | :--- |
| **"No se encontraron modelos"** | Verifica que `run_local.sh` no tenga la doble barra `//` en la URL de OpenAI. |
| **El chat no responde** | Asegúrate de haber seleccionado un modelo Gemini válido, no el "Arena" o uno vacío. |
| **Error de conexión** | Revisa la terminal donde corre `run_local.sh` para ver errores en tiempo real. |

---
*smartDoc v0.6.41 - Powered by Google DeepMind Gemini*
