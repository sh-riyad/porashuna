from pathlib import Path
from io import BytesIO
import PyPDF2
from fastapi import UploadFile
import os
from langsmith import traceable

@traceable(name="split_pdf_to_chunks")
def split_pdf_to_chunks(file: UploadFile, chunk_size: int = 5) -> dict:
    
    # Create temp directory
    TEMP_DIR = Path(__file__).parent.parent.parent / "temp"
    TEMP_DIR.mkdir(exist_ok=True)

    file_content = file.file.read()
    pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
    total_pages = len(pdf_reader.pages)
    chunks_created = []

    base_name = file.filename.replace('.pdf', '')

    # Log initial metadata for tracing
    trace_metadata = {
        "original_filename": file.filename,
        "total_pages": total_pages,
        "chunk_size": chunk_size,
        "file_size_kb": round(len(file_content) / 1024, 2)
    }

    for start_page in range(0, total_pages, chunk_size):
        end_page = min(start_page + chunk_size, total_pages)
        pdf_writer = PyPDF2.PdfWriter()

        for page_num in range(start_page, end_page):
            pdf_writer.add_page(pdf_reader.pages[page_num])

        chunk_number = (start_page // chunk_size) + 1
        chunk_filename = f"{base_name}_chunk_{chunk_number:03d}.pdf"
        chunk_path = TEMP_DIR / chunk_filename

        with open(chunk_path, "wb") as chunk_file:
            pdf_writer.write(chunk_file)

        chunks_created.append({
            "chunk_number": chunk_number,
            "filename": chunk_filename,
            "path": str(chunk_path),
            "pages": f"{start_page + 1}-{end_page}",
            "page_count": end_page - start_page
        })

    result = {
        "message": "PDF file uploaded and split successfully",
        "original_file": file.filename,
        "total_pages": sum(chunk["page_count"] for chunk in chunks_created),
        "chunks_created": len(chunks_created),
        "file_size": f"{round(len(file_content) / 1024, 2)} KB",
        "save_directory": str(TEMP_DIR.resolve()),
        "chunks_info": chunks_created
    }
    
    return result
