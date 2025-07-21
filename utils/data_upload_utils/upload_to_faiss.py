import os
from dotenv import load_dotenv
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

from utils.logger import get_logger
log = get_logger()

def upload_personal_data():
    log.info("*******************Starting uploading to FAISS...  From data/knowledge_base *******************")
    base_dir = Path(__file__).resolve().parent.parent
    data_path = base_dir / "data" / "knowledge_base"

    if not data_path.exists():
        log.error(f"❌ To Upload Data to Vector DB Folder not found: {data_path}")
        raise FileNotFoundError(f"❌ To Upload Data to Vector DB Folder not found: {data_path}")

    # Load all .txt files
    loader = DirectoryLoader(
        path=str(data_path),
        glob="**/*.txt",
        loader_cls=TextLoader
    )
    raw_docs = loader.load()

    # Add metadata to each doc
    for doc in raw_docs:
        filename = os.path.basename(doc.metadata['source'])
        topic = filename.replace(".txt", "")
        doc.metadata.update({
            "topic": topic
            # "source": topic,
            # "topic": "personal_info",
            # "author": "abc"
        })

    log.info(f"📄 Loaded {len(raw_docs)} raw documents")

    # Split text into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(raw_docs)

    log.info(f"✂️  Created {len(chunks)} chunks")

    # Load embeddings
    #embeddings = OpenAIEmbeddings()  #or use HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Upload to FAISS (stores in memory unless you persist to disk)
    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    # Save to disk (optional but recommended)
    persist_path = base_dir / "vectorstores" / "faiss_index"
    persist_path.parent.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(folder_path=str(persist_path))

    log.info(f"✅ Personal data uploaded to FAISS and saved to {persist_path}")

if __name__ == "__main__":
    upload_personal_data()
