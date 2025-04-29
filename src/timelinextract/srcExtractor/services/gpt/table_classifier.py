import os
import openai
from dotenv import load_dotenv
from srcExtractor.utils.prompts import PROMPTS

# Load .env file
load_dotenv()


def classify_table(csv_file_path):
    """
    Classifies a given CSV file as a Schedule of Events (SoE) table or not.

    Args:
        csv_file_path (str): Path to the CSV file.

    Returns:
        dict: {"success": "YES"} if it's an SoE table, {"success": "NO"} otherwise, or an error message.
    """
    classifier_prompt = PROMPTS["table_classifier"]

    api_key = os.getenv('CHATGPT_API_KEY')
    if not api_key:
        return {"error": "API key not found. Please set the CHATGPT_API_KEY environment variable."}

    openai.api_key = api_key
    MODEL = "gpt-4o"

    try:
        # Ensure the file exists
        if not os.path.isfile(csv_file_path):
            return {"error": f"CSV file not found: {csv_file_path}"}

        with open(csv_file_path, "r") as file:
            csv_content = file.read()

        response = openai.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant that processes tables from clinical trial documents."},
                {"role": "user", "content": f"Analyse the following input table (CSV format) {csv_content} and follow the instructions: {classifier_prompt}"}
            ],
            model=MODEL,
        )
        return {"success": response.choices[0].message.content.strip()}
    except Exception as e:
        return {"error": f"Failed to process CSV content with GPT-4o: {str(e)}"}


def classify_all_tables_in_folder(folder_path):
    """
    Classifies all CSV files in the specified folder as Schedule of Events (SoE) tables or not.

    Args:
        folder_path (str): Path to the folder containing CSV files.

    Returns:
        dict: {"success": [list of file paths classified as "YES"]} or an error message.
    """
    try:
        # Ensure the folder exists
        if not os.path.isdir(folder_path):
            return {"error": f"Folder not found: {folder_path}"}

        # List to store filenames that get a "YES"
        yes_files = []

        # Iterate over all files in the folder
        for filename in os.listdir(folder_path):
            # Get the full file path
            file_path = os.path.join(folder_path, filename)

            # Check if the file is a CSV
            if os.path.isfile(file_path) and filename.endswith(".csv"):
                # Call classify_table for each CSV file
                try:
                    result = classify_table(file_path)
                    if "error" in result:
                        return result
                    if "yes" in result["success"].lower():
                        yes_files.append(folder_path + "/" + filename)
                except Exception as e:
                    return {"error": f"Error processing {filename}: {e}"}
        return {"success": yes_files}
    except Exception as e:
        return {"error": f"Failed to classify all CSV files in the specified folder as a Schedule of Events (SoE) or not: {str(e)}"}
