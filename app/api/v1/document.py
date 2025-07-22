from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List
from app.schemas.document import UploadPDFRequest, DeletePDFRequest, PDFListResponse

router = APIRouter()

@router.post("/upload", response_model=dict)
async def upload_pdf(file: UploadFile = File(...), payload: UploadPDFRequest = None):
    # Placeholder: In the future, store the PDF in a vector store
    # For now, just return a stub response
    return {"message": "PDF upload endpoint (stub)", "filename": file.filename}

@router.delete("/delete", response_model=dict)
async def delete_pdf(payload: DeletePDFRequest):
    # Placeholder: In the future, delete the PDF from the vector store
    # For now, just return a stub response
    return {"message": "PDF delete endpoint (stub)", "pdf_id": payload.pdf_id}

@router.get("/list", response_model=PDFListResponse)
async def list_pdfs():
    # Placeholder: In the future, list PDFs from the vector store
    # For now, just return a stub response
    return PDFListResponse(files=[])
