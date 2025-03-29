import json
from bson.objectid import ObjectId
from . import mongodb


def add_tables(data):
    """
    Insert a table document associated with a user and a PDF into the database.

    Args:
        data (dict): Dictionary containing user_id, pdf_id, and classified tables.

    Returns:
        dict: Result message indicating success or failure.
    """
    tables_collection = mongodb.get_collection("Tables")
    users_collection = mongodb.get_collection("Users")
    pdf_collection = mongodb.get_collection("PDFs")

    user_id = data.get('user_id')
    pdf_id = data.get('pdf_id')
    classified_response = json.dumps(data.get('classified_response'))

    # Validation checks
    if not all([user_id, pdf_id, classified_response]):
        return {"error": "Missing required fields: user_id, pdf_id, or classified_response."}

    if not mongodb.is_valid_object_id(user_id):
        return {"error": "Invalid user_id format."}
    if not mongodb.is_user_id_valid(user_id, users_collection):
        return {"error": "user_id does not exist in the Users collection."}

    if not mongodb.is_valid_object_id(pdf_id):
        return {"error": "Invalid pdf_id format."}
    if not mongodb.is_pdf_id_valid(pdf_id, pdf_collection):
        return {"error": "pdf_id does not exist in the PDFs collection."}

    if not isinstance(classified_response, str) or not classified_response.strip():
        return {"error": "Response must be a non-empty string."}

    # Construct the new document
    new_query = {
        "user_id": ObjectId(user_id),
        "pdf_id": ObjectId(pdf_id),
        "classified_response": classified_response
    }

    try:
        result = tables_collection.insert_one(new_query)
        return {
            "message": "Tables metadata uploaded successfully.",
            "table_id": str(result.inserted_id)
        }
    except Exception as e:
        return {"error": f"Failed to upload tables metadata: {str(e)}"}
