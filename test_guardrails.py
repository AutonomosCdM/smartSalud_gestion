from backend.open_webui.utils.guardrails import SmartDocGuardrails

def test_guardrails():
    print("🧪 Probando smartDoc Guardrails...")
    
    # Test RUT Anonymization
    rut_text = "El paciente con RUT 12.345.678-9 fue atendido."
    anon_text = SmartDocGuardrails.anonymize_rut(rut_text)
    print(f"Original: {rut_text}")
    print(f"Anonimizado: {anon_text}")
    assert "[RUT ANONIMIZADO]" in anon_text
    
    # Test Scope Check
    medical_text = "Se prescribe paracetamol para el síntoma de fiebre."
    pizza_text = "Dime cómo hacer una pizza hawaina."
    
    print(f"¿Es médico? '{medical_text}': {SmartDocGuardrails.is_clinical_context(medical_text)}")
    print(f"¿Es médico? '{pizza_text}': {SmartDocGuardrails.is_clinical_context(pizza_text)}")
    
    assert SmartDocGuardrails.is_clinical_context(medical_text) == True
    assert SmartDocGuardrails.is_clinical_context(pizza_text) == False
    
    # Test Disclaimer
    response = "El diagnóstico sugiere una gripe común."
    final_response = SmartDocGuardrails.apply_outlet_guardrails(response)
    print(f"Respuesta con Disclaimer: {final_response}")
    assert "Aviso smartDoc" in final_response

    print("\n✅ Todas las pruebas de lógica pasaron exitosamente.")

if __name__ == "__main__":
    test_guardrails()
