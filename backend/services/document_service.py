"""
Document processing service for PDF, image, and text file extraction.
"""

import io
import json
import os
import uuid
from typing import Tuple, List
from fastapi import HTTPException, UploadFile

from core.database import get_db, dict_from_row


def configure_tesseract():
    """Configure Tesseract path for Windows."""
    import pytesseract
    
    if os.name == 'nt':
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            os.path.expanduser(r'~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'),
        ]
        
        env_path = os.getenv('TESSERACT_PATH')
        if env_path:
            possible_paths.insert(0, env_path)
        
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                return True
        
        return False
    return True


async def process_document(file: UploadFile) -> dict:
    """Process uploaded document and extract text content."""
    content = await file.read()
    filename = file.filename or "unknown"
    extracted_text = ""
    
    if filename.lower().endswith('.pdf'):
        extracted_text = extract_from_pdf(content)
    elif filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
        extracted_text = extract_from_image(content)
    elif filename.lower().endswith(('.txt', '.md')):
        extracted_text = content.decode('utf-8', errors='ignore')
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF, images, or text files.")
    
    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from document")
    
    words, sentences = extract_vocabulary(extracted_text)
    
    doc_id = str(uuid.uuid4())
    conn = get_db()
    conn.execute(
        "INSERT INTO documents (id, filename, content, extracted_words, extracted_sentences) VALUES (?, ?, ?, ?, ?)",
        (doc_id, filename, extracted_text, json.dumps(words[:500]), json.dumps(sentences[:100]))
    )
    conn.commit()
    conn.close()
    
    return {
        "id": doc_id,
        "filename": filename,
        "word_count": len(words),
        "sentence_count": len(sentences),
        "preview": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text
    }


def extract_from_pdf(content: bytes) -> str:
    """Extract text from PDF."""
    try:
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text_parts = []
        for page in pdf_reader.pages:
            text_parts.append(page.extract_text())
        return "\n".join(text_parts)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF extraction failed: {str(e)}")


def extract_from_image(content: bytes) -> str:
    """Extract text from image using OCR (Tesseract)."""
    try:
        from PIL import Image
        import pytesseract
        
        if not configure_tesseract():
            raise HTTPException(
                status_code=500,
                detail="Tesseract not found. "
                       " set TESSERACT_PATH in your .env file."
            )
        
        image = Image.open(io.BytesIO(content))
        return pytesseract.image_to_string(image, lang='deu+eng')
    except ImportError:
        raise HTTPException(
            status_code=500, 
            detail="OCR dependencies not installed. Run: pip install pytesseract Pillow"
        )
    except pytesseract.TesseractNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="Tesseract not found. "
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OCR failed: {str(e)}")


def extract_vocabulary(text: str) -> Tuple[List[str], List[str]]:
    """Extract unique words and sentences from text."""
    words = list(set(
        w.lower() for w in text.split() 
        if len(w) > 2 and w.isalpha()
    ))
    
    sentences = [
        s.strip() for s in text.replace('\n', ' ').split('.') 
        if len(s.strip()) > 10
    ]
    
    return words, sentences


def get_document(doc_id: str) -> dict:
    """Get document by ID."""
    conn = get_db()
    doc = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
    conn.close()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc_dict = dict_from_row(doc)
    doc_dict["extracted_words"] = json.loads(doc_dict["extracted_words"]) if doc_dict["extracted_words"] else []
    doc_dict["extracted_sentences"] = json.loads(doc_dict["extracted_sentences"]) if doc_dict["extracted_sentences"] else []
    
    return doc_dict


def get_all_documents() -> List[dict]:
    """Get all documents metadata."""
    conn = get_db()
    rows = conn.execute(
        "SELECT id, filename, created_at FROM documents ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict_from_row(r) for r in rows]


def delete_document(doc_id: str) -> None:
    """Delete a document."""
    conn = get_db()
    conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()
