import pymupdf

def PdfToImage(pdf_binary_data: bytes) -> list[bytes]:
    """
    Converts a PDF's binary content into a list of binary image data (PNG format).

    Args:
        pdf_binary_data: The binary content of the PDF file.

    Returns:
        A list of bytes, where each item is the binary content of a page image (PNG).
        Returns an empty list if conversion fails.
    """
    image_binaries = []

    try:
        # Open the PDF from binary data
        doc = pymupdf.open(stream=pdf_binary_data, filetype="pdf")

        # Iterate through each page and convert to image binary
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=200)
            image_binaries.append(pix.tobytes(format="png"))

        doc.close()
    
    except Exception as e:
        return []

    return image_binaries