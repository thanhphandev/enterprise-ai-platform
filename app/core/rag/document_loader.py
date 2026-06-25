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
    def _load_pdf_with_pdfplumber(file_path: str) -> List[Document]:
        """
        Extract text and reconstruct tables in Markdown format from a PDF using pdfplumber.
        """
        import pdfplumber
        documents = []
        
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                # Extract text
                text = page.extract_text() or ""
                
                # Extract tables
                tables = page.extract_tables()
                markdown_tables = []
                
                for table in tables:
                    if not table or all(all(cell is None or cell == "" for cell in row) for row in table):
                        continue
                    
                    # Convert to Markdown GFM format
                    markdown_lines = []
                    for row_idx, row in enumerate(table):
                        cleaned_row = [
                            str(cell).replace('\n', ' ').strip() if cell is not None else ""
                            for cell in row
                        ]
                        markdown_lines.append("| " + " | ".join(cleaned_row) + " |")
                        
                        # Add header separator
                        if row_idx == 0:
                            separator = "| " + " | ".join(["---"] * len(row)) + " |"
                            markdown_lines.append(separator)
                    
                    if markdown_lines:
                        markdown_tables.append("\n".join(markdown_lines))
                
                # Construct page content
                page_content = text
                if markdown_tables:
                    page_content += "\n\n### Bảng biểu trích xuất từ trang này:\n\n" + "\n\n".join(markdown_tables)
                
                metadata = {
                    "source": file_path,
                    "page": i + 1
                }
                documents.append(Document(page_content=page_content, metadata=metadata))
                
        return documents

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
                try:
                    logger.info(f"Loading PDF with table extraction (via pdfplumber): {file_path}")
                    return DocumentLoader._load_pdf_with_pdfplumber(file_path)
                except Exception as ex:
                    logger.warning(f"pdfplumber failed: {str(ex)}. Falling back to PyMuPDFLoader.")
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

