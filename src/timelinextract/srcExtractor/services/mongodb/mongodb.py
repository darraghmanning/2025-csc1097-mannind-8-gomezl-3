import os
import logging
from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve the MongoDB URI
MONGO_URI = os.getenv("MONGODB_URI")


def get_mongo_client():
    """
    Establish and return a MongoDB client.

    Returns:
        MongoClient: An instance of the MongoDB client.

    Raises:
        ValueError: If MONGO_URI is not set.
        ConnectionFailure: If unable to connect to MongoDB.
    """
    if not MONGO_URI:
        logger.error("MONGO_URI not set in environment variables.")
        raise ValueError("MONGO_URI is required in the environment.")

    try:
        client = MongoClient(MONGO_URI)
        client.admin.command("ping")
        logger.info("MongoDB connection established.")
        return client
    except (ConnectionFailure, ConfigurationError) as e:
        logger.error(f"MongoDB connection error: {e}")
        raise


def get_database():
    """
    Get the specified MongoDB database.

    Returns:
        Database: MongoDB database object.
    """
    client = get_mongo_client()
    return client['timelinextract']


def get_collection(collection_name):
    """
    Get the specified MongoDB collection.

    Returns:
        Collection: MongoDB collection object.
    """
    db = get_database()
    return db[collection_name]


def is_valid_object_id(oid):
    """Validate whether the string is a valid MongoDB ObjectId."""
    return ObjectId.is_valid(oid)


def is_user_id_valid(user_id, users_collection):
    """Check if the user ID exists in the Users collection."""
    return users_collection.find_one({'_id': ObjectId(user_id)}) is not None


def is_pdf_id_valid(pdf_id, pdf_collection):
    """Check if the PDF ID exists in the PDFs collection."""
    return pdf_collection.find_one({'_id': ObjectId(pdf_id)}) is not None


def is_query_id_valid(query_id, query_collection):
    """Check if the query ID exists in the Queries collection."""
    return query_collection.find_one({'_id': ObjectId(query_id)}) is not None


def is_table_id_valid(table_id, table_collection):
    """Check if the table ID exists in the Tables collection."""
    return table_collection.find_one({'_id': ObjectId(table_id)}) is not None
