import re
import os
import json
import csv
from .data_validation import is_json
from pathlib import Path
from difflib import SequenceMatcher


def clean_text(content):
    """
    Clean the provided text by replacing newlines with <br> tags and removing metadata.

    Args:
        content (str): Input text content.

    Returns:
        str: Cleaned text.
    """
    content = re.sub(r'\n', r'<br>', content)
    cleaned_text = re.sub(r'【[\d:†source]+】', '', content)
    return cleaned_text


def extract_json(content):
    """
    Extract JSON content from a string and clean it.

    Args:
        content (str): Input text containing JSON.

    Returns:
        str: Extracted and cleaned JSON content.
    """
    json_pattern = r'```json(.*?)\n```'
    json_match = re.search(json_pattern, content, re.DOTALL)
    return clean_text(json_match.group(1).strip() if json_match else content)


def save_merged_data_to_json(merged_data, pdf_file_path, output_directory='output'):
    """
    Save merged data to a JSON file with additional metadata.

    Args:
        merged_data (str): JSON string to save.
        pdf_file_path (str): Path of the original PDF file.
        output_directory (str): Directory to save the JSON file. Defaults to 'output'.

    Returns:
        dict: Success or error message.
    """
    try:
        directory = output_directory
        os.makedirs(directory, exist_ok=True)

        pdf_file_name = Path(pdf_file_path).stem
        saved_file_path = os.path.join(directory, f'{pdf_file_name}.json')

        # Replace <br> tags with newlines
        merged_data = re.sub(r'<br>', r'\n', merged_data)

        if is_json(merged_data):
            data_dict = json.loads(merged_data)

            with open(saved_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(data_dict, json_file, indent=4)
            return {"success": f"Data saved successfully to {saved_file_path}."}
        else:
            return {"error": "The provided data is not valid JSON."}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}


def csv_to_json(csv_file_path, json_file_path):
    """
    Convert a CSV file to a JSON file.

    Args:
        csv_file_path (str): Path to the CSV file.
        json_file_path (str): Path to save the JSON file.

    Returns:
        dict: Success or error message.
    """
    try:
        with open(csv_file_path, mode='r', encoding='utf-8-sig') as csv_file:
            reader = csv.reader(csv_file)
            header = next(reader)

            # Ensure headers are unique and non-empty
            first_row = next(reader)
            header = [col if col.strip() else first_row[i] for i, col in enumerate(header)]

            csv_file.seek(0)
            csv_reader = csv.DictReader(csv_file, fieldnames=header)
            next(csv_reader, None)  # Skip header row

            data = [row for row in csv_reader]

        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4)
        return {"success": "CSV file converted to JSON successfully."}
    except FileNotFoundError:
        return {"error": f"File not found: {csv_file_path}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred while turning a CSV file into a JSON file: {e}"}


def convert_valid_files_to_json(yes_files, output_folder):
    """
    Convert multiple CSV files classified as "YES" to JSON files.

    Args:
        yes_files (List[str]): List of CSV file paths.
        output_folder (str): Folder to save JSON files.

    Returns:
        dict: Success or error message.
    """
    try:
        os.makedirs(output_folder, exist_ok=True)

        for csv_file_path in yes_files:
            json_file_name = f"{Path(csv_file_path).stem}.json"
            json_file_path = os.path.join(output_folder, json_file_name)

            response = csv_to_json(csv_file_path, json_file_path)
            if "error" in response:
                return response
        return {"success": "All YES files successfully converted to JSON."}
    except Exception as e:
        return {"error": f"An unexpected error occurred while coverting yes files to json: {e}"}


def merge_json_files(folder_path1, folder_path2, output_file):
    """
    Merge JSON files from two directories into a single file.

    Args:
        folder_path1 (str): First directory containing JSON files.
        folder_path2 (str): Second directory containing JSON files.
        output_file (str): Path for the merged JSON file.

    Returns:
        dict: Success or error message.
    """
    try:
        merged_data = []

        for folder_path in [folder_path1, folder_path2]:
            for file_name in os.listdir(folder_path):
                if file_name.endswith('.json'):
                    file_path = os.path.join(folder_path, file_name)
                    with open(file_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                        if isinstance(data, list):
                            merged_data.extend(data)

        with open(output_file, 'w', encoding='utf-8') as out_file:
            json.dump(merged_data, out_file, indent=4)
        return {"success": f"JSON files merged successfully into {output_file}."}
    except Exception as e:
        return {"error": f"An unexpected error occurred while merging the JSON files: {e}"}


def similar(a, b):
    """
    Calculate the similarity ratio between two strings.

    Args:
        a (str): First string.
        b (str): Second string.

    Returns:
        float: Similarity ratio (0.0 to 1.0).
    """
    if a.lower().strip() in b.lower().strip():
        return 1.0
    return SequenceMatcher(None, a, b).ratio()


def extract_time_points(entry):
    """
    Extracts keys from a dictionary where the corresponding value is marked as "X" (case-insensitive).

    Args:
        entry (dict): Dictionary containing various key-value pairs.

    Returns:
        list: List of keys where the value is exactly "X".
    """
    return [key.strip() for key, value in entry.items() if isinstance(value, str) and value.strip().lower() == "x"]


def merge_json_files_into_one(pdf_file_name):
    """
    Merges all JSON files inside the folder table_extraction_output/json_<pdf_file_name>/
    into one JSON object.

    Args:
        pdf_file_name (str): The name of the PDF (without .pdf).

    Returns:
        dict: A dictionary containing either the merged data or an error message.
    """
    folder_path = Path(f"table_extraction_output/json_{pdf_file_name}/")
    merged_data = {}
    errors = []

    if not folder_path.exists() or not folder_path.is_dir():
        return {"error": f"Folder not found: {folder_path}"}

    for file in folder_path.glob("*.json"):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                file_name = file.stem
                merged_data[file_name] = data
        except Exception as e:
            errors.append(f"Error in {file.name}: {str(e)}")

    if errors:
        return {"error": errors}

    return {"success": merged_data}
