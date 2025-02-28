import os
import openai
from dotenv import load_dotenv
from pathlib import Path
from srcExtractor.utils.data_processing import extract_json, save_merged_data_to_json
from srcExtractor.utils.prompts import PROMPTS

# Load .env file
load_dotenv()

def openai_run(client, pdf_file, file_response, prompt):
    """
    Extract information by creating and polling a thread run.

    Args:
        client: The OpenAI client instance.
        pdf_file (Path): The uploaded PDF file.
        file_response (dict): The response from the file upload API.
        assistant_id (str): The assistant ID to use.

    Returns:
        str or None: Extracted protocol information or None if extraction failed.
    """

    thread = client.beta.threads.create(messages=[{
        "role": "user",
        "content": f"Analyse the attached file called {pdf_file} and follow the instructions: {prompt}",
        "attachments": [{"file_id": file_response.id, "tools": [{"type": "file_search"}]}]
    }])
    run = client.beta.threads.runs.create_and_poll(thread_id=thread.id, assistant_id='asst_ax901pyhjedCgjxeo1X8cAne')

    if run.status == 'completed':
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        if messages.data:
            return messages.data[0].content[0].text.value
    return None

def send_to_chatgpt(pdf_file_path):
    """
    Handle a PDF file upload and interact with GPT for extracting protocol information.

    Args:
        pdf_file_path (str): Path to the PDF file to be processed.

    Returns:
        dict: A dictionary containing either extracted data or an error message.
    """
    print(f"Processing PDF file: {pdf_file_path}")

    protocol_prompt = PROMPTS["protocol_extraction"]
    questionnaire_prompt = PROMPTS["questionnaire_extraction"]
 
    api_key = os.getenv('CHATGPT_API_KEY')

    if not api_key:
        return {"error": "API key not found. Please set the CHATGPT_API_KEY environment variable."}

    openai.api_key = api_key

    try:
        # Step 1: Upload file
        with open(pdf_file_path, "rb") as file:
            file_response = openai.files.create(file=file, purpose='assistants')

        print(f"Starting OpenAI extraction for file: {pdf_file_path}")

        # Step 2: Extract protocol information
        protocol_content = openai_run(openai, pdf_file_path, file_response, protocol_prompt)

        if not protocol_content:
            return {"error": "Failed to extract protocol information."}

        # Step 3: Extract questionnaires
        questionnaire_content = openai_run(openai, pdf_file_path, file_response, questionnaire_prompt)

        if not questionnaire_content:
            return {"error": "Failed to extract questionnaire information."}
        
        # Step 4: Merge and save the extracted data
        extracted_protocol = extract_json(protocol_content)
        extracted_questionnaires = extract_json(questionnaire_content)
        merged_data = extracted_protocol[:-5] + ',' + extracted_questionnaires[1:]

        save_status = save_merged_data_to_json(merged_data, pdf_file_path)

        combined_response = protocol_content + ' ' + questionnaire_content

        if "error" in save_status:
            return {
                "error_message": save_status,
                "response": combined_response
            }

        print(f"Extraction and merging completed successfully for {pdf_file_path}")

        return {
            "extracted_data": save_status,
            "response": combined_response
        }
    except Exception as e:
        return {"error": f"Failed to process PDF with GPT-4o: {str(e)}"}