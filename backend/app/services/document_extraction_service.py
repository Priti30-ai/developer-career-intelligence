"""
document_extraction_service.py
------------------------------
Service for extracting raw text from uploaded resume documents (PDF, DOCX, TXT).

Architecture:
Uploaded Resume File -> DocumentExtractionService -> Plain Resume Text -> ResumeService
"""

import io
from pathlib import Path
from typing import Optional

import docx
import pymupdf


# Maximum file upload size: 5 MB
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024

# Allowed file extensions and MIME types
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}


class DocumentExtractionError(Exception):
    """Base exception for document extraction failures."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class UnsupportedFormatError(DocumentExtractionError):
    """Raised when an uploaded document is not a supported format."""

    def __init__(
        self,
        message: str = "Unsupported resume format. Please upload a PDF, DOCX, or TXT file.",
    ):
        super().__init__(message=message, status_code=400)


class EmptyFileError(DocumentExtractionError):
    """Raised when an uploaded document contains 0 bytes."""

    def __init__(
        self,
        message: str = "Uploaded file is empty. Please upload a valid resume document.",
    ):
        super().__init__(message=message, status_code=400)


class FileTooLargeError(DocumentExtractionError):
    """Raised when an uploaded document exceeds the maximum allowed size."""

    def __init__(
        self,
        message: str = "File size exceeds the 5 MB limit. Please upload a smaller resume document.",
    ):
        super().__init__(message=message, status_code=413)


class CorruptedDocumentError(DocumentExtractionError):
    """Raised when a document cannot be parsed due to corruption or malformed structure."""

    def __init__(self, message: str = "The document appears to be corrupted or invalid."):
        super().__init__(message=message, status_code=400)


class NoTextExtractedError(DocumentExtractionError):
    """Raised when a document is successfully opened but yields no extractable text."""

    def __init__(
        self,
        message: str = "Could not extract text from this document. Please upload a text-based resume.",
    ):
        super().__init__(message=message, status_code=400)


class DocumentExtractionService:
    """
    Deterministic extraction service supporting PDF, DOCX, and TXT files.
    """

    def validate_file_metadata(
        self,
        filename: Optional[str] = None,
        content_type: Optional[str] = None,
        file_size: Optional[int] = None,
    ) -> str:
        """
        Validates file extension, MIME type, and optional size before processing.
        Returns the normalized format type: 'pdf', 'docx', or 'txt'.
        """
        ext = ""
        if filename:
            ext = Path(filename).suffix.lower()

        normalized_mime = (content_type or "").split(";")[0].strip().lower()

        # Determine format based on extension first, then MIME type
        format_type = None
        if ext == ".pdf" or normalized_mime == "application/pdf":
            format_type = "pdf"
        elif (
            ext == ".docx"
            or normalized_mime
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            format_type = "docx"
        elif ext == ".txt" or normalized_mime == "text/plain":
            format_type = "txt"

        if not format_type:
            raise UnsupportedFormatError(
                "Unsupported resume format. Please upload a PDF, DOCX, or TXT file."
            )

        if file_size is not None:
            if file_size == 0:
                raise EmptyFileError("Uploaded file is empty. Please upload a valid resume document.")
            if file_size > MAX_FILE_SIZE_BYTES:
                raise FileTooLargeError(
                    "File size exceeds the 5 MB limit. Please upload a smaller resume document."
                )

        return format_type

    def extract_text(
        self,
        file_bytes: bytes,
        filename: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> str:
        """
        Extracts plain text content from raw bytes based on file format.

        Args:
            file_bytes: In-memory byte content of the uploaded document.
            filename: Original filename of the uploaded file.
            content_type: Reported HTTP Content-Type header.

        Returns:
            Extracted, stripped plain text string.
        """
        if not file_bytes or len(file_bytes) == 0:
            raise EmptyFileError("Uploaded file is empty. Please upload a valid resume document.")

        if len(file_bytes) > MAX_FILE_SIZE_BYTES:
            raise FileTooLargeError(
                "File size exceeds the 5 MB limit. Please upload a smaller resume document."
            )

        format_type = self.validate_file_metadata(
            filename=filename,
            content_type=content_type,
            file_size=len(file_bytes),
        )

        if format_type == "pdf":
            extracted = self._extract_from_pdf(file_bytes)
        elif format_type == "docx":
            extracted = self._extract_from_docx(file_bytes)
        elif format_type == "txt":
            extracted = self._extract_from_txt(file_bytes)
        else:
            raise UnsupportedFormatError(
                "Unsupported resume format. Please upload a PDF, DOCX, or TXT file."
            )

        trimmed = extracted.strip()
        if not trimmed:
            if format_type == "pdf":
                raise NoTextExtractedError(
                    "Could not extract text from this PDF. Please upload a text-based PDF or DOCX resume."
                )
            if format_type == "docx":
                raise NoTextExtractedError(
                    "Could not extract text from this DOCX document. The document appears to be empty."
                )
            raise NoTextExtractedError("The text file is empty or contains only whitespace.")

        return trimmed

    def _extract_from_pdf(self, file_bytes: bytes) -> str:
        """Extracts text across all pages using PyMuPDF."""
        try:
            doc = pymupdf.open(stream=file_bytes, filetype="pdf")
        except Exception as exc:
            raise CorruptedDocumentError(
                "Could not read PDF document. The file appears to be corrupted or invalid."
            ) from exc

        try:
            if doc.is_encrypted:
                try:
                    # Attempt authentication with empty password
                    doc.authenticate("")
                except Exception:
                    pass
                if doc.is_encrypted:
                    raise CorruptedDocumentError(
                        "The PDF document is password-protected and cannot be read."
                    )

            extracted_pages = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text("text")
                if page_text and page_text.strip():
                    extracted_pages.append(page_text.strip())

            if not extracted_pages:
                raise NoTextExtractedError(
                    "Could not extract text from this PDF. Please upload a text-based PDF or DOCX resume."
                )

            return "\n\n".join(extracted_pages)
        except DocumentExtractionError:
            raise
        except Exception as exc:
            raise CorruptedDocumentError(
                "Could not read PDF document. The file appears to be corrupted or invalid."
            ) from exc
        finally:
            doc.close()

    def _extract_from_docx(self, file_bytes: bytes) -> str:
        """Extracts text from paragraphs and tables using python-docx."""
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
        except Exception as exc:
            raise CorruptedDocumentError(
                "Could not read DOCX document. The file appears to be corrupted or invalid."
            ) from exc

        text_lines = []

        # 1. Paragraphs
        for para in doc.paragraphs:
            content = para.text.strip()
            if content:
                text_lines.append(content)

        # 2. Tables
        for table in doc.tables:
            for row in table.rows:
                row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                # Deduplicate merged cells that repeat identical text in consecutive cells
                unique_cells = []
                for cell_val in row_cells:
                    if not unique_cells or cell_val != unique_cells[-1]:
                        unique_cells.append(cell_val)
                if unique_cells:
                    text_lines.append(" | ".join(unique_cells))

        return "\n".join(text_lines)

    def _extract_from_txt(self, file_bytes: bytes) -> str:
        """Extracts text by decoding as UTF-8 (with fallbacks)."""
        # Try UTF-8 with BOM first, then standard UTF-8
        for encoding in ("utf-8-sig", "utf-8"):
            try:
                return file_bytes.decode(encoding)
            except UnicodeDecodeError:
                continue

        # If strict UTF-8 fails, reject with clear decoding error
        raise CorruptedDocumentError(
            "Failed to decode text file. Please ensure the file is valid UTF-8 encoded text."
        )


document_extraction_service = DocumentExtractionService()
