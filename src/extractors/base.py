# src/extractors/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

@dataclass
class ExtractionResult:
    """Canonical extraction outcome passed to Team A's normalizer (FR-E7)."""
    text: str = ""
    native_metadata_raw: Dict[str, Any] = field(default_factory=dict)
    extraction_method: str = "parser"
    page_count: Optional[int] = None
    errors: List[str] = field(default_factory=list)

class Extractor(ABC):
    """Abstract base class for all file parsers and OCR modules."""
    
    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """List of lowercase file extensions supported (e.g. ['pdf'])."""
        pass

    @abstractmethod
    def extract(self, file_bytes: bytes, filename: str) -> ExtractionResult:
        """Extract native properties and readable body text."""
        pass