"""
Upload documents to Gemini File Search stores.

Handles uploading PDFs to the appropriate stores based on document type.
"""

import os
import time
from pathlib import Path
from typing import Optional
from google import genai

from .stores import StoreManager, DOCUMENT_STORE_MAP


class DocumentUploader:
    """Uploads documents to Gemini File Search stores."""

    def __init__(self, client: Optional[genai.Client] = None):
        """Initialize uploader.

        Args:
            client: Gemini client. If None, creates from env.
        """
        if client:
            self.client = client
        else:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not set")
            self.client = genai.Client(api_key=api_key)

        self.store_manager = StoreManager(self.client)

    def upload_file(
        self,
        file_path: str | Path,
        store_name: Optional[str] = None,
        display_name: Optional[str] = None
    ) -> str:
        """Upload a single file to a store.

        Args:
            file_path: Path to the file.
            store_name: Target store name. If None, auto-selects based on filename.
            display_name: Display name for the file. If None, uses filename.

        Returns:
            File name/ID from the API.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Auto-select store if not specified
        if not store_name:
            store_name = self.store_manager.get_target_store(file_path.name)

        # Get or create store
        store_id = self.store_manager.get_store_id(store_name)
        if not store_id:
            store_id = self.store_manager.create_store(store_name)

        # Set display name
        if not display_name:
            display_name = file_path.stem.replace("-", " ").replace("_", " ")

        print(f"Uploading '{file_path.name}' to store '{store_name}'...")

        # Upload file
        operation = self.client.file_search_stores.upload_to_file_search_store(
            file=str(file_path),
            file_search_store_name=store_id,
            config={"display_name": display_name}
        )

        # Wait for processing
        print("  Processing...", end="", flush=True)
        while not operation.done:
            time.sleep(2)
            print(".", end="", flush=True)
        print(" Done!")

        return operation.result().name if hasattr(operation.result(), 'name') else str(operation.result())

    def upload_directory(
        self,
        directory: str | Path,
        pattern: str = "*.pdf"
    ) -> dict[str, str]:
        """Upload all matching files from a directory.

        Args:
            directory: Directory path.
            pattern: Glob pattern for files.

        Returns:
            Dict mapping filenames to file IDs.
        """
        directory = Path(directory)
        if not directory.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory}")

        results = {}
        files = list(directory.glob(pattern))

        print(f"\nUploading {len(files)} files from {directory}...")
        print("=" * 60)

        for i, file_path in enumerate(files, 1):
            print(f"\n[{i}/{len(files)}] {file_path.name}")
            try:
                file_id = self.upload_file(file_path)
                results[file_path.name] = file_id
            except Exception as e:
                print(f"  ERROR: {e}")
                results[file_path.name] = f"ERROR: {e}"

        print("\n" + "=" * 60)
        print(f"Uploaded: {sum(1 for v in results.values() if not v.startswith('ERROR'))}/{len(files)}")

        return results

    def list_files_in_store(self, store_name: str) -> list[dict]:
        """List all files in a store.

        Args:
            store_name: Store name.

        Returns:
            List of file info dicts.
        """
        store_id = self.store_manager.get_store_id(store_name)
        if not store_id:
            raise ValueError(f"Store not found: {store_name}")

        files = list(self.client.file_search_stores.list_files(name=store_id))
        return [
            {
                "name": f.name,
                "display_name": f.display_name if hasattr(f, 'display_name') else None,
                "state": str(f.state) if hasattr(f, 'state') else None
            }
            for f in files
        ]


def upload_minsal_docs():
    """Upload all MINSAL documents from data/minsal/ directory."""
    data_dir = Path(__file__).parent.parent / "data" / "minsal"

    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}")
        return

    uploader = DocumentUploader()

    # First create all stores
    print("Creating stores...")
    uploader.store_manager.create_all_stores()

    # Then upload documents
    results = uploader.upload_directory(data_dir)

    print("\n\nUpload Summary:")
    print("-" * 40)
    for filename, result in results.items():
        status = "OK" if not result.startswith("ERROR") else "FAIL"
        print(f"  [{status}] {filename}")


# CLI usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Upload documents to File Search")
    parser.add_argument("action", choices=["upload", "upload-all", "list"])
    parser.add_argument("--file", help="File to upload")
    parser.add_argument("--store", help="Target store name")
    parser.add_argument("--dir", help="Directory to upload")
    args = parser.parse_args()

    if args.action == "upload" and args.file:
        uploader = DocumentUploader()
        uploader.upload_file(args.file, args.store)

    elif args.action == "upload-all":
        upload_minsal_docs()

    elif args.action == "list" and args.store:
        uploader = DocumentUploader()
        files = uploader.list_files_in_store(args.store)
        print(f"\nFiles in '{args.store}':")
        for f in files:
            print(f"  - {f['display_name']}: {f['state']}")
