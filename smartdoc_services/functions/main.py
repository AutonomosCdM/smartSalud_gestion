from firebase_functions import scheduler_fn, storage_fn
from firebase_admin import initialize_app, storage
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import os
import time

initialize_app()

# Configuración de Gemini (API KEY debe estar en Secret Manager o Environment)
# genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

@scheduler_fn.on_schedule(schedule="every monday 09:00", timeout_sec=540, memory=512)
def scrape_minsal_guides(event: scheduler_fn.ScheduledEvent) -> None:
    """
    Scraper programado:
    1. Accede a las Guías Clínicas GES (Supersalud).
    2. Identifica PDFs de las 87 patologías.
    3. Los descarga y guarda en Firebase Storage ("raw-docs/ges").
    """
    URL_GES = "https://auge.minsal.cl/problemasdesalud/index"
    BUCKET_NAME = "raw-docs"
    
    print(f"Iniciando scraping desde: {URL_GES}")
    
    try:
        bucket = storage.bucket(BUCKET_NAME)
        # auge.minsal.cl no requiere headers complejos, pero es buena práctica mantener un timeout
        response = requests.get(URL_GES, timeout=60)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar enlaces a documentos PDF
        links = soup.find_all('a', href=True)
        count = 0
        
        for link in links:
            href = link['href']
            text = link.get_text(strip=True)
            
            # Filtrar solo PDFs
            if "pdf" in href.lower():
                # Resolver URL relativa
                if not href.startswith('http'):
                    # auge.minsal.cl usa rutas relativas a veces
                    base_url = "https://auge.minsal.cl"
                    if href.startswith('/'):
                        href = f"{base_url}{href}"
                    else:
                        href = f"{base_url}/{href}"
                    
                filename = f"ges/{os.path.basename(href)}"
                blob = bucket.blob(filename)
                
                # Verificar si ya existe (evitar descargas duplicadas)
                if not blob.exists():
                    print(f"Descargando: {text} -> {filename}")
                    pdf_resp = requests.get(href, stream=True, timeout=60)
                    if pdf_resp.status_code == 200:
                        blob.upload_from_string(pdf_resp.content, content_type='application/pdf')
                        # Metadata mapping (Disabled for Local Emulator compatibility)
                        # blob.metadata = {"source": URL_GES, "title": text}
                        # blob.patch() 
                        count += 1
                        print(f"✅ Subido: {filename}")
                    else:
                        print(f"Error descargando PDF: {href}")
        
        print(f"Proceso finalizado. {count} documentos subidos.")
        
    except Exception as e:
        print(f"Error crítico en scraper: {str(e)}")
        raise e

@storage_fn.on_object_finalized(bucket="raw-docs", timeout_sec=300, memory=512)
def sync_to_gemini(event: storage_fn.CloudEvent) -> None:
    """
    Trigger por evento:
    1. Detecta nuevo archivo en Storage.
    2. Lo sube a Gemini File API.
    3. Registra el URI de Gemini en los metadatos del archivo en Storage.
    """
    file_path = event.data.name # e.g., "ges/guia_diabetes.pdf"
    bucket_name = event.data.bucket
    
    # Ignorar si no es PDF
    if not file_path.lower().endswith('.pdf'):
        print(f"Ignorando archivo no PDF: {file_path}")
        return

    print(f"Sincronizando a Gemini: {file_path}")
    
    # API Key desde .env
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY no configurada.")
        return
        
    genai.configure(api_key=api_key)

    bucket = storage.bucket(bucket_name)
    blob = bucket.blob(file_path)
    
    # Descargar temporalmente
    tmp_path = f"/tmp/{os.path.basename(file_path)}"
    blob.download_to_filename(tmp_path)
    
    try:
        # Subir a Gemini File API
        print("Subiendo a Gemini...")
        gemini_file = genai.upload_file(path=tmp_path, display_name=os.path.basename(file_path))
        
        # Poll para estado ACTIVE
        while gemini_file.state.name == "PROCESSING":
            print("Esperando procesamiento...")
            time.sleep(2)
            gemini_file = genai.get_file(gemini_file.name)
            
        if gemini_file.state.name == "ACTIVE":
            print(f"Archivo activo en Gemini: {gemini_file.name}")
            print(f"Sync exitoso: {gemini_file.uri}")
            
            # Metadata update (Disabled for Local Emulator compatibility)
            # metadata = blob.metadata or {}
            # metadata["gemini_uri"] = gemini_file.uri
            # blob.metadata = metadata
            # blob.patch()
        else:
            print(f"Error: Procesamiento fallido en Gemini. Estado: {gemini_file.state.name}")
            
    except Exception as e:
        print(f"Error subiendo a Gemini: {str(e)}")
    finally:
        # Limpieza
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
