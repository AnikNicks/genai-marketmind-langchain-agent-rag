# Advanced RAG ingestion and retrieval tool for local financial docs

import os
import logging
from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from src import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_vector_db() -> Chroma:
    # checks for extisting entries within vector database
    # if empty, ingests, chunks, and indexes pdfs from data folder
    
    embeddings  = OpenAIEmbeddings(model="text-embedding-3-small")
    
    db_exists = os.path.exists(config.CHROMA_DB_DIR) and len(os.listdir(config.CHROMA_DB_DIR)) > 0
    
    if db_exists:
        logger.info("Chroma DB found. Attaching instance.")
        return Chroma(persist_directory=config.CHROMA_DB_DIR, embedding_function=embeddings)
    
    logger.info("No vector DB found. Processing documents...")
    if not os.path.exists(config.DATA_DIR) or not os.listdir(config.DATA_DIR):
        logger.warning("Data directory is completely empty.")
        return Chroma(persist_directory=config.CHROMA_DB_DIR, embedding_function=embeddings)
    
    loader = PyPDFDirectoryLoader(config.DATA_DIR)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)
    
    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=config.CHROMA_DB_DIR
    )
    return vector_store

# tool to lookup internal company docs, statements, etc.
@tool
def query_internal_financials(query: str) -> str:
    """Use this tool to lookup internal company documents, quarterly statements, 
    historical investor presentations, or corporate policy records."""
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        vector_store = Chroma(persist_directory=config.CHROMA_DB_DIR, embedding_function=embeddings)
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        
        docs = retriever.invoke(query)
        if not docs:
            return "No matching internal documents were found for this query context."
            
        return "\n\n".join([
            f"Source: {d.metadata.get('source', 'N/A')} (Pg {d.metadata.get('page', 'N/A')}):\n{d.page_content}"
            for d in docs
        ])
    except Exception as e:
        return f"An exception occurred running internal document RAG processing: {str(e)}"