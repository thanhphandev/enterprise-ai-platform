from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging

logger = logging.getLogger(__name__)

class TextSplitterService:
    """
    Handles chunking of text to preserve context using overlapping.
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
            separators=["\n\n", "\n", " ", ""]
        )

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Splits a list of documents into chunks.
        """
        logger.info(f"Splitting {len(documents)} documents (chunk_size={self.chunk_size}, overlap={self.chunk_overlap})")
        chunks = self.splitter.split_documents(documents)
        logger.info(f"Generated {len(chunks)} chunks.")
        return chunks
