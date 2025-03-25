import logging
from srcExtractor.services.adobe.table_extraction import extract_tables
from srcExtractor.services.gpt.table_classifier import classify_all_tables_in_folder
from srcExtractor.utils.data_processing import convert_valid_files_to_json

logging.basicConfig(level=logging.INFO)


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
