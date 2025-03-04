import time
import datetime
import logging
from srcExtractor.services.questionnaire_extraction import send_to_chatgpt
from srcExtractor.services.table_extraction import extract_tables
from srcExtractor.services.table_classifier import classify_all_tables_in_folder
from srcExtractor.utils.data_processing import convert_valid_files_to_json

logging.basicConfig(level=logging.INFO)

def process_pdf_with_chatgpt(pdf_file_path):
    """Process the uploaded PDF file with ChatGPT and return extracted data."""
    try:
        start_time = time.time()
        chatgpt_data = send_to_chatgpt(pdf_file_path)
        end_time = time.time()

        return {
            "response_time": str(end_time - start_time),
            "processed_at": datetime.datetime.now(),
            "extracted_data": chatgpt_data.get("extracted_data", ""),
            "response": chatgpt_data.get("response", ""),
            "error_message": chatgpt_data.get("error_message", "")
        }
    except Exception as e:
        logging.error(f"Error processing PDF with ChatGPT: {e}")
        return {"error": "Failed to process PDF with ChatGPT"}

def extract_and_classify_tables(pdf_file_path, pdf_file_name):
    """Extract tables from a PDF and classify them."""
    try:
        tables_result = extract_tables(pdf_file_path, pdf_file_name)
        if "error" in tables_result:
            return tables_result

        valid_files = classify_all_tables_in_folder(f"table_extraction_output/extracted_{pdf_file_name}/tables")
        
        if not valid_files:
            return {"error": "No Schedule of Events table found in the protocol."}

        if "error" in valid_files:
            return valid_files

        # Convert valid tables to JSON
        if valid_files["success"]:
            convert_valid_files_to_json(valid_files["success"], f"table_extraction_output/json_{pdf_file_name}/")

        return {"valid_files": valid_files["success"]}
    except Exception as e:
        logging.error(f"Error extracting and classifying tables: {e}")
        return {"error": "Failed to extract or classify tables"}
