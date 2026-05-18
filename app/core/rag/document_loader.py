import os
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader, UnstructuredExcelLoader
import logging

logger = logging.getLogger(__name__)

class DocumentLoader:
    """
    Utility class to load various document formats into LangChain Document objects.
    """
    
    @staticmethod
    def load_document(file_path: str) -> List[Document]:
        """
        Detect file extension and use appropriate loader.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if ext == '.pdf':
                logger.info(f"Loading PDF (via PyMuPDF): {file_path}")
                loader = PyMuPDFLoader(file_path)
            elif ext in ['.xlsx', '.xls']:
                logger.info(f"Loading Excel: {file_path}")
                loader = UnstructuredExcelLoader(file_path, mode="elements")
            elif ext == '.txt':
                logger.info(f"Loading Text: {file_path}")
                loader = TextLoader(file_path, encoding='utf-8')
            else:
                raise ValueError(f"Unsupported file format: {ext}")
                
            documents = loader.load()
            logger.info(f"Successfully loaded {len(documents)} pages/elements from {file_path}")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {str(e)}")
            raise
