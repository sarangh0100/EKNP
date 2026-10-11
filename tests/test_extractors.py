# tests/test_extractors.py
import pytest
from src.extractors.parsers import TxtExtractor, PdfExtractor, DocxExtractor

def test_txt_extractor():
    extractor = TxtExtractor()
    content = b"Enterprise Knowledge Normalization Platform"
    result = extractor.extract(content, "sample.txt")
    
    assert result.text == "Enterprise Knowledge Normalization Platform"
    assert result.extraction_method == "builtin_txt"
    assert len(result.errors) == 0

def test_corrupt_file_handling():
    """FR-E8 / NFR-5: Corrupted files must not throw unhandled exceptions."""
    extractor = PdfExtractor()
    corrupt_bytes = b"NOT_A_VALID_PDF_STREAM"
    result = extractor.extract(corrupt_bytes, "broken.pdf")
    
    assert len(result.errors) > 0
    assert result.text == ""

def test_unsupported_or_empty_docx():
    """FR-E8: Verify docx parser error handling on malformed input."""
    extractor = DocxExtractor()
    result = extractor.extract(b"", "empty.docx")
    
    assert len(result.errors) > 0