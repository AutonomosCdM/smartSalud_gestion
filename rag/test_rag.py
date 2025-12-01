#!/usr/bin/env python3
"""
Test script for Gemini File Search RAG.

Usage:
    # First, set up environment
    export GOOGLE_API_KEY=your_key

    # Upload documents (only needed once)
    python -m rag.upload upload-all

    # Test queries
    python -m rag.test_rag
"""

import os
from dotenv import load_dotenv

# Load .env file if exists
load_dotenv()


def test_stores():
    """Test store creation and listing."""
    from .stores import StoreManager

    print("\n" + "=" * 60)
    print("TEST: Store Management")
    print("=" * 60)

    manager = StoreManager()

    # Create all stores
    print("\n1. Creating stores...")
    stores = manager.create_all_stores()
    for name, store_id in stores.items():
        print(f"   {name}: {store_id}")

    # List stores
    print("\n2. Listing stores from API...")
    api_stores = manager.list_stores()
    for s in api_stores:
        print(f"   {s['display_name']}")

    # Test role access
    print("\n3. Testing role-based access...")
    for role in ["matrona", "medico", "secretaria"]:
        store_ids = manager.get_stores_for_role(role)
        print(f"   {role}: {len(store_ids)} stores")

    return True


def test_upload():
    """Test document upload."""
    from .upload import DocumentUploader
    from pathlib import Path

    print("\n" + "=" * 60)
    print("TEST: Document Upload")
    print("=" * 60)

    uploader = DocumentUploader()
    data_dir = Path(__file__).parent.parent / "data" / "minsal"

    if not data_dir.exists():
        print(f"   SKIP: Data directory not found: {data_dir}")
        return False

    files = list(data_dir.glob("*.pdf"))
    print(f"\n   Found {len(files)} PDFs to upload")

    # Upload first file as test
    if files:
        print(f"\n   Uploading test file: {files[0].name}")
        try:
            result = uploader.upload_file(files[0])
            print(f"   Result: {result}")
            return True
        except Exception as e:
            print(f"   ERROR: {e}")
            return False

    return True


def test_query():
    """Test RAG queries."""
    from .gemini_rag import GeminiRAG

    print("\n" + "=" * 60)
    print("TEST: RAG Queries")
    print("=" * 60)

    rag = GeminiRAG()

    test_questions = [
        ("medico", "¿Cuáles son los síntomas del dengue grave?"),
        ("medico", "¿Qué tratamiento se recomienda para el asma?"),
        ("matrona", "¿Cuáles son los controles prenatales recomendados?"),
    ]

    for role, question in test_questions:
        print(f"\n[{role.upper()}] {question}")
        print("-" * 50)

        try:
            result = rag.query_by_role(question, role)
            # Truncate answer for display
            answer = result['answer'][:500] + "..." if len(result['answer']) > 500 else result['answer']
            print(f"Respuesta: {answer}")
            if result['citations']:
                print(f"Fuentes: {len(result['citations'])}")
        except Exception as e:
            print(f"ERROR: {e}")

    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("smartSalud RAG Test Suite")
    print("=" * 60)

    if not os.getenv("GOOGLE_API_KEY"):
        print("\nERROR: GOOGLE_API_KEY not set")
        print("Run: export GOOGLE_API_KEY=your_key")
        return

    tests = [
        ("Stores", test_stores),
        ("Upload", test_upload),
        ("Query", test_query),
    ]

    results = {}
    for name, test_fn in tests:
        try:
            results[name] = test_fn()
        except Exception as e:
            print(f"\n   EXCEPTION in {name}: {e}")
            results[name] = False

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"   [{status}] {name}")


if __name__ == "__main__":
    main()
