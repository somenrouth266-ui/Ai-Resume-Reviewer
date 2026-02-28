"""
parser.py — Resume File Parsing Module
=======================================
Provides functions to extract plain text from PDF and DOCX resume files.
Keeps I/O concerns completely separate from the LLM and UI layers.
"""

import io
import pdfplumber
from docx import Document


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract all text from a PDF file provided as raw bytes.

    Uses pdfplumber which handles most modern, text-based PDFs reliably.
    Scanned / image-only PDFs will return an empty string.

    Args:
        file_bytes: Raw bytes of the uploaded PDF file.

    Returns:
        A single string containing all extracted text, pages joined by newlines.

    Raises:
        ValueError: If the bytes cannot be parsed as a valid PDF.
    """
    try:
        text_parts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                # extract_text() returns None for image-only pages
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text_parts.append(page_text.strip())
        return "\n\n".join(text_parts)
    except Exception as exc:
        raise ValueError(f"Failed to parse PDF: {exc}") from exc


def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Extract all text from a DOCX file provided as raw bytes.

    Iterates over every paragraph in the document body, preserving natural
    line breaks. Also extracts text from tables if present.

    Args:
        file_bytes: Raw bytes of the uploaded DOCX file.

    Returns:
        A single string containing all extracted text joined by newlines.

    Raises:
        ValueError: If the bytes cannot be parsed as a valid DOCX document.
    """
    try:
        doc = Document(io.BytesIO(file_bytes))
        parts = []

        # Extract paragraph text
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                parts.append(text)

        # Extract text from tables (some resumes use table layouts)
        for table in doc.tables:
            for row in table.rows:
                row_texts = []
                for cell in row.cells:
                    cell_text = cell.text.strip()
                    if cell_text:
                        row_texts.append(cell_text)
                if row_texts:
                    parts.append("  |  ".join(row_texts))

        return "\n".join(parts)
    except Exception as exc:
        raise ValueError(f"Failed to parse DOCX: {exc}") from exc
