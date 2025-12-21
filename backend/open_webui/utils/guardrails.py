import re
import logging

log = logging.getLogger(__name__)

class SmartDocGuardrails:
    # Patrón para RUT Chileno (con o sin puntos/guion)
    RUT_PATTERN = r'\b(\d{1,2}(?:[\.]?\d{3}){2}-[\dkK])\b'
    
    # Lista básica de palabras clave clínicas para el clasificador de ámbito
    CLINICAL_KEYWORDS = [
        "paciente", "clínica", "síntoma", "diagnóstico", "tratamiento", "examen",
        "médico", "salud", "hospital", "farmacia", "receta", "dolor", "fiebre",
        "anamnesis", "epicrisis", "interconsulta", "historia", "ficha", "clinica"
    ]

    @staticmethod
    def anonymize_rut(text: str) -> str:
        """Anonimiza RUTs detectados sustituyéndolos por [RUT ANONIMIZADO]."""
        return re.sub(SmartDocGuardrails.RUT_PATTERN, "[RUT ANONIMIZADO]", text)

    @staticmethod
    def is_clinical_context(text: str) -> bool:
        """Verifica si el texto parece ser clínico o administrativo de salud."""
        text_lower = text.lower()
        # Si tiene alguna palabra clave o es lo suficientemente largo para ser un reporte
        has_keywords = any(kw in text_lower for kw in SmartDocGuardrails.CLINICAL_KEYWORDS)
        # Permitir saludos o textos muy cortos para no ser obstructivo
        if len(text_lower) < 15:
            return True
        return has_keywords

    @staticmethod
    def get_medical_disclaimer() -> str:
        """Retorna el aviso legal mandatorio de smartDoc."""
        return (
            "\n\n---\n"
            "*⚠️ **Aviso smartDoc**: Esta información es generada por IA y debe ser validada por un profesional de la salud "
            "antes de cualquier decisión clínica. smartDoc no sustituye el juicio médico facultativo.*"
        )

    @staticmethod
    def apply_inlet_guardrails(form_data: dict) -> dict:
        """Aplica filtros a la entrada antes de enviarla al LLM."""
        if "messages" in form_data:
            for message in form_data["messages"]:
                if message.get("role") == "user":
                    content = message.get("content", "")
                    # 1. Anonimización
                    message["content"] = SmartDocGuardrails.anonymize_rut(content)
                    
                    # 2. Validación de ámbito (opcionalmente podríamos lanzar error, 
                    # pero por ahora solo logueamos o marcamos metadatos)
                    if not SmartDocGuardrails.is_clinical_context(content):
                        log.warning(f"Posible consulta fuera de ámbito: {content[:50]}...")
        
        return form_data

    @staticmethod
    def apply_outlet_guardrails(response_text: str, has_sources: bool = False) -> str:
        """Aplica filtros a la salida antes de mostrarla al usuario."""
        # 1. Avisar si no hay citaciones cuando se usaron fuentes (Integridad RAG)
        if has_sources and "[[" not in response_text and "fuente" not in response_text.lower():
             response_text = "💡 *Nota: Esta respuesta no cita directamente los documentos médicos subidos. Por favor, verifique la concordancia.*\n\n" + response_text

        # 2. Añadir disclaimer si detectamos contenido clínico
        if any(kw in response_text.lower() for kw in ["diagnóstico", "tratamiento", "receta", "sugerimos", "prescribe"]):
            response_text += SmartDocGuardrails.get_medical_disclaimer()
            
        return response_text
