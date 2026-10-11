# src/extractors/ocr.py
import io
import fitz
import numpy as np
from PIL import Image
import easyocr
from src.extractors.base import Extractor, ExtractionResult

class ImageOcrExtractor(Extractor):
    """Optical Character Recognition for image files and scanned text-free PDFs (FR-E6)."""
    
    def __init__(self, languages: list = None):
        self.languages = languages or ["en"]
        # Initalizes model on CPU by default
        self._reader = None

    @property
    def reader(self):
        if self._reader is None:
            self._reader = easyocr.Reader(self.languages, gpu=False)
        return self._reader

    @property
    def supported_extensions(self):
        return ["png", "jpg", "jpeg", "tiff"]

    def extract(self, file_bytes: bytes, filename: str) -> ExtractionResult:
        res = ExtractionResult(extraction_method="EasyOCR")
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        
        try:
            if ext in self.supported_extensions:
                img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
                img_np = np.array(img)
                lines = self.reader.readtext(img_np, detail=0)
                res.text = "\n".join(lines).strip()
                res.page_count = 1
                res.native_metadata_raw = {"format": img.format, "size": img.size}
            elif ext == "pdf":
                # Fallback path for PDFs with no digital text layer
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                res.page_count = len(doc)
                extracted_pages = []
                for page in doc:
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    lines = self.reader.readtext(np.array(img), detail=0)
                    extracted_pages.append("\n".join(lines))
                res.text = "\n\n".join(extracted_pages).strip()
                res.native_metadata_raw = dict(doc.metadata) if doc.metadata else {}
                doc.close()
        except Exception as e:
            res.errors.append(f"ImageOcrExtractor failed: {str(e)}")
            
        return res