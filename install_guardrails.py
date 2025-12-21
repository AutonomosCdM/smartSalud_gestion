import os
import sys
import time
from pathlib import Path

# Configurar el path para importar los modelos de open_webui
# Asumimos que el script se corre desde la raíz del proyecto
CURRENT_DIR = Path.cwd()
sys.path.append(str(CURRENT_DIR / "backend"))

# Configurar variables de entorno para la DB si no están
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "sqlite:///backend/open_webui/data/webui.db"
if "DATA_DIR" not in os.environ:
    os.environ["DATA_DIR"] = "backend/open_webui/data"

try:
    from open_webui.models.functions import Functions, FunctionForm, FunctionMeta
    from open_webui.models.users import Users
    from open_webui.internal.db import get_db, Base
    from sqlalchemy import text
except ImportError as e:
    print(f"Error al importar módulos de open_webui: {e}")
    print("Asegúrate de estar en la raíz del proyecto y tener las dependencias instaladas.")
    sys.exit(1)

def install_smartdoc_guardrails():
    print("🚀 Iniciando instalación de smartDoc Guardrails...")
    
    # 1. Obtener al primer admin
    admin = Users.get_super_admin_user()
    if not admin:
        print("❌ Error: No se encontró un usuario administrador para registrar la función.")
        return

    filter_code = """
'''
title: smartDoc Guardrails 🛡️
author: smartDoc Team
author_url: https://smartdoc.ai
version: 0.1.0
'''

import logging
from typing import Optional
from open_webui.utils.guardrails import SmartDocGuardrails

log = logging.getLogger(__name__)

class Filter:
    def __init__(self):
        self.valves = self.Valves()

    class Valves:
        priority: int = 0
        enable_anonymization: bool = True
        enable_scope_check: bool = True
        enable_disclaimer: bool = True

    def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        # Filtro de entrada para anonimización y validación de ámbito.
        log.info(f"smartDoc Guardrails [Inlet] - Procesando entrada para usuario: {__user__.get('email', 'N/A') if __user__ else 'N/A'}")
        
        if self.valves.enable_anonymization:
            body = SmartDocGuardrails.apply_inlet_guardrails(body)
            
        return body

    def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        # Filtro de salida para disclaimers y validación clínica.
        log.info("smartDoc Guardrails [Outlet] - Procesando salida")
        
        if self.valves.enable_disclaimer:
            if "messages" in body:
                messages = body.get("messages", [])
                if messages:
                    last_msg = messages[-1]
                    if last_msg.get("role") == 'assistant':
                        # Detectar si se usaron fuentes en la respuesta (RAG)
                        has_sources = False
                        if "citations" in body or "sources" in body:
                            has_sources = True
                        
                        last_msg["content"] = SmartDocGuardrails.apply_outlet_guardrails(
                            last_msg["content"], 
                            has_sources=has_sources
                        )
        
        return body
"""

    function_id = "smartdoc_guardrails"
    
    # 3. Preparar datos
    form_data = FunctionForm(
        id=function_id,
        name="smartDoc Guardrails 🛡️",
        content=filter_code,
        meta=FunctionMeta(
            description="Sistema de seguridad clínica: Anonimización de RUTs, validación de ámbito médico y advertencias legales automáticas.",
            manifest={
                "title": "smartDoc Guardrails",
                "author": "smartDoc Team"
            }
        )
    )

    # 4. Insertar o Actualizar
    existing = Functions.get_function_by_id(function_id)
    if existing:
        print(f"🔄 Actualizando filtro existente: {function_id}")
        Functions.update_function_by_id(function_id, {
            "name": form_data.name,
            "content": form_data.content,
            "meta": form_data.meta.model_dump(),
            "is_active": True,
            "is_global": True
        })
    else:
        print(f"✨ Registrando nuevo filtro: {function_id}")
        # Insertar directamente vía SQL o usando el modelo para asegurar campos is_active e is_global
        Functions.insert_new_function(admin.id, "filter", form_data)
        # Forzar activación global
        Functions.update_function_by_id(function_id, {"is_active": True, "is_global": True})

    print("✅ smartDoc Guardrails instalado y activado globalmente.")

if __name__ == "__main__":
    install_smartdoc_guardrails()
