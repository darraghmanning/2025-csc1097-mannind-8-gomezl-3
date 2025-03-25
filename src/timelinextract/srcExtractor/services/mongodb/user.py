import re
from . import mongodb


def is_valid_email(email):
    """
    Validate email format using regular expressions.

    Args:
        email (str): Email address to validate.

    Returns:
        bool: True if the email is valid, False otherwise.
    """
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None


def add_user(data):
    """
    Add a new user to the database if not already present.

    Args:
        data (dict): Dictionary containing 'email'.

    Returns:
        dict: Result message or error.
    """
    email = data.get('email')

    if  not email:
        return {"error": "Missing required field: email."}

    if not is_valid_email(email):
        return {"error": "Invalid email format."}

    collection = mongodb.get_collection("Users")

    try:
        result = collection.find_one({"email": email})
        if result:
            return {"message": f"User '{email}' already exists.",
                    "user_id": str(result.get('_id'))
            }

        new_user = {"email": email}
        result = collection.insert_one(new_user)
        return {"message": f"User '{email}' created successfully.",
                "user_id": str(result.inserted_id)
        }

    except Exception as e:
        return {"error": f"Failed to add user: {str(e)}"}

