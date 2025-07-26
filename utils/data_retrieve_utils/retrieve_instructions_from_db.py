import os
from pathlib import Path
from typing import List

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from utils.logger import get_logger
log = get_logger()

def infer_topic_from_filename(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".java":
        return "java_instruction"
    elif ext in [".js", ".jsx", ".tsx"]:
        return "react_instructions"
    elif ext == ".py":
        return "python_instructions"
    elif ext == "general":
        return "general_instructions"
    return "default"

def retrieve_instructions(file_path: str="default", query: str = "How to review this code?") -> List[str]:
    topic = infer_topic_from_filename(file_path)
    log.info(f"🔍 Fetching instructions for: {file_path}  on   📁 Inferred topic: {topic}")
    base_dir = Path(__file__).resolve().parent.parent.parent
    persist_path = base_dir / "vectorstores" / "chroma_db"

    if not persist_path.exists():
        log.error("❌ Vectorstore not found. Please run `upload_vector_data.py` first.")
        raise FileNotFoundError("Vectorstore not found.")

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory=str(persist_path)
    )
    log.debug("📦 Loaded Chroma vectorstore")

   #todo if we use qdrant or other vectorstore, we can retrive data based on direct meta data instead of going through all files
    docs = vectorstore.similarity_search(query, k=10)
    log.debug(f"🔎 Retrieved {len(docs)} similar documents")

    if topic == "default":
        log.info("📝 No specific topic provided, returning top 3 general docs.")
        return [doc.page_content for doc in docs[:3]]

    filtered = [doc.page_content for doc in docs if doc.metadata.get("topic", "").lower() == topic.lower()]
    log.info(f"🧠 Filtered to {len(filtered)} docs with topic: {topic}")

    if not filtered:
        log.warning("⚠️ No exact topic match found. Returning top 3 general docs.")
        return [doc.page_content for doc in docs[:3]]

    return filtered[:5]

if __name__ == "__main__":
    file_path = "MyComponent.jsx"
    instructions = retrieve_instructions(file_path)
    print("\n🔍 Relevant Instructions:")
    for i, line in enumerate(instructions, 1):
        print(f"{i}. {line}")
