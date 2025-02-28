import os
import zipfile
from dotenv import load_dotenv
from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_pdf_params import ExtractPDFParams
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.table_structure_type import TableStructureType
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_pdf_params import ExtractPDFParams
from adobe.pdfservices.operation.pdfjobs.result.extract_pdf_result import ExtractPDFResult
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, SdkException
from adobe.pdfservices.operation.pdfjobs.jobs.extract_pdf_job import ExtractPDFJob

# Load .env file
load_dotenv()

def extract_tables(pdf_file, file_name):
    """
    Extracts tables from a PDF file using Adobe PDF Services.

    Args:
        pdf_file (str): Path to the PDF file.
        file_name (str): Name of the output file without extension.

    Returns:
        dict: Success or error message.
    """
    print(f"Starting the extraction of tables from this file: {file_name}")
    try:
        # Step 1: Read the PDF file
        with open(pdf_file, "rb") as file:
            input_stream = file.read()

        client_id=os.getenv('PDF_SERVICES_CLIENT_ID')
        client_secret=os.getenv('PDF_SERVICES_CLIENT_SECRET')

        if not client_id or not client_secret:
            return {"error": "Adobe API client id or secret not found. Please set the PDF_SERVICES_CLIENT_ID and PDF_SERVICES_CLIENT_SECRET environment variable."}

        # Step 2: Initialize Adobe PDF Services credentials
        credentials = ServicePrincipalCredentials(client_id, client_secret)

        # Step 3: Create a PDF Services instance
        pdf_services = PDFServices(credentials=credentials)
        
        # Step 4: Upload the PDF file
        input_asset = pdf_services.upload(input_stream=input_stream, mime_type=PDFServicesMediaType.PDF)

        # Step 5: Define extraction parameters
        extract_pdf_params = ExtractPDFParams(
            elements_to_extract=[ExtractElementType.TABLES],
            table_structure_type=TableStructureType.CSV,
        )

        # Step 6: Submit the extraction job
        extract_pdf_job = ExtractPDFJob(input_asset=input_asset, extract_pdf_params=extract_pdf_params)
        location = pdf_services.submit(pdf_services_job=extract_pdf_job)
        pdf_services_response = pdf_services.get_job_result(location, ExtractPDFResult)

        # Step 7: Retrieve the extraction result
        result_asset = pdf_services_response.get_result().get_resource()
        stream_asset = pdf_services.get_content(result_asset)

        # Step 8: Save the result as a zip file
        os.makedirs("table_extraction_output", exist_ok=True)
        output_file_path = f"table_extraction_output/{file_name}.zip"
        with open(output_file_path, "wb") as file:
            file.write(stream_asset.get_input_stream())

        # Step 9: Unzip the output file
        unzip_response = unzip_file(output_file_path, file_name)

        if "error" in unzip_response:
            return unzip_response
        
        print(f"Extraction of tables completed successfully for {file_name}")

        return {"success": f"Tables from PDF file were extracted successfully {output_file_path}"}
    except (ServiceApiException, SdkException) as e:
        return {"error": f"Failed to extract tables from the PDF file: {str(e)}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

def unzip_file(zip_file_path, output_dir):
    """
    Unzips a zip file to a specified directory.

    Args:
        zip_file_path (str): Path to the zip file.
        output_dir (str): Directory to extract the files to.

    Returns:
        dict: Success or error message.
    """
    try:
        extract_path = f'table_extraction_output/extracted_{output_dir}'
        os.makedirs(extract_path, exist_ok=True)

        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
            return {"success" : f"Extracted all files to {extract_path}"}
    except zipfile.BadZipFile:
        return {"error": f"The file at {zip_file_path} is not a valid zip file or is corrupted."}
    except Exception as e:
        return {"error": f"An unexpected error occurred while unzipping the file: {str(e)}"}