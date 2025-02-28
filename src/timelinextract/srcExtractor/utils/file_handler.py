import os
import logging
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

logging.basicConfig(level=logging.INFO)

def save_temp_pdf(pdf_file):
    """Save the uploaded PDF file to a temporary location."""
    return default_storage.save(
        f"temp/{pdf_file.name}",
        ContentFile(pdf_file.read())
    )

def remove_temp_file(file_path):
    """Remove a temporary file after processing."""
    if os.path.exists(file_path):
        os.remove(file_path)
        logging.info(f"Temporary file {file_path} deleted.")