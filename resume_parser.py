"""
resume_parser.py — Resume File Parsing Module
===============================================
Extracts plain text from PDF and DOCX resume files.
Images, graphics, and non-text elements are silently ignored.
"""

import io
import pdfplumber
from docx import Document
from docx.oxml.ns import qn


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract all text from a PDF file provided as raw bytes.
    Images and graphics are automatically skipped by pdfplumber.
    Only text characters are extracted — photos have no effect.

    Args:
        file_bytes: Raw bytes of the uploaded PDF file.

    Returns:
        A single string containing all extracted text.

    Raises:
        ValueError: If the bytes cannot be parsed as a valid PDF.
    """
    try:
        text_parts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                try:
                    # crop() with a bounding box covering the full page
                    # helps isolate text even in complex multi-column layouts
                    page_text = page.extract_text(
                        x_tolerance=3,
                        y_tolerance=3,
                    )
                    if page_text and page_text.strip():
                        text_parts.append(page_text.strip())
                except Exception:
                    # If a single page fails (e.g. image-only page), skip it
                    continue

        full_text = "\n\n".join(text_parts)

        # If nothing was extracted at all, try a fallback with looser settings
        if not full_text.strip():
            text_parts = []
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    try:
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            text_parts.append(page_text.strip())
                    except Exception:
                        continue
            full_text = "\n\n".join(text_parts)

        return full_text

    except Exception as exc:
        raise ValueError(f"Failed to parse PDF: {exc}") from exc


def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Extract all text from a DOCX file provided as raw bytes.
    Images, embedded objects, and drawing elements are silently skipped.
    Text from paragraphs, tables, text boxes, and headers is included.

    Args:
        file_bytes: Raw bytes of the uploaded DOCX file.

    Returns:
        A single string containing all extracted text.

    Raises:
        ValueError: If the bytes cannot be parsed as a valid DOCX document.
    """
    try:
        doc = Document(io.BytesIO(file_bytes))
        parts = []

        # ── Main body paragraphs ──────────────────────────────────────────────
        for para in doc.paragraphs:
            try:
                # Skip paragraph if it only contains an image (drawing element)
                # by checking if it has any actual text runs
                text = para.text.strip()
                if text:
                    parts.append(text)
            except Exception:
                continue

        # ── Tables (many resume templates use table-based layouts) ────────────
        for table in doc.tables:
            for row in table.rows:
                row_texts = []
                for cell in row.cells:
                    try:
                        cell_text = cell.text.strip()
                        if cell_text:
                            row_texts.append(cell_text)
                    except Exception:
                        continue
                if row_texts:
                    parts.append("  ".join(row_texts))

        # ── Headers and footers ───────────────────────────────────────────────
        for section in doc.sections:
            try:
                for para in section.header.paragraphs:
                    text = para.text.strip()
                    if text:
                        parts.append(text)
            except Exception:
                pass
            try:
                for para in section.footer.paragraphs:
                    text = para.text.strip()
                    if text:
                        parts.append(text)
            except Exception:
                pass

        # ── Text boxes (some designer templates put content in text boxes) ────
        try:
            body = doc.element.body
            for txbx in body.iter(qn("w:txbxContent")):
                for para in txbx.iter(qn("w:p")):
                    texts = [
                        node.text
                        for node in para.iter(qn("w:t"))
                        if node.text
                    ]
                    line = "".join(texts).strip()
                    if line:
                        parts.append(line)
        except Exception:
            pass

        return "\n".join(parts)

    except Exception as exc:
        raise ValueError(f"Failed to parse DOCX: {exc}") from exc
