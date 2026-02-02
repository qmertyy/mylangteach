"""
Documents API routes
"""

from fastapi import APIRouter, UploadFile, File

from services.document_service import (
    process_document,
    get_document,
    get_all_documents,
    delete_document
)

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("")
async def list_documents():
    """List all uploaded documents"""
    return get_all_documents()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document (PDF, image, or text)"""
    return await process_document(file)


@router.get("/{doc_id}")
async def get_document_detail(doc_id: str):
    """Get document details including extracted words and sentences"""
    return get_document(doc_id)


@router.delete("/{doc_id}")
async def delete_document_endpoint(doc_id: str):
    """Delete a document"""
    delete_document(doc_id)
    return {"status": "deleted"}
