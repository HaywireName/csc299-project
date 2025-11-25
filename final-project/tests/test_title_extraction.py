"""
Tests for title extraction feature in docs_module.
"""
import pytest
import os
from pathlib import Path


class TestTitleExtraction:
    """Test title extraction from document content."""
    
    def test_extract_title_from_text_basic(self, document_manager):
        """Test extracting title from simple text."""
        text = "This is the Title\n\nThis is some content."
        
        title = document_manager._extract_title_from_text(text)
        
        assert title == "This is the Title"
    
    def test_extract_title_from_text_with_empty_lines(self, document_manager):
        """Test extracting title when there are empty lines at start."""
        text = "\n\n\nActual Title Here\n\nContent follows."
        
        title = document_manager._extract_title_from_text(text)
        
        assert title == "Actual Title Here"
    
    def test_extract_title_from_text_skips_page_numbers(self, document_manager):
        """Test that page numbers are skipped."""
        text = "1\n2\nReal Title\nContent here."
        
        title = document_manager._extract_title_from_text(text)
        
        assert title == "Real Title"
    
    def test_extract_title_from_text_skips_page_markers(self, document_manager):
        """Test that page markers are skipped."""
        text = "--- Page 1 ---\nDocument Title\nContent."
        
        title = document_manager._extract_title_from_text(text)
        
        assert title == "Document Title"
    
    def test_extract_title_from_text_truncates_long_titles(self, document_manager):
        """Test that very long titles are truncated."""
        long_title = "A" * 150
        text = f"{long_title}\nContent here."
        
        title = document_manager._extract_title_from_text(text, max_length=100)
        
        assert len(title) <= 103  # 100 + "..."
        assert title.endswith("...")
    
    def test_extract_title_from_text_no_suitable_title(self, document_manager):
        """Test when no suitable title can be found."""
        text = "1\n2\n3\n\n\n"
        
        title = document_manager._extract_title_from_text(text)
        
        assert title is None
    
    def test_extract_title_from_text_empty_input(self, document_manager):
        """Test with empty text."""
        title = document_manager._extract_title_from_text("")
        
        assert title is None
    
    def test_txt_document_title_from_content(self, document_manager, temp_data_dir):
        """Test that TXT document extracts title from content."""
        # Create a TXT file
        txt_file = temp_data_dir / "test_doc.txt"
        txt_file.write_text("Document Title Goes Here\n\nThis is the content of the document.")
        
        doc = document_manager.add_doc(str(txt_file))
        
        assert doc['title'] == "Document Title Goes Here"
    
    def test_txt_document_title_with_empty_lines(self, document_manager, temp_data_dir):
        """Test TXT document title extraction with leading empty lines."""
        txt_file = temp_data_dir / "test_doc2.txt"
        txt_file.write_text("\n\n\nMy Important Document\n\nContent starts here.")
        
        doc = document_manager.add_doc(str(txt_file))
        
        assert doc['title'] == "My Important Document"
    
    def test_fallback_to_filename_when_no_title(self, document_manager, temp_data_dir):
        """Test that filename is used when no title can be extracted."""
        # Create a file with only numbers
        txt_file = temp_data_dir / "my_document.txt"
        txt_file.write_text("1\n2\n3\n")
        
        doc = document_manager.add_doc(str(txt_file))
        
        # Should fall back to filename without extension
        assert doc['title'] == "my_document"


class TestPDFTitleExtraction:
    """Test PDF-specific title extraction."""
    
    def test_pdf_title_prefers_metadata_when_good(self, document_manager, mocker):
        """Test that good metadata title is preferred over content extraction."""
        # Create a mock PDF with good metadata
        mock_reader = mocker.MagicMock()
        mock_reader.pages = [mocker.MagicMock()]
        mock_reader.pages[0].extract_text.return_value = "Some Content\nIn the PDF"
        
        # Mock metadata with a good title
        mock_metadata = mocker.MagicMock()
        mock_metadata.title = "Proper Document Title"
        mock_reader.metadata = mock_metadata
        
        mocker.patch('modules.docs_module.PdfReader', return_value=mock_reader)
        
        # Create a temporary PDF file (just for path validation)
        from pathlib import Path
        temp_pdf = Path("/tmp/test.pdf")
        temp_pdf.touch()
        
        try:
            metadata = document_manager._extract_pdf_metadata(str(temp_pdf))
            
            assert metadata['title'] == "Proper Document Title"
        finally:
            temp_pdf.unlink()
    
    def test_pdf_title_extracts_from_content_when_metadata_generic(self, document_manager, mocker):
        """Test that content extraction is used when metadata is generic."""
        mock_reader = mocker.MagicMock()
        mock_reader.pages = [mocker.MagicMock()]
        mock_reader.pages[0].extract_text.return_value = "Artificial Intelligence Fundamentals\nThis is a paper about AI."
        
        # Mock metadata with generic title
        mock_metadata = mocker.MagicMock()
        mock_metadata.title = "(anonymous)"
        mock_reader.metadata = mock_metadata
        
        mocker.patch('modules.docs_module.PdfReader', return_value=mock_reader)
        
        from pathlib import Path
        temp_pdf = Path("/tmp/test.pdf")
        temp_pdf.touch()
        
        try:
            metadata = document_manager._extract_pdf_metadata(str(temp_pdf))
            
            assert metadata['title'] == "Artificial Intelligence Fundamentals"
        finally:
            temp_pdf.unlink()
    
    def test_pdf_title_extracts_from_content_when_no_metadata(self, document_manager, mocker):
        """Test that content extraction is used when no metadata."""
        mock_reader = mocker.MagicMock()
        mock_reader.pages = [mocker.MagicMock()]
        mock_reader.pages[0].extract_text.return_value = "Research Paper Title\nAuthors: John Doe\nAbstract follows..."
        
        # No metadata
        mock_reader.metadata = None
        
        mocker.patch('modules.docs_module.PdfReader', return_value=mock_reader)
        
        from pathlib import Path
        temp_pdf = Path("/tmp/test.pdf")
        temp_pdf.touch()
        
        try:
            metadata = document_manager._extract_pdf_metadata(str(temp_pdf))
            
            assert metadata['title'] == "Research Paper Title"
        finally:
            temp_pdf.unlink()


class TestDOCXTitleExtraction:
    """Test DOCX-specific title extraction."""
    
    def test_docx_title_prefers_properties_when_good(self, document_manager, mocker):
        """Test that good properties title is preferred."""
        mock_doc = mocker.MagicMock()
        mock_doc.paragraphs = [mocker.MagicMock()]
        mock_doc.paragraphs[0].text = "Content in document"
        
        # Mock core properties with good title
        mock_properties = mocker.MagicMock()
        mock_properties.title = "Business Report 2025"
        mock_doc.core_properties = mock_properties
        
        mocker.patch('modules.docs_module.Document', return_value=mock_doc)
        
        from pathlib import Path
        temp_docx = Path("/tmp/test.docx")
        temp_docx.touch()
        
        try:
            metadata = document_manager._extract_docx_metadata(str(temp_docx))
            
            assert metadata['title'] == "Business Report 2025"
        finally:
            temp_docx.unlink()
    
    def test_docx_title_extracts_from_content_when_properties_generic(self, document_manager, mocker):
        """Test that content extraction is used when properties are generic."""
        mock_doc = mocker.MagicMock()
        
        # Create mock paragraphs
        para1 = mocker.MagicMock()
        para1.text = "Annual Financial Report"
        para2 = mocker.MagicMock()
        para2.text = ""
        para3 = mocker.MagicMock()
        para3.text = "Summary of Q4 results..."
        
        mock_doc.paragraphs = [para1, para2, para3]
        
        # Mock core properties with generic title
        mock_properties = mocker.MagicMock()
        mock_properties.title = "Word Document"
        mock_doc.core_properties = mock_properties
        
        mocker.patch('modules.docs_module.Document', return_value=mock_doc)
        
        from pathlib import Path
        temp_docx = Path("/tmp/test.docx")
        temp_docx.touch()
        
        try:
            metadata = document_manager._extract_docx_metadata(str(temp_docx))
            
            assert metadata['title'] == "Annual Financial Report"
        finally:
            temp_docx.unlink()
    
    def test_docx_title_skips_empty_paragraphs(self, document_manager, mocker):
        """Test that empty paragraphs are skipped when extracting title."""
        mock_doc = mocker.MagicMock()
        
        # Create mock paragraphs with empty ones first
        para1 = mocker.MagicMock()
        para1.text = ""
        para2 = mocker.MagicMock()
        para2.text = "   "
        para3 = mocker.MagicMock()
        para3.text = "Actual Document Title"
        
        mock_doc.paragraphs = [para1, para2, para3]
        
        # No properties title
        mock_properties = mocker.MagicMock()
        mock_properties.title = None
        mock_doc.core_properties = mock_properties
        
        mocker.patch('modules.docs_module.Document', return_value=mock_doc)
        
        from pathlib import Path
        temp_docx = Path("/tmp/test.docx")
        temp_docx.touch()
        
        try:
            metadata = document_manager._extract_docx_metadata(str(temp_docx))
            
            assert metadata['title'] == "Actual Document Title"
        finally:
            temp_docx.unlink()
