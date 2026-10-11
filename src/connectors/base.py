# src/connectors/base.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any

class Connector(ABC):
    """Abstract interface for all silo connectors (FR-C1 to FR-C5)."""
    
    def __init__(self, silo_id: str):
        self.silo_id = silo_id

    @abstractmethod
    def list_files(self) -> List[str]:
        """Recursively list all relative file paths within the silo."""
        pass

    @abstractmethod
    def read_bytes(self, relative_path: str) -> bytes:
        """Read and return byte content of a given file in read-only mode."""
        pass

    @abstractmethod
    def native_stat(self, relative_path: str) -> Dict[str, Any]:
        """Return filesystem metadata (size, timestamps)."""
        pass