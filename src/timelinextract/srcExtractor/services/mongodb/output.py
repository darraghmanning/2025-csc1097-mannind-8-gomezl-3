import json
from bson.objectid import ObjectId
from . import mongodb


def add_output(data):
    """
    Insert an output document associated with a user, a PDF, a query and a table into the database.

    Args:
        data (dict): Dictionary containing user_id, pdf_id, query_id, table_id and output.

    Returns:
        dict: Result message indicating success or failure.
    """
    output_collection = mongodb.get_collection("Output")
    users_collection = mongodb.get_collection("Users")
    pdf_collection = mongodb.get_collection("PDFs")
    query_collection = mongodb.get_collection("Queries")
    table_collection = mongodb.get_collection("Tables")

    user_id = data.get('user_id')
    pdf_id = data.get('pdf_id')
    query_id = data.get('query_id')
    table_id = data.get('table_id')
    output = json.dumps(data.get('output'))
    response_time = data.get('response_time')

    # Validation checks
    if not all([user_id, pdf_id, query_id, table_id, output]):
        return {"error": "Missing required fields: user_id, pdf_id, query_id, table_id, or output."}

    if not mongodb.is_valid_object_id(user_id):
        return {"error": "Invalid user_id format."}
    if not mongodb.is_user_id_valid(user_id, users_collection):
        return {"error": "user_id does not exist in the Users collection."}

    if not mongodb.is_valid_object_id(pdf_id):
        return {"error": "Invalid pdf_id format."}
    if not mongodb.is_pdf_id_valid(pdf_id, pdf_collection):
        return {"error": "pdf_id does not exist in the PDFs collection."}

    if not mongodb.is_valid_object_id(query_id):
        return {"error": "Invalid query_id format."}
    if not mongodb.is_query_id_valid(query_id, query_collection):
        return {"error": "query_id does not exist in the Queries collection."}

    if not mongodb.is_valid_object_id(table_id):
        return {"error": "Invalid table_id format."}
    if not mongodb.is_table_id_valid(table_id, table_collection):
        return {"error": "table_id does not exist in the Tables collection."}

    if not isinstance(output, str) or not output.strip():
        return {"error": "Output must be a non-empty string."}

    if not isinstance(response_time, str) or len(response_time.strip()) == 0:
        return {"error": "response_time must be a non-empty string."}

    # Construct the new document
    new_query = {
        "user_id": ObjectId(user_id),
        "pdf_id": ObjectId(pdf_id),
        "query_id": ObjectId(query_id),
        "table_id": ObjectId(table_id),
        "output": output,
        "response_time": response_time
    }

    try:
        output_collection.insert_one(new_query)
        return {"message": "Output metadata uploaded successfully."}
    except Exception as e:
        return {"error": f"Failed to upload output metadata: {str(e)}"}
