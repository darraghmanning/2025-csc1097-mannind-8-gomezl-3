import os
from .data_validation import extract_text_from_pdf

def handle_pdf_upload(pdf_file_path):
    """
    Handle the upload of a PDF file, validate it, and extract text.

    Args:
        data (string): A string containing the pdf file path.

    Returns:
        dict: A dictionary containing either a success message or an error message.
    """

    if not pdf_file_path:
        return {"error": "No PDF file in data."}
    
    # Validate the file type and size
    try:
        file_name = os.path.basename(pdf_file_path)
        file_size = os.path.getsize(pdf_file_path)

        if not file_name.endswith('.pdf'):
            return {"error": "Only PDF files are allowed."}

        if file_size == 0:
            return {"error": "Uploaded PDF file is empty."}
    except Exception as e:
        return {"error": f"Error validating the file: {e}"}
    
    # Extract text from the PDF file
    try:
        response = extract_text_from_pdf(pdf_file_path)
    except Exception as e:
        return {"error": f"Error extracting text from the PDF: {e}"}

    # Check for errors in the text extraction response
    if 'error' in response:
        return response

    return {"success": f"{pdf_file_path}"}