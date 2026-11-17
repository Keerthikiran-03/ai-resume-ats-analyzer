import io
import re
from typing import Tuple, Dict, Any
import pypdf
import docx

def extract_text_from_pdf(file_bytes: bytes) -> Tuple[str, Dict[str, Any]]:
    """Extracts text and metadata from a PDF file with robust error handling."""
    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        num_pages = len(reader.pages)
        text_parts = []
        
        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text() or ""
                text_parts.append(page_text)
            except Exception as pe:
                text_parts.append(f"")
        
        raw_text = "\n".join(text_parts)
        clean_text = clean_extracted_text(raw_text)
        
        metadata = {
            "format": "pdf",
            "num_pages": num_pages,
            "char_count": len(clean_text),
            "is_scanned_or_empty": len(clean_text.strip()) < 30
        }
        return clean_text, metadata
    except Exception as e:
        # Fallback raw string extraction
        raw_fallback = extract_printable_strings(file_bytes)
        clean_text = clean_extracted_text(raw_fallback)
        return clean_text, {
            "format": "pdf",
            "num_pages": 1,
            "char_count": len(clean_text),
            "is_scanned_or_empty": len(clean_text.strip()) < 30,
            "fallback_used": True
        }

def extract_text_from_docx(file_bytes: bytes) -> Tuple[str, Dict[str, Any]]:
    """Extracts text and table content from a DOCX file."""
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        
        # Also extract table contents (often used in resumes)
        table_texts = []
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    table_texts.append(row_text)
                    
        full_text = "\n".join(paragraphs + table_texts)
        clean_text = clean_extracted_text(full_text)
        
        metadata = {
            "format": "docx",
            "num_paragraphs": len(paragraphs),
            "num_tables": len(doc.tables),
            "char_count": len(clean_text),
            "is_scanned_or_empty": len(clean_text.strip()) < 30
        }
        return clean_text, metadata
    except Exception as e:
        # Fallback raw string extraction for legacy .doc or unzipped docx
        raw_fallback = extract_printable_strings(file_bytes)
        clean_text = clean_extracted_text(raw_fallback)
        return clean_text, {
            "format": "doc/docx",
            "num_paragraphs": 1,
            "num_tables": 0,
            "char_count": len(clean_text),
            "is_scanned_or_empty": len(clean_text.strip()) < 30,
            "fallback_used": True
        }

def extract_printable_strings(data: bytes, min_len: int = 4) -> str:
    """Extracts ASCII/UTF-8 strings from binary data as a resilient fallback."""
    result = []
    # Find readable words / sentences
    matches = re.findall(b'[\x20-\x7E\r\n\t]{' + str(min_len).encode() + b',}', data)
    for m in matches:
        try:
            decoded = m.decode('utf-8', errors='ignore').strip()
            if len(decoded) >= min_len and not decoded.startswith(('<<', '>>', 'obj', 'endobj', 'stream')):
                result.append(decoded)
        except Exception:
            continue
    return "\n".join(result)

def extract_text(file_bytes: bytes, filename: str) -> Tuple[str, Dict[str, Any]]:
    """Routes file to appropriate extractor based on filename extension."""
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    
    if ext == 'pdf':
        return extract_text_from_pdf(file_bytes)
    elif ext in ['docx', 'doc']:
        return extract_text_from_docx(file_bytes)
    elif ext in ['txt', 'md', 'rtf', 'html', 'htm']:
        text = file_bytes.decode('utf-8', errors='ignore')
        clean = clean_extracted_text(text)
        return clean, {"format": ext, "num_pages": 1, "char_count": len(clean), "is_scanned_or_empty": len(clean.strip()) < 30}
    else:
        # Try decoding as text or fallback
        try:
            text = file_bytes.decode('utf-8', errors='ignore')
            clean = clean_extracted_text(text)
            if len(clean.strip()) >= 30:
                return clean, {"format": "text", "num_pages": 1, "char_count": len(clean), "is_scanned_or_empty": False}
        except Exception:
            pass
        fallback = extract_printable_strings(file_bytes)
        clean = clean_extracted_text(fallback)
        return clean, {"format": ext or "unknown", "num_pages": 1, "char_count": len(clean), "is_scanned_or_empty": len(clean.strip()) < 30}

def clean_extracted_text(text: str) -> str:
    """Normalizes whitespace and removes null bytes or weird artifacts."""
    if not text:
        return ""
    # Strip null characters which break JSON
    text = text.replace('\x00', ' ')
    # Standardize newlines
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Replace multiple spaces with a single space
    text = re.sub(r'[ \t]+', ' ', text)
    # Condense 3+ consecutive newlines to 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()
