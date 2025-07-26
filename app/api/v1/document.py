import os
import tempfile
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, status
# from app.schemas.document import UploadPDFRequest, DeletePDFRequest, PDFListResponse
from app.services.multimodal_llm import multimodal_llm
from app.prompts.extract_text import PDF_EXTRACTION_PROMPT
import google.generativeai as genai
import base64
from app.utils.pdf_utils import split_pdf_to_chunks
from langchain.text_splitter import RecursiveCharacterTextSplitter, Language
from langchain_chroma import Chroma
from app.core.config import settings
from app.services.embedding_models import embeddings
import asyncio
import time

DocumentRouter = APIRouter()



# Initialize vector store (adjust persist_directory as needed)
vector_store = Chroma(
    persist_directory="./vector_db",
    embedding_function=embeddings
)



@DocumentRouter.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed.")
    
    try:
        start_time = time.time()  # Start timer

        # Split PDF into chunks
        result = split_pdf_to_chunks(file, chunk_size=5)

        # Get the temp directory path from the result
        temp_dir = Path(result["save_directory"])

        # Find all PDF chunks in the temp directory
        pdf_chunks = sorted(temp_dir.glob("*.pdf"))

        extracted_texts = []
        processed_chunks = []

        # Process each chunk with Gemini
        for chunk_path in pdf_chunks:
            try:
                uploaded_file = genai.upload_file(str(chunk_path), mime_type="application/pdf")
                response = multimodal_llm.generate_content([PDF_EXTRACTION_PROMPT, uploaded_file])
                genai.delete_file(uploaded_file.name)

                extracted_text = response.text if hasattr(response, 'text') else str(response)
                extracted_texts.append(extracted_text)

                processed_chunks.append({
                    "chunk_file": chunk_path.name,
                    "text_length": len(extracted_text),
                    "status": "success"
                })

            except Exception as chunk_error:
                processed_chunks.append({
                    "chunk_file": chunk_path.name,
                    "error": str(chunk_error),
                    "status": "failed"
                })
                continue

            # Gemini rate limit (3 req/min = 20s/request)
            await asyncio.sleep(20)

        # Combine markdown and save to .md file
        combined_text = "\n\n".join(extracted_texts)
        markdown_path = temp_dir / f"{Path(file.filename).stem}_extracted.md"
        with open(markdown_path, "w", encoding="utf-8") as md_file:
            md_file.write(combined_text)

        # Split text for embeddings
        text_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.MARKDOWN, 
            chunk_size=2000,
            chunk_overlap=200
        )
        
        # Split the combined text into chunks
        text_chunks = text_splitter.split_text(combined_text)
        
        # Create metadata for each chunk
        metadatas = []
        for i, chunk in enumerate(text_chunks):
            metadatas.append({
                "source": file.filename,
                "chunk_index": i,
                "total_chunks": len(text_chunks),
                "file_size": result["file_size"],
                "total_pages": result["total_pages"]
            })
        
        # Add documents to vector store
        vector_store.add_texts(
            texts=text_chunks,
            metadatas=metadatas
        )

        # # Clean up PDF chunks
        # for chunk_path in pdf_chunks:
        #     try:
        #         chunk_path.unlink()
        #     except:
        #         pass

        end_time = time.time()  # End timer
        total_extraction_time = round(end_time - start_time, 2)  # In seconds

        return {
            "message": "PDF processed, text extracted and saved to vector store successfully",
            "original_file": result["original_file"],
            "total_pages": result["total_pages"],
            "chunks_processed": len(processed_chunks),
            "chunks_extraction_details": processed_chunks,
            "file_size": result["file_size"],
            "text_length": len(combined_text),
            "markdown_file": str(markdown_path.resolve()),
            "vector_chunks_created": len(text_chunks),
            "extraction_time_seconds": total_extraction_time
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to process PDF file: {str(e)}")


   



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
