from django.shortcuts import render
import json
import os
import time
import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from extractor.services.questionnaire_extraction import send_to_chatgpt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from extractor.utils.pdf_validation import handle_pdf_upload

# Create your views here.
@csrf_exempt
def upload_pdf(request):
    """
    Handle PDF upload, process it with GPT, and store necessary information in the database.

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

            # Step 6: Add PDF information extraction to the database
            """ Code to upload PDF information extracted to the database """

            # Success response
            return JsonResponse({"message": "The PDF was uploaded successfully, and we returned the necessary information to the database."}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
    
    return JsonResponse({"message": "Waiting for a PDF to be uploaded."}, status=200)