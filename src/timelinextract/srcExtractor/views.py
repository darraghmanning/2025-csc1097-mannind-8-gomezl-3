import json
import os
import time
import datetime
from django.http import JsonResponse
from pathlib import Path
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from srcExtractor.services.questionnaire_extraction import send_to_chatgpt
from srcExtractor.services.table_classifier import classify_all_tables_in_folder
from srcExtractor.services.table_extraction import extract_tables
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from srcExtractor.utils.pdf_validation import handle_pdf_upload
from srcExtractor.utils.data_processing import convert_valid_files_to_json
from srcExtractor.utils.match_questionnaires import find_matching_questionnaires

# Create your views here.
@csrf_exempt
def upload_pdf(request):
    """
    Handle PDF upload, process it with GPT and Adobe, and store necessary information in the database.

    Args:
        request (HttpRequest): The incoming HTTP request containing the PDF data.

    Returns:
        JsonResponse: JSON response with the status and result of the operation.
    """
    if request.method == 'POST':
        try:
            # Validate the file in the request
            if 'pdf_file' not in request.FILES:
                return JsonResponse({"error": "No PDF file provided in the request."}, status=400)

            # Get the uploaded file
            pdf_file = request.FILES['pdf_file']

            # Save the file temporarily
            temp_file_path = default_storage.save(
                f"temp/{pdf_file.name}",
                ContentFile(pdf_file.read())
            )

            data = {}

            # Step 1: Authenticate User
            """ Authenticate user using Google Log in API"""

            # Step 2: Handle PDF upload
            pdf_file_response = handle_pdf_upload(temp_file_path)
            if 'error' in pdf_file_response:
                return JsonResponse(pdf_file_response, status=400)
            
            # Extract and add file name
            file_name = os.path.basename(pdf_file_response["success"])
            data['file_name'] = file_name

            # Step 3: Add user to the database
            """ Code for the upload of user to database """

            # Step 4: Retrieve user ID
            """ Get the user ID from the database to link the PDF information extractracted to the user """

            # Step 5: Send PDF content to ChatGPT for processing
            start_time = time.time()
            start_date = datetime.datetime.now()
            data["upload_date"] = start_date
            data["created_at"] = start_date
            chatgpt_data = send_to_chatgpt(pdf_file_response["success"])
            end_time = time.time()

            data["response_time"] = str(end_time - start_time)
            data["processed_at"] = datetime.datetime.now()

            if 'error' in chatgpt_data:
                return JsonResponse(chatgpt_data, status=400)
            elif 'error_message' in chatgpt_data:
                data['error_message'] = chatgpt_data["error_message"]
            else:
                data['extracted_data'] = chatgpt_data["extracted_data"]
            data['response'] = chatgpt_data["response"]

            pdf_file_name = Path(file_name).stem

            # Step 6: Extract tables
            extract_tables_result = extract_tables(pdf_file_response["success"], pdf_file_name)
            if "error" in extract_tables_result:
                return JsonResponse(extract_tables_result, status=400)

            # Step 7: Classify the extracted tables
            valid_files = classify_all_tables_in_folder(f"table_extraction_output/extracted_{pdf_file_name}/tables")
            if "error" in valid_files:
                return JsonResponse(valid_files, status=400)

            # Step 8: Convert valid files tables to JSON
            if valid_files["success"]:
                convert_valid_files_to_json(valid_files["success"], f"table_extraction_output/json_{pdf_file_name}/")

            # Step 9: Extract Timelines that match with the previously extracted questionnaires
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

            # Success response
            print(f"Protocol {pdf_file_name} processed successfully, to see the results in a JSON file format go to output/{file_name}.")
            
            # Remove the temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

            return JsonResponse({"output": data['extracted_data']}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
    
    return JsonResponse({"message": "Waiting for a PDF to be uploaded."}, status=200)