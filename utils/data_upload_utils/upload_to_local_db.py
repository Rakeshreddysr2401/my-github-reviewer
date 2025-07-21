import os
from dotenv import load_dotenv
from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from utils.logger import get_logger
log = get_logger()

load_dotenv()

def upload_vector_data():
    log.info("🚀 Starting upload to ChromaDB from `data/knowledge_base`")

    base_dir = Path(__file__).resolve().parent.parent.parent
    data_path = base_dir / "data" / "knowledge_base"
    persist_path = base_dir / "vectorstores" / "chroma_db"

    if not data_path.exists():
        log.error(f"❌ Folder not found: {data_path}")
        raise FileNotFoundError(f"❌ To Upload Data to Vector DB Folder not found: {data_path}")

    # Load all .txt files
    loader = DirectoryLoader(path=str(data_path), glob="**/*.txt", loader_cls=TextLoader)
    raw_docs = loader.load()
    log.info(f"📄 Loaded {len(raw_docs)} raw text files")

    # Add topic metadata
    for doc in raw_docs:
        filename = os.path.basename(doc.metadata['source'])
        topic = filename.replace(".txt", "")
        doc.metadata.update({"topic": topic})
    log.info("🏷️  Added 'topic' metadata to all documents")

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(raw_docs)
    log.info(f"✂️  Split into {len(chunks)} document chunks")

    # Load Embeddings
    # embeddings = OpenAIEmbeddings()  #or use HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Create Chroma vectorstore
    persist_path.mkdir(parents=True, exist_ok=True)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(persist_path)
    )

    log.info(f"✅ Vectorstore saved at {persist_path}")

if __name__ == "__main__":
    upload_vector_data()
