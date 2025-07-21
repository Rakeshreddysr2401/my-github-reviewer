import os
from pathlib import Path
from typing import List

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from utils.logger import get_logger
log = get_logger()

def infer_topic_from_filename(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".java":
        return "java"
    elif ext in [".js", ".jsx", ".tsx"]:
        return "react"
    return "general"

def retrieve_instructions(file_path: str, query: str = "How to review this code?") -> List[str]:
    log.info(f"🔍 Fetching instructions for: {file_path}")
    topic = infer_topic_from_filename(file_path)
    log.info(f"📁 Inferred topic: {topic}")

    base_dir = Path(__file__).resolve().parent
    persist_path = base_dir / "vectorstores" / "faiss_index"

    if not persist_path.exists():
        log.error("❌ Vectorstore not found. Please run `upload_personal_data.py` first.")
        raise FileNotFoundError("Vectorstore not found.")

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.load_local(folder_path=str(persist_path), embeddings=embeddings)
    log.info("📦 Loaded FAISS vectorstore")

    docs = vectorstore.similarity_search(query, k=10)
    log.info(f"🔎 Retrieved {len(docs)} similar documents")

    filtered = [doc.page_content for doc in docs if doc.metadata.get("topic", "").lower() == topic.lower()]
    log.info(f"🧠 Filtered to {len(filtered)} docs with topic: {topic}")

    if not filtered:
        log.warning("⚠️ No exact topic match found. Returning top 3 general docs.")
        return [doc.page_content for doc in docs[:3]]

    return filtered

if __name__ == "__main__":
    file_path = "MyComponent.jsx"
    instructions = retrieve_instructions(file_path)
    print("\n🔍 Relevant Instructions:")
    for i, line in enumerate(instructions, 1):
        print(f"{i}. {line}")
