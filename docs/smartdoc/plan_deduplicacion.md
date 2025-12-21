# Plan de Implementación: Deduplicación de Archivos en smartDoc

Para optimizar el uso de memoria (RAG) y evitar respuestas redundantes, implementaremos una lógica de deduplicación basada en hashes.

## Cambios Propuestos

### 1. Backend: Modelo de Base de Datos
- **Archivo**: [files.py](file:///Users/autonomos_dev/Projects/autonomos_ui/backend/open_webui/models/files.py)
- **Acción**: Agregar método `get_file_by_hash(self, hash: str, user_id: str)` en `FilesTable`.

### 2. Backend: Router de Archivos (Deduplicación Binaria)
- **Archivo**: [files.py](file:///Users/autonomos_dev/Projects/autonomos_ui/backend/open_webui/routers/files.py)
- **Acción**: 
    - En `upload_file_handler`, calcular el hash SHA256 de los bytes crudos del archivo nada más recibirlo.
    - Consultar si ya existe un archivo con ese hash para el usuario actual.
    - Si existe, devolver el objeto `file_item` existente en lugar de crear uno nuevo y disparar el procesamiento RAG.

### 3. Backend: Procesamiento de Hash de Contenido (Deduplicación de Texto)
- **Archivo**: [retrieval.py](file:///Users/autonomos_dev/Projects/autonomos_ui/backend/open_webui/routers/retrieval.py)
- **Acción**:
    - Asegurar que el hash de contenido (después de extraer el texto) se guarde correctamente.
    - Se podría implementar una lógica donde, incluso si los archivos binarios son diferentes, si el texto extraído es idéntico, se comparta la colección vectorial.

## Beneficios
- **Reducción de Costes**: Menos llamadas a la API de Embeddings de Google.
- **Calidad de Respuesta**: Evitamos que el LLM reciba el mismo fragmento de información 3 veces, dejándole más "espacio" para razonar.
- **Orden**: La sección de documentos no se llenará de duplicados accidentales.

## Verificación
1. Subir un archivo `datos.xlsx`.
2. Volver a subir el mismo archivo (o uno con distinto nombre pero idéntico contenido).
3. Verificar en los logs que el sistema detecta el duplicado y reutiliza el ID existente.
