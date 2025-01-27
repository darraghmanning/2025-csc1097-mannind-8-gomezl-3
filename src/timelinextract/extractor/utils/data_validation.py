import os
from PyPDF2 import PdfReader
import json
from django.conf import settings

def extract_text_from_pdf(pdf_file):
    """
    Extract text from a PDF file and validate it.

    Args:
        pdf_file (str): Path to the PDF file.

    Returns:
        dict: A dictionary with either success status or an error message.
    """
    try:
        reader = PdfReader(pdf_file)
        text = "".join(page.extract_text() for page in reader.pages)

        # Validate the extracted text
        if not text.strip():
            return {"error": "Extracted text is empty."}
        elif all(ord(char) < 128 for char in text):
            return {"error": "Extracted text contains non-ASCII characters."}

        if not is_verbal_text(text):
            return {"error": "The provided text does not appear to be verbal text."}
        
        return {"success": True}
    except Exception as e:
        return {"error": f"Error processing PDF: {str(e)}"}

def load_common_words(filepath):
    """
    Load common English words from a specified file.

    Args:
        filepath (str): Path to the file containing common words.

    Returns:
        set: A set of common English words.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return set(word.strip().lower() for word in file.readlines())
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except Exception as e:
        raise RuntimeError(f"Error loading common words file: {e}")

def is_verbal_text(text):
    """
    Check if the extracted text from the PDF appears to be verbal text.

    Args:
        text (str): The extracted text.

    Returns:
        bool: True if the text is verbal, otherwise False.
    """
    try:
        # Load common words from the predefined file
        common_words_path = os.path.join(settings.BASE_DIR, 'extractor', 'static', 'files', 'common_words.txt')
        common_english_words = load_common_words(common_words_path)

        # Convert text to lowercase and remove spaces
        text = text.lower().replace(" ", "")

        # Calculate the proportion of common English words in the text
        num_english_words = sum(1 for word in common_english_words if word in text)
        proportion_english_words = num_english_words / len(common_english_words)

        #Check the proportion of common English words
        num_english_words = sum(1 for word in common_english_words if word in text)
        proportion_english_words = num_english_words / len(common_english_words)
        
        return proportion_english_words >= 0.1
    except Exception as e:
        raise RuntimeError(f"Error determining if text is verbal: {e}")

def is_json(my_data):
    """
    Check if a string can be parsed as valid JSON.

    Args:
        my_data (str): The string to check.

    Returns:
        bool: True if the string is valid JSON, otherwise False.
    """
    try:
        json.loads(my_data)
        return True
    except json.JSONDecodeError:
        return False