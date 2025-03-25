from bson import ObjectId
from . import mongodb


def add_query(data):
    """
    Insert a query document associated with a user and a PDF into the database.

    Args:
        data (dict): Dictionary containing user_id, pdf_id, and response.

    Returns:
        dict: Result message indicating success or failure.
    """
    queries_collection = mongodb.get_collection("Queries")
    users_collection = mongodb.get_collection("Users")
    pdf_collection = mongodb.get_collection("PDFs")

    user_id = data.get('user_id')
    pdf_id = data.get('pdf_id')
    response = data.get('response')

    # Validation checks
    if not all([user_id, pdf_id, response]):
        return {"error": "Missing required fields: user_id, pdf_id, or response."}

    if not mongodb.is_valid_object_id(user_id):
        return {"error": "Invalid user_id format."}
    if not mongodb.is_user_id_valid(user_id, users_collection):
        return {"error": "user_id does not exist in the Users collection."}

    if not mongodb.is_valid_object_id(pdf_id):
        return {"error": "Invalid pdf_id format."}
    if not mongodb.is_pdf_id_valid(pdf_id, pdf_collection):
        return {"error": "pdf_id does not exist in the PDFs collection."}

    if not isinstance(response, str) or not response.strip():
        return {"error": "Response must be a non-empty string."}

    # Construct the new document
    new_query = {
        "user_id": ObjectId(user_id),
        "pdf_id": ObjectId(pdf_id),
        "response": response.strip()
    }

    try:
        result = queries_collection.insert_one(new_query)
        return {
            "message": "Query metadata uploaded successfully.",
            "query_id": str(result.inserted_id)
        }
    except Exception as e:
        return {"error": f"Failed to upload query metadata: {str(e)}"}
