# src/connectors/local.py
import os
import hashlib
from typing import List, Dict, Any
from src.connectors.base import Connector

class LocalFolderConnector(Connector):
    """Local file-system directory connector (FR-C1, FR-C2, FR-C3, FR-C4)."""
    
    def __init__(self, silo_id: str, root_path: str):
        super().__init__(silo_id)
        self.root_path = os.path.abspath(root_path)
        if not os.path.isdir(self.root_path):
            raise ValueError(f"Silo path does not exist: {self.root_path}")

    def list_files(self) -> List[str]:
        """Recursively scans the local silo folder."""
        file_list = []
        for root, _, files in os.walk(self.root_path):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, self.root_path)
                file_list.append(rel_path.replace("\\", "/"))
        return sorted(file_list)

    def read_bytes(self, relative_path: str) -> bytes:
        """Reads file bytes with strict read-only access (FR-C3)."""
        abs_path = os.path.join(self.root_path, relative_path)
        with open(abs_path, "rb") as f:
            return f.read()

    def native_stat(self, relative_path: str) -> Dict[str, Any]:
        """Fetches filesystem stats without modifying files."""
        abs_path = os.path.join(self.root_path, relative_path)
        stat = os.stat(abs_path)
        return {
            "size_bytes": stat.st_size,
            "created_timestamp": stat.st_ctime,
            "modified_timestamp": stat.st_mtime,
        }

    @staticmethod
    def compute_sha256(content: bytes) -> str:
        """Deterministic SHA-256 byte digest for change tracking (FR-C4)."""
        return hashlib.sha256(content).hexdigest()