import unittest
from unittest.mock import MagicMock, patch
import os

# Ensure project root is in python path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.rag.document_loader import DocumentLoader

class TestPDFTableExtraction(unittest.TestCase):
    
    @patch('pdfplumber.open')
    def test_pdfplumber_table_extraction(self, mock_pdfplumber_open):
        # Setup mock page
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Đây là văn bản ngữ cảnh xung quanh bảng biểu."
        
        # Mock table data: list of lists representing rows/columns
        mock_page.extract_tables.return_value = [
            [
                ["Họ và tên", "Tuổi", "Vai trò"],
                ["Nguyễn Văn A", "30", "Kỹ sư AI"],
                ["Trần Thị B", "28", "Chuyên viên QA"]
            ]
        ]
        
        # Mock PDF object
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        
        # When pdfplumber.open is called as a context manager
        mock_pdfplumber_open.return_value.__enter__.return_value = mock_pdf
        
        # Execute loader
        # We pass a dummy path because the opening is mocked
        documents = DocumentLoader.load_document("dummy_path.pdf")
        
        # Asserts
        self.assertEqual(len(documents), 1)
        doc = documents[0]
        
        # The content should contain the text and the reconstructed GFM table
        self.assertIn("Đây là văn bản ngữ cảnh xung quanh bảng biểu.", doc.page_content)
        self.assertIn("### Bảng biểu trích xuất từ trang này:", doc.page_content)
        self.assertIn("| Họ và tên | Tuổi | Vai trò |", doc.page_content)
        self.assertIn("| --- | --- | --- |", doc.page_content)
        self.assertIn("| Nguyễn Văn A | 30 | Kỹ sư AI |", doc.page_content)
        self.assertIn("| Trần Thị B | 28 | Chuyên viên QA |", doc.page_content)
        
        # Metadata check
        self.assertEqual(doc.metadata["source"], "dummy_path.pdf")
        self.assertEqual(doc.metadata["page"], 1)
        
        print("\n[SUCCESS] Test passed successfully! pdfplumber successfully parsed and converted table to Markdown.\n")

if __name__ == '__main__':
    # Ensure there is a dummy file on disk because load_document checks os.path.exists
    with open("dummy_path.pdf", "w") as f:
        f.write("dummy content")
        
    try:
        unittest.main()
    finally:
        if os.path.exists("dummy_path.pdf"):
            os.remove("dummy_path.pdf")
