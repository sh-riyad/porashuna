import os
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List
from app.schemas.document import UploadPDFRequest, DeletePDFRequest, PDFListResponse
from datetime import datetime
import uuid
from app.utils.PdfToImage import PdfToImage


DocumentRouter = APIRouter()


@DocumentRouter.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

   if not file.filename.endswith('.pdf'):
       raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be a PDF")

   # Read the PDF file content
   pdf_binary_data = await file.read()

   # Convert PDF to images
   image_binaries_list = PdfToImage(pdf_binary_data)

   if not image_binaries_list:
       raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to convert PDF to images")

   return {
       "message": "PDF uploaded and converted to images successfully",
       "file_name": file.filename,
       "number_of_images": len(image_binaries_list)
   }








# @DocumentRouter.delete("/delete", response_model=dict)
# async def delete_pdf(payload: DeletePDFRequest):
#     # Placeholder: In the future, delete the PDF from the vector store
#     # For now, just return a stub response
#     return {"message": "PDF delete endpoint (stub)", "pdf_id": payload.pdf_id}

# @DocumentRouter.get("/list", response_model=PDFListResponse)
# async def list_pdfs():
#     # Placeholder: In the future, list PDFs from the vector store
#     # For now, just return a stub response
#     return PDFListResponse(files=[])
