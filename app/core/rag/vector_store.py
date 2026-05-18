import os
from typing import List
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.utils import filter_complex_metadata
from chromadb.config import Settings
import chromadb
import logging

logger = logging.getLogger(__name__)

class VectorStoreService:
    """
    Manages the Vector Database (ChromaDB) for storing and retrieving document embeddings.
    """
    
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "enterprise_knowledge"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Use a high-quality lightweight local embedding model to save costs
        # Alternatively, this can be swapped with OpenAIEmbeddings or GoogleGenerativeAIEmbeddings
        logger.info("Initializing HuggingFace Embeddings (Local)...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize ChromaDB with anonymized telemetry disabled for privacy & performance
        os.makedirs(self.persist_directory, exist_ok=True)
        client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        self.vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            client=client
        )

    def add_documents(self, documents: List[Document]):
        """
        Embeds and stores documents in ChromaDB.
        """
        filtered_docs = filter_complex_metadata(documents)
        logger.info(f"Adding {len(filtered_docs)} chunks to Vector Store (ChromaDB)...")
        self.vector_store.add_documents(filtered_docs)
        logger.info("Documents successfully indexed and persisted.")

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """
        Retrieve top K most relevant document chunks based on semantic similarity.
        """
        logger.info(f"Performing similarity search for query: '{query}' (top_k={k})")
        results = self.vector_store.similarity_search(query, k=k)
        return results
        
    def as_retriever(self, search_kwargs={"k": 4}):
        """
        Get standard LangChain retriever interface.
        """
        return self.vector_store.as_retriever(search_kwargs=search_kwargs)
