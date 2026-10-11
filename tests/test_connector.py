# tests/test_connector.py
import pytest
import os
import hashlib
from src.connectors.local import LocalFolderConnector

@pytest.fixture
def mock_silo(tmp_path):
    """
    Creates a simulated directory structure mimicking a department silo (FR-C1).
    Structure:
      silo_root/
      ├── hr_policy.txt
      ├── employee_handbook.pdf
      └── nested/
          └── subfolder_doc.txt
    """
    silo_dir = tmp_path / "hr_test_silo"
    silo_dir.mkdir()

    # Create root level files
    file1 = silo_dir / "hr_policy.txt"
    file1.write_text("Standard corporate HR policy content.", encoding="utf-8")

    file2 = silo_dir / "employee_handbook.pdf"
    file2.write_bytes(b"%PDF-1.4 dummy binary content")

    # Create nested subfolder and file
    nested_dir = silo_dir / "nested"
    nested_dir.mkdir()
    file3 = nested_dir / "subfolder_doc.txt"
    file3.write_text("Nested document inside sub-directory.", encoding="utf-8")

    return silo_dir


def test_invalid_silo_path_raises_error():
    """FR-C1: Connector must validate directory existence."""
    with pytest.raises(ValueError, match="Silo path does not exist"):
        LocalFolderConnector(silo_id="hr", root_path="invalid/non_existent/path")


def test_recursive_file_discovery(mock_silo):
    """
    FR-C2: The system shall scan registered silos recursively 
    to discover all contained documents.
    """
    connector = LocalFolderConnector(silo_id="hr", root_path=str(mock_silo))
    discovered = connector.list_files()

    expected_files = [
        "employee_handbook.pdf",
        "hr_policy.txt",
        "nested/subfolder_doc.txt"
    ]
    assert discovered == expected_files


def test_read_bytes_content_integrity(mock_silo):
    """Verifies read_bytes correctly accesses file contents."""
    connector = LocalFolderConnector(silo_id="hr", root_path=str(mock_silo))
    content = connector.read_bytes("hr_policy.txt")
    
    assert content == b"Standard corporate HR policy content."


def test_non_destructive_read_only_guarantee(mock_silo):
    """
    FR-C3 & NFR-2: Read-only guarantee.
    Connector operations must never alter files, modify hashes, 
    or write sidecars to the silo folder.
    """
    connector = LocalFolderConnector(silo_id="hr", root_path=str(mock_silo))
    
    # Hash check before
    target_rel = "hr_policy.txt"
    target_abs = mock_silo / target_rel
    hash_before = hashlib.sha256(target_abs.read_bytes()).hexdigest()

    # Execute read operations
    _ = connector.list_files()
    _ = connector.read_bytes(target_rel)
    _ = connector.native_stat(target_rel)

    # Hash check after
    hash_after = hashlib.sha256(target_abs.read_bytes()).hexdigest()
    assert hash_before == hash_after, "Source file was altered during connector access!"


def test_compute_sha256_hash_detection():
    """
    FR-C4: Calculate deterministic SHA-256 cryptographic hashes 
    to track changes across runs.
    """
    payload_a = b"Original draft version 1"
    payload_b = b"Modified draft version 2"

    hash_a1 = LocalFolderConnector.compute_sha256(payload_a)
    hash_a2 = LocalFolderConnector.compute_sha256(payload_a)
    hash_b = LocalFolderConnector.compute_sha256(payload_b)

    # Determinism
    assert hash_a1 == hash_a2
    # Change differentiation
    assert hash_a1 != hash_b
    assert len(hash_a1) == 64


def test_native_stat_metadata(mock_silo):
    """Verifies retrieval of file system stats (size, timestamps)."""
    connector = LocalFolderConnector(silo_id="hr", root_path=str(mock_silo))
    stats = connector.native_stat("hr_policy.txt")

    assert "size_bytes" in stats
    assert "created_timestamp" in stats
    assert "modified_timestamp" in stats
    assert stats["size_bytes"] == len(b"Standard corporate HR policy content.")