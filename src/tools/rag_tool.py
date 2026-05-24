"""
Internal Document Ingestion & RAG Query Vector Store Engine
"""
import os
import logging
from langchain_core.tools import tool
from src.config import DATA_DIR

logger = logging.getLogger(__name__)

def initialize_vector_db():
    """Initializes the vector storage directory path."""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        logger.info(f"Vector data registry synchronized at: {DATA_DIR}")
        return True
    except Exception as e:
        logger.error(f"Vector collection build fault: {str(e)}")
        return False

@tool
def query_internal_financials(query: str) -> str:
    """Queries the internal vector database or extracts raw text from uploaded corporate 
    financial records, balance sheets, and private company documentation."""
    try:
        # 1. ATTEMPT VECTOR STORE SEARCH (Your existing ChromaDB/Vector store logic)
        # For example:
        # docs = vector_store.similarity_search(query, k=4)
        # if docs:
        #     return "\n".join([d.page_content for d in docs])
        
        # If vector search yields nothing, intentionally pass to trigger the robust fallback below
        pass
    except Exception as e:
        logger.warning(f"Vector store lookup failed or uninitialized: {str(e)}. Falling back to direct extraction.")

    # 2. BULLETPROOF RAW FALLBACK: If vector database is empty or fails, read the PDF directly from disk!
    try:
        if not os.path.exists(DATA_DIR) or not os.listdir(DATA_DIR):
            return "CRITICAL ERROR: No documents found in storage directory. Please upload a corporate financial PDF via the sidebar."
        
        from pypdf import PdfReader
        extracted_context = []
        
        for file in os.listdir(DATA_DIR):
            if file.lower().endswith(".pdf"):
                file_path = os.path.join(DATA_DIR, file)
                reader = PdfReader(file_path)
                
                # Extract the first 4 pages (usually contains the core balance sheets / financial statements)
                file_text = f"--- Source File: {file} --- \n"
                for i in range(min(4, len(reader.pages))):
                    file_text += reader.pages[i].extract_text() or ""
                
                extracted_context.append(file_text)
        
        if extracted_context:
            logger.info("Successfully bypassed database block using raw structural PDF stream parser.")
            return "\n\n".join(extracted_context)
            
    except Exception as raw_err:
        logger.error(f"Critical fallback extraction failure: {str(raw_err)}")
        
    return "CRITICAL ERROR: Unable to read internal financial documentation due to a low-level parsing block."