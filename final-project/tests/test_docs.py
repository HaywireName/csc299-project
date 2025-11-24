"""
Tests for modules.docs_module (DocumentManager).
"""
import pytest
import os
from core.errors import PDFNotFoundError, InvalidInputError, StorageError


class TestDocumentManagerBasics:
    """Test basic DocumentManager functionality."""
    
    def test_add_txt_document(self, document_manager, sample_txt_file):
        """Test adding a TXT document."""
        doc = document_manager.add_doc(sample_txt_file)
        
        assert doc['id'] is not None
        assert doc['extension'] == '.txt'
        assert 'Sample Text Document' in doc['title']
        assert doc['page_count'] > 0  # Line count
    
    def test_add_document_invalid_path(self, document_manager):
        """Test that adding non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            document_manager.add_doc("/path/to/nonexistent/file.pdf")
    
    def test_add_document_invalid_extension(self, document_manager, temp_data_dir):
        """Test that invalid file type raises error."""
        # Create a file with invalid extension
        invalid_file = temp_data_dir / "test.invalid"
        invalid_file.write_text("test content")
        
        with pytest.raises(ValueError):
            document_manager.add_doc(str(invalid_file))
    
    def test_list_docs_empty(self, document_manager):
        """Test listing documents when none exist."""
        docs = document_manager.list_docs()
        
        assert docs == []
    
    def test_list_docs_multiple(self, document_manager, sample_txt_file, temp_data_dir):
        """Test listing multiple documents."""
        # Add first document
        document_manager.add_doc(sample_txt_file)
        
        # Create and add second document
        txt2 = temp_data_dir / "sample2.txt"
        txt2.write_text("Second document")
        document_manager.add_doc(str(txt2))
        
        docs = document_manager.list_docs()
        
        assert len(docs) == 2
    
    def test_list_docs_sorted_by_last_accessed(self, document_manager, sample_txt_file, temp_data_dir):
        """Test that documents are sorted by last accessed."""
        doc1 = document_manager.add_doc(sample_txt_file)
        
        txt2 = temp_data_dir / "sample2.txt"
        txt2.write_text("Second document")
        doc2 = document_manager.add_doc(str(txt2))
        
        # Access first document
        document_manager.update_last_accessed(doc1['id'])
        
        docs = document_manager.list_docs()
        
        # Most recently accessed should be first
        assert docs[0]['id'] == doc1['id']


class TestDocumentOperations:
    """Test document operations."""
    
    def test_get_doc_by_id(self, document_manager, sample_txt_file):
        """Test getting document by ID."""
        doc = document_manager.add_doc(sample_txt_file)
        
        retrieved = document_manager.get_doc(doc['id'])
        
        assert retrieved['id'] == doc['id']
    
    def test_get_doc_by_partial_id(self, document_manager, sample_txt_file):
        """Test getting document by partial ID."""
        doc = document_manager.add_doc(sample_txt_file)
        
        partial_id = doc['id'][:2]
        retrieved = document_manager.get_doc(partial_id)
        
        assert retrieved['id'] == doc['id']
    
    def test_get_doc_invalid_id(self, document_manager):
        """Test that invalid ID raises PDFNotFoundError."""
        with pytest.raises(PDFNotFoundError):
            document_manager.get_doc("invalid_id")
    
    def test_remove_doc(self, document_manager, sample_txt_file, monkeypatch):
        """Test removing a document."""
        doc = document_manager.add_doc(sample_txt_file)
        
        # Mock user confirmation
        monkeypatch.setattr('builtins.input', lambda _: "yes")
        
        document_manager.remove_doc(doc['id'])
        
        with pytest.raises(PDFNotFoundError):
            document_manager.get_doc(doc['id'])
    
    def test_remove_doc_deletes_file(self, document_manager, sample_txt_file, monkeypatch):
        """Test that removing document deletes the file."""
        doc = document_manager.add_doc(sample_txt_file)
        filepath = doc['filepath']
        
        # Verify file exists
        assert os.path.exists(filepath)
        
        # Mock user confirmation
        monkeypatch.setattr('builtins.input', lambda _: "yes")
        
        document_manager.remove_doc(doc['id'])
        
        # Verify file is deleted
        assert not os.path.exists(filepath)
    
    def test_update_last_accessed(self, document_manager, sample_txt_file):
        """Test updating last accessed timestamp."""
        doc = document_manager.add_doc(sample_txt_file)
        original_timestamp = doc['last_accessed']
        
        import time
        time.sleep(0.1)  # Small delay to ensure different timestamp
        
        document_manager.update_last_accessed(doc['id'])
        
        updated_doc = document_manager.get_doc(doc['id'])
        assert updated_doc['last_accessed'] != original_timestamp


class TestTextExtraction:
    """Test text extraction functionality."""
    
    def test_extract_text_from_txt(self, document_manager, sample_txt_file):
        """Test extracting text from TXT file."""
        doc = document_manager.add_doc(sample_txt_file)
        
        text, word_count = document_manager.extract_text(doc['id'])
        
        assert "Sample Text Document" in text
        assert word_count > 0
    
    def test_extract_text_caching(self, document_manager, sample_txt_file):
        """Test that extracted text is cached."""
        doc = document_manager.add_doc(sample_txt_file)
        
        # Extract first time
        text1, _ = document_manager.extract_text(doc['id'])
        
        # Extract second time (should use cache)
        text2, _ = document_manager.extract_text(doc['id'])
        
        assert text1 == text2
        
        # Verify cache file exists
        cache_path = document_manager._get_cache_path(doc['id'], None)
        assert os.path.exists(cache_path)
    
    def test_extract_text_updates_last_accessed(self, document_manager, sample_txt_file):
        """Test that extraction updates last accessed."""
        doc = document_manager.add_doc(sample_txt_file)
        original_timestamp = doc['last_accessed']
        
        import time
        time.sleep(0.1)
        
        document_manager.extract_text(doc['id'])
        
        updated_doc = document_manager.get_doc(doc['id'])
        assert updated_doc['last_accessed'] != original_timestamp


class TestDocumentSearch:
    """Test document search functionality."""
    
    def test_search_docs_by_content(self, document_manager, sample_txt_file):
        """Test searching documents by content."""
        document_manager.add_doc(sample_txt_file)
        
        results = document_manager.search_docs("Sample")
        
        assert len(results) > 0
        assert any("Sample" in r[2] for r in results)  # Check context
    
    def test_search_docs_case_insensitive(self, document_manager, sample_txt_file):
        """Test that search is case-insensitive."""
        document_manager.add_doc(sample_txt_file)
        
        results_lower = document_manager.search_docs("sample")
        results_upper = document_manager.search_docs("SAMPLE")
        
        assert len(results_lower) == len(results_upper)
    
    def test_search_docs_no_results(self, document_manager, sample_txt_file):
        """Test searching with no matches."""
        document_manager.add_doc(sample_txt_file)
        
        results = document_manager.search_docs("nonexistent_term")
        
        assert len(results) == 0
    
    def test_search_docs_empty_query(self, document_manager, sample_txt_file):
        """Test searching with empty query."""
        document_manager.add_doc(sample_txt_file)
        
        results = document_manager.search_docs("")
        
        assert len(results) == 0


class TestDocumentSummarization:
    """Test document summarization with AI."""
    
    def test_summarize_doc(self, document_manager, sample_txt_file):
        """Test summarizing a document."""
        doc = document_manager.add_doc(sample_txt_file)
        
        summary, cost = document_manager.summarize_doc(doc['id'])
        
        assert summary is not None
        assert len(summary) > 0
        assert cost > 0
        
        # Verify summary is saved
        updated_doc = document_manager.get_doc(doc['id'])
        assert updated_doc['summary'] == summary
    
    def test_summarize_doc_invalid_id(self, document_manager):
        """Test that invalid ID raises error."""
        from core.errors import PDFNotFoundError
        with pytest.raises(PDFNotFoundError):
            document_manager.summarize_doc("invalid_id")
    
    def test_summarize_doc_tracks_cost(self, document_manager, sample_txt_file):
        """Test that summarization tracks cost."""
        doc = document_manager.add_doc(sample_txt_file)
        
        initial_cost = document_manager.session_cost
        document_manager.summarize_doc(doc['id'])
        
        assert document_manager.session_cost > initial_cost
    
    def test_summarize_doc_with_max_words(self, document_manager, sample_txt_file):
        """Test summarizing with custom max words."""
        doc = document_manager.add_doc(sample_txt_file)
        
        summary, _ = document_manager.summarize_doc(doc['id'], max_words=100)
        
        # Summary should respect word limit (roughly)
        word_count = len(summary.split())
        assert word_count <= 150  # Allow some buffer


class TestDocumentMetadata:
    """Test document metadata extraction."""
    
    def test_txt_metadata_extraction(self, document_manager, sample_txt_file):
        """Test extracting metadata from TXT file."""
        metadata = document_manager._extract_txt_metadata(sample_txt_file)
        
        assert 'page_count' in metadata  # Line count
        assert 'title' in metadata
        assert 'preview' in metadata
        assert metadata['page_count'] > 0
    
    def test_generate_unique_filename(self, document_manager):
        """Test generating unique filenames."""
        filename1 = document_manager._generate_unique_filename("test.pdf")
        filename2 = document_manager._generate_unique_filename("test.pdf")
        
        # Should be different
        assert filename1 != filename2
        # Should contain original name
        assert "test.pdf" in filename1
    
    def test_generate_doc_id(self, document_manager, sample_txt_file):
        """Test generating document IDs."""
        doc1 = document_manager.add_doc(sample_txt_file)
        
        # Create second document
        txt2_path = os.path.join(os.path.dirname(sample_txt_file), "sample2.txt")
        with open(txt2_path, 'w') as f:
            f.write("Second document")
        doc2 = document_manager.add_doc(txt2_path)
        
        # IDs should be sequential
        assert int(doc2['id']) == int(doc1['id']) + 1


class TestDocumentCache:
    """Test document caching functionality."""
    
    def test_cache_path_full_document(self, document_manager):
        """Test getting cache path for full document."""
        cache_path = document_manager._get_cache_path("1", None)
        
        assert "1_full.txt" in cache_path
    
    def test_cache_path_specific_page(self, document_manager):
        """Test getting cache path for specific page."""
        cache_path = document_manager._get_cache_path("1", 5)
        
        assert "1_page5.txt" in cache_path
    
    def test_text_extraction_creates_cache(self, document_manager, sample_txt_file):
        """Test that text extraction creates cache file."""
        doc = document_manager.add_doc(sample_txt_file)
        cache_path = document_manager._get_cache_path(doc['id'], None)
        
        # Cache shouldn't exist yet
        assert not os.path.exists(cache_path)
        
        # Extract text
        document_manager.extract_text(doc['id'])
        
        # Cache should now exist
        assert os.path.exists(cache_path)


class TestDocumentChunking:
    """Test text chunking for large documents."""
    
    def test_chunk_text(self, document_manager):
        """Test chunking text into smaller pieces."""
        # Create a long text
        long_text = " ".join(["word"] * 5000)
        
        chunks = document_manager._chunk_text(long_text, chunk_size=1000)
        
        assert len(chunks) > 1
        assert len(chunks) == 5  # 5000 words / 1000 per chunk
    
    def test_chunk_text_small_text(self, document_manager):
        """Test chunking small text returns single chunk."""
        small_text = "This is a small text"
        
        chunks = document_manager._chunk_text(small_text, chunk_size=1000)
        
        assert len(chunks) == 1
        assert chunks[0] == small_text
