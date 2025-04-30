import re
import os
import json
import csv
from .data_validation import is_json
from pathlib import Path
from difflib import SequenceMatcher
from collections import Counter


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
    Convert a CSV file to a structured JSON file.

    This function reads a CSV file, handles multi-row headers, ensures column uniqueness,
    and writes the content to a JSON file.

    Args:
        csv_file_path (str): Path to the input CSV file.
        json_file_path (str): Path to save the output JSON file.

    Returns:
        dict: A dictionary with a "success" or "error" message.
    """
    try:
        with open(csv_file_path, mode="r", encoding="utf-8-sig") as csv_file:
            reader = csv.reader(csv_file)

            # Collect header rows until we find one with enough content
            header_rows = []
            while True:
                try:
                    row = next(reader)
                    header_rows.append(row)
                    if row.count("") < 2:
                        break
                except StopIteration:
                    return {"error": "No valid header row found in CSV."}

            # Merge multi-line headers into one
            merged_header = header_rows[-1]
            for previous in reversed(header_rows[:-1]):
                merged_header = merge_headers(previous, merged_header)

            # Add prefix from first column to clarify repeated headers
            prefix = merged_header[0].strip() if len(merged_header) > 1 else ""
            if prefix:
                merged_header = [
                    col if i == 0 else f"{prefix}: {col}".strip()
                    for i, col in enumerate(merged_header)
                ]

            # Make column names unique
            header_counts = Counter()
            unique_headers = []
            for col in merged_header:
                if col in header_counts:
                    header_counts[col] += 1
                    unique_headers.append(f"{col}_{header_counts[col]}")
                else:
                    header_counts[col] = 0
                    unique_headers.append(col)

            # Read the remaining rows into structured JSON
            data = [dict(zip(unique_headers, row)) for row in reader]

        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4)

        return {"success": "CSV successfully converted to JSON."}

    except FileNotFoundError:
        return {"error": f"File not found: {csv_file_path}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def merge_headers(old, new):
    """
    Merge two header rows by filling in blanks and combining mismatched labels.

    Args:
        old (List[str]): First header row.
        new (List[str]): Second header row.

    Returns:
        List[str]: Merged header row.
    """
    merged = []
    for old_val, new_val in zip(old, new):
        if not new_val and old_val:
            merged.append(old_val)
        elif old_val and new_val and old_val != new_val:
            merged.append(f"{new_val} ({old_val})")
        else:
            merged.append(new_val or "")
    return merged


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
    Calculate the similarity between two strings.
    Full containment or word match returns 1.0, otherwise uses SequenceMatcher.

    Args:
        a (str): First string.
        b (str): Second string.

    Returns:
        float: Similarity ratio between 0.0 and 1.0.
    """
    clean_a = clean_string(a)
    clean_b = clean_string(b)

    if clean_a in clean_b or words_in_other(a, b):
        return 1.0
    return SequenceMatcher(None, clean_a, clean_b).ratio()


def extract_time_points(entry):
    """
    Extract keys from a dictionary where the value indicates selection (e.g., contains 'x' or 'selected').

    Args:
        entry (dict): Dictionary representing a table row.

    Returns:
        list: List of keys with marked selection.
    """
    return [
        key.strip()
        for key, value in entry.items()
        if isinstance(value, str) and re.search(r"(x|\bselected\b)", value.strip().lower().replace("\ufffd", ""))
    ]


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


def clean_string(text):
    """
    Clean a string by removing non-alphanumeric characters, spaces, and appendix references.

    Args:
        text (str): Input string.

    Returns:
        str: Cleaned string.
    """
    # Remove appendix references like (Appendix A)
    cleaned_text = re.sub(r"\s*\(Appendix [A-Z]\)", "", text)
    # Remove non-alphanumeric characters and spaces, then lowercase
    return re.sub(r'\s+', '', re.sub(r'[^a-zA-Z0-9]', '', cleaned_text)).lower()

def words_in_other(a, b):
    """
    Check if all words from string 'a' exist within string 'b'.

    Args:
        a (str): First string.
        b (str): Second string.

    Returns:
        bool: True if all words in 'a' are found in 'b', False otherwise.
    """
    def to_words(s):
        return re.findall(r'\b\w+\b', s.lower())

    words_a = to_words(a)
    words_b = to_words(b)

    return all(word in words_b for word in words_a)
