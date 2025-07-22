import os

from utils.data_retrieve_utils.guidelines_store_wrapper import GuidelineStore
from utils.data_upload_utils.upload_to_local_db import upload_vector_data
from pathlib import Path

def ensure_vectorstore_exists():
    base_dir = Path(__file__).resolve().parent.parent
    persist_path = base_dir / "vectorstores" / "chroma_db"

    if not os.path.exists(persist_path) or not os.listdir(persist_path):
        print("⚠️ Vectorstore not found or empty. Uploading guideline data...")
        upload_vector_data()
        print("✅ Vectorstore created.")
    else:
        print("✅ Vectorstore already exists.")


def ensure_vectorstore_exists_and_get():
    base_dir = Path(__file__).resolve().parent.parent
    persist_path = base_dir / "vectorstores" / "chroma_db"

    if not os.path.exists(persist_path) or not os.listdir(persist_path):
        print("⚠️ Vectorstore not found or empty. Uploading guideline data...")
        upload_vector_data()
        print("✅ Vectorstore created.")

    return GuidelineStore()

