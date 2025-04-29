import gzip
import io
import os
from bson.objectid import ObjectId
from . import mongodb


def get_unique_file_name(file_name, collection):
    """
    Ensure that the file name is unique by appending a counter if needed.

    Args:
        file_name: The proposed file name.
        collection: MongoDB collection to check uniqueness.

    Returns:
        A unique file name string.
    """
    count = 1
    base_name, extension = file_name.rsplit('.', 1) if '.' in file_name else (file_name, '')
    new_file_name = file_name

    while collection.find_one({"file_name": new_file_name}):
        new_file_name = f"{base_name}_{count}.{extension}" if extension else f"{base_name}_{count}"
        count += 1

    return new_file_name


def add_pdf(data):
    """
    Add a PDF document reference to the database.

    Args:
        data (dict): A dictionary containing 'user_id', 'file_name', and 'file_object'.

    Returns:
        dict: A success or error message.
    """
    pdf_collection = mongodb.get_collection("PDFs")
    user_collection = mongodb.get_collection("Users")

    user_id = data.get('user_id')
    file_name = data.get('file_name')
    file_object = data.get('temp_file_path')

    # Validation
    if not all([user_id, file_name, file_object]):
        return {"error": "Missing required fields: user_id, file_name, or file_object."}

    if not mongodb.is_valid_object_id(user_id):
        return {"error": "Invalid user_id format."}

    if not mongodb.is_user_id_valid(user_id, user_collection):
        return {"error": "User ID does not exist in the Users collection."}

    if not isinstance(file_name, str) or not file_name.strip():
        return {"error": "file_name must be a non-empty string."}

    if len(file_name) > 255:
        return {"error": "file_name must be 255 characters or less."}

    unique_file_name = get_unique_file_name(file_name, pdf_collection)
    compressed_data = compress_file(file_object)

    if "error" in compressed_data:
        return compressed_data

    new_pdf = {
        "user_id": ObjectId(user_id),
        "file_name": unique_file_name,
        "file_object": compressed_data
    }

    try:
        result = pdf_collection.insert_one(new_pdf)

        return {
            "message": f"PDF '{unique_file_name}' uploaded successfully.",
            "pdf_id": str(result.inserted_id)
        }
    except Exception as e:
        return {"error": f"Failed to upload PDF metadata: {str(e)}"}


def compress_file(file_path):
    """
    Compresses a file using Gzip and returns the compressed binary data.

    Args:
        file_path (str): Path to the file to compress.

    Returns:
        bytes: Gzip-compressed file content.
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}

    try:
        with open(file_path, 'rb') as f:
            original_data = f.read()

        buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode='wb') as gz_file:
            gz_file.write(original_data)

        return {"success": buffer.getvalue()}

    except Exception as e:
        return {"error": f"Failed to compress file '{file_path}': {str(e)}"}
