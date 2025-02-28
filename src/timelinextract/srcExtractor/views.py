import os
import json
import logging
from pathlib import Path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from srcExtractor.utils.pdf_processing import process_pdf_with_chatgpt, extract_and_classify_tables
from srcExtractor.utils.file_handler import save_temp_pdf, remove_temp_file
from srcExtractor.utils.match_questionnaires import find_matching_questionnaires

@csrf_exempt
def upload_pdf(request):
    """
    Handle PDF upload, process it with GPT and Adobe, and store necessary information in the database.

    Args:
        request (HttpRequest): The incoming HTTP request containing the PDF data.

    Returns:
        JsonResponse: JSON response with the status and result of the operation.
    """
    if request.method != 'POST':
        return JsonResponse({"message": "Waiting for a PDF to be uploaded."}, status=200)

    try:
        # Step 1: Validate Request
        pdf_file = request.FILES.get('pdf_file')
        if not pdf_file:
            return JsonResponse({"error": "No PDF file provided in the request."}, status=400)

        temp_file_path = save_temp_pdf(pdf_file)
        data = {"file_name": os.path.basename(temp_file_path)}

        # Step 2: Authenticate User
        """ Authenticate user using Google Log in API"""

        # Step 3: Add user to the database
        """ Code for the upload of user to database """

        # Step 4: Retrieve user ID
        """ Get the user ID from the database to link the PDF information extractracted to the user """

        # Step 5: Process PDF with ChatGPT
        chatgpt_data = process_pdf_with_chatgpt(temp_file_path)
        if 'error' in chatgpt_data:
            return JsonResponse(chatgpt_data, status=400)

        data.update(chatgpt_data)
        pdf_file_name = Path(data['file_name']).stem

        # Step 6: Extract and Classify Tables
        tables_response = extract_and_classify_tables(temp_file_path, pdf_file_name)
        if "error" in tables_response:
            return JsonResponse(tables_response, status=400)

        # Step 7: Match Questionnaires with Extracted Timelines
        matching_questionnaires_response = find_matching_questionnaires(
            f"output/{pdf_file_name}.json",
            f"table_extraction_output/json_{pdf_file_name}/",
            similarity_threshold=0.6,
        )
        if "error" in matching_questionnaires_response:
            return JsonResponse(matching_questionnaires_response, status=400)

        data["extracted_data"] = matching_questionnaires_response["success"]

        # Step 8: Add PDF information extraction to the database
        """ Code to upload PDF information extracted to the database """

        # Step 9: Save Results and Cleanup
        remove_temp_file(temp_file_path)
        logging.info(f"Protocol {pdf_file_name} processed successfully.")
        
        return JsonResponse({"output": data['extracted_data']}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)