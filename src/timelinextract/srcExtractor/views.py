import os
import json
import logging
import time
from pathlib import Path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from srcExtractor.utils.pdf_validation import handle_pdf_upload
from srcExtractor.utils.pdf_processing import extract_and_classify_tables
from srcExtractor.utils.data_processing import merge_json_files_into_one
from srcExtractor.services.gpt.questionnaire_extraction import send_to_chatgpt
from srcExtractor.utils.file_handler import save_temp_pdf, remove_temp_file
from srcExtractor.utils.match_questionnaires import find_matching_questionnaires
from srcExtractor.services.mongodb.user import add_user
from srcExtractor.services.mongodb.pdf import add_pdf
from srcExtractor.services.mongodb.query import add_query
from srcExtractor.services.mongodb.table import add_tables
from srcExtractor.services.mongodb.output import add_output
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
import requests

User = get_user_model()


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
        data = {
            "file_name": os.path.basename(temp_file_path),
            "temp_file_path": temp_file_path
        }

        handle_pdf_upload_response = handle_pdf_upload(temp_file_path)
        if "error" in handle_pdf_upload_response:
            return JsonResponse(handle_pdf_upload_response, status=400)

        # Step 2: Authenticate User
        email = request.POST.get("email")

        if not email:
            return JsonResponse({"error": "Missing email."}, status=400)

        data.update({"email": email})

        # Step 3: Add user to the database
        """ Code for the upload of user to database """
        user_status = add_user(data)

        if "error" in user_status:
            return JsonResponse(user_status, status=500)

        data.update({"user_id": user_status.get("user_id")})

        start_time = time.time()
        # Step 5: Process PDF with ChatGPT
        chatgpt_data = send_to_chatgpt(temp_file_path)
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

        classified_response = merge_json_files_into_one(pdf_file_name)

        if "error" in classified_response:
            return JsonResponse(classified_response, status=400)

        data.update({"classified_response": classified_response["success"]})

        end_time = time.time()

        data.update({"response_time": f"{end_time - start_time:.2f}"})

        # Step 8: Add PDF information extraction to the database
        """ Code to upload PDF information extracted to the database """
        pdf_status = add_pdf(data)

        if "error" in pdf_status:
            return JsonResponse(pdf_status, status=500)

        data.update({"pdf_id": pdf_status.get("pdf_id")})

        query_status = add_query(data)

        if "error" in query_status:
            return JsonResponse(query_status, status=500)

        data.update({"query_id": query_status.get("query_id")})

        table_status = add_tables(data)

        if "error" in table_status:
            return JsonResponse(table_status, status=500)

        data.update({"table_id": table_status.get("table_id")})

        data.update({"output": data.get("extracted_data")})

        output_response = add_output(data)

        if "error" in output_response:
            return JsonResponse(output_response, status=500)

        # Step 9: Save Results and Cleanup
        remove_temp_file(temp_file_path)
        logging.info(f"Protocol {pdf_file_name} processed successfully.")

        return JsonResponse({"output": data['extracted_data']}, status=201)

    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON format: {e}")
        return JsonResponse({"error": "Invalid JSON format."}, status=400)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "Token is required"}, status=400)

        # Verify Google token
        google_response = requests.get(
            f"https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={token}"
        )
        google_data = google_response.json()

        if "email" not in google_data:
            return Response({"error": "Invalid Google token"}, status=400)

        email = google_data["email"]

        # Restrict access to DCU emails only
        if not email.endswith("@mail.dcu.ie"):
            return Response({"error": "Access restricted to DCU users only."}, status=403)

        first_name = google_data.get("given_name", "")
        last_name = google_data.get("family_name", "")

        # Check if user exists, otherwise create a new one
        user, created = User.objects.get_or_create(email=email, defaults={
            "first_name": first_name,
            "last_name": last_name,
            "username": email.split("@")[0],  # Ensure username uniqueness
        })

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        })
