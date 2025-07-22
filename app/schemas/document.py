from pydantic import BaseModel, Field
from typing import List, Optional

class UploadPDFRequest(BaseModel):
    # Add fields as needed for upload metadata (stub for now)
    description: Optional[str] = Field(None, description="Optional description of the PDF.")

class DeletePDFRequest(BaseModel):
    pdf_id: str = Field(..., description="The unique identifier of the PDF to delete.")

class PDFListResponse(BaseModel):
    files: List[str] = Field(default_factory=list, description="List of available PDF filenames or IDs.") 