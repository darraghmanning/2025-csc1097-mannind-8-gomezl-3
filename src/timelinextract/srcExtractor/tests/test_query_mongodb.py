from django.test import TestCase
from unittest.mock import patch, MagicMock
from bson.objectid import ObjectId
from srcExtractor.services.mongodb import query


class QueryMongoDBTests(TestCase):

    def setUp(self):
        self.valid_user_id = str(ObjectId())
        self.valid_pdf_id = str(ObjectId())
        self.valid_response = "Sample response."

    @patch("srcExtractor.services.mongodb.query.mongodb.get_collection")
    def test_add_query_missing_fields(self, mock_get_collection):
        """Should return error if required fields are missing"""
        result = query.add_query({})
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Missing required fields: user_id, pdf_id, or response.")

    @patch("srcExtractor.services.mongodb.query.mongodb.get_collection")
    @patch("srcExtractor.services.mongodb.query.mongodb.is_valid_object_id", return_value=False)
    def test_add_query_invalid_user_id_format(self, _, mock_get_collection):
        """Should return error if ObjectId format is invalid"""
        result = query.add_query({
            "user_id": "invalid",
            "pdf_id": self.valid_pdf_id,
            "response": self.valid_response
        })
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Invalid user_id format.")

    @patch("srcExtractor.services.mongodb.query.mongodb.get_collection")
    @patch("srcExtractor.services.mongodb.query.mongodb.is_valid_object_id", side_effect=[True, True])
    @patch("srcExtractor.services.mongodb.query.mongodb.is_user_id_valid", return_value=False)
    def test_add_query_user_id_not_found(self, mock_user_valid, mock_obj_id, mock_get_collection):
        """Should return error if user ID doesn't exist in DB"""
        result = query.add_query({
            "user_id": self.valid_user_id,
            "pdf_id": self.valid_pdf_id,
            "response": self.valid_response
        })
        self.assertIn("error", result)
        self.assertEqual(result["error"], "user_id does not exist in the Users collection.")

    @patch("srcExtractor.services.mongodb.query.mongodb.get_collection")
    @patch("srcExtractor.services.mongodb.query.mongodb.is_valid_object_id", side_effect=[True, False])
    @patch("srcExtractor.services.mongodb.query.mongodb.is_user_id_valid", return_value=True)
    def test_add_query_invalid_pdf_id_format(self, _, __, mock_get_collection):
        """Should return error if ObjectId format is invalid"""
        result = query.add_query({
            "user_id": self.valid_user_id,
            "pdf_id": "invalid",
            "response": self.valid_response
        })
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Invalid pdf_id format.")

    @patch("srcExtractor.services.mongodb.query.mongodb.get_collection")
    @patch("srcExtractor.services.mongodb.query.mongodb.is_valid_object_id", side_effect=[True, True])
    @patch("srcExtractor.services.mongodb.query.mongodb.is_user_id_valid", return_value=True)
    @patch("srcExtractor.services.mongodb.query.mongodb.is_pdf_id_valid", return_value=False)
    def test_add_query_pdf_id_not_found(self, *mocks):
        """Should return error if pdf ID doesn't exist in DB"""
        result = query.add_query({
            "user_id": self.valid_user_id,
            "pdf_id": self.valid_pdf_id,
            "response": self.valid_response
        })
        self.assertIn("error", result)
        self.assertEqual(result["error"], "pdf_id does not exist in the PDFs collection.")

    @patch("srcExtractor.services.mongodb.query.mongodb.get_collection")
    def test_add_query_invalid_response_type(self, mock_get_collection):
        result = query.add_query({
            "user_id": self.valid_user_id,
            "pdf_id": self.valid_pdf_id,
            "response": " "
        })
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Response must be a non-empty string.")

    @patch("srcExtractor.services.mongodb.query.mongodb.get_collection")
    @patch("srcExtractor.services.mongodb.query.mongodb.is_pdf_id_valid", return_value=True)
    @patch("srcExtractor.services.mongodb.query.mongodb.is_user_id_valid", return_value=True)
    @patch("srcExtractor.services.mongodb.query.mongodb.is_valid_object_id", return_value=True)
    def test_add_query_success(self, mock_obj, mock_user, mock_pdf, mock_get_collection):
        """Should upload query successfully"""
        mock_query_collection = MagicMock()
        mock_query_collection.insert_one.return_value.inserted_id = "query123"
        mock_get_collection.side_effect = [
            mock_query_collection, MagicMock(), MagicMock()
        ]  # Queries, Users, PDFs

        result = query.add_query({
            "user_id": self.valid_user_id,
            "pdf_id": self.valid_pdf_id,
            "response": self.valid_response
        })

        self.assertIn("message", result)
        self.assertEqual(result["message"], "Query metadata uploaded successfully.")
        self.assertEqual(result["query_id"], "query123")

    @patch("srcExtractor.services.mongodb.query.mongodb.get_collection")
    @patch("srcExtractor.services.mongodb.query.mongodb.is_pdf_id_valid", return_value=True)
    @patch("srcExtractor.services.mongodb.query.mongodb.is_user_id_valid", return_value=True)
    @patch("srcExtractor.services.mongodb.query.mongodb.is_valid_object_id", return_value=True)
    def test_add_query_db_failure(self, mock_obj, mock_user, mock_pdf, mock_get_collection):
        """Should handle DB write errors gracefully"""
        mock_query_collection = MagicMock()
        mock_query_collection.insert_one.side_effect = Exception("DB error")
        mock_get_collection.side_effect = [
            mock_query_collection, MagicMock(), MagicMock()
        ]

        result = query.add_query({
            "user_id": self.valid_user_id,
            "pdf_id": self.valid_pdf_id,
            "response": self.valid_response
        })

        self.assertIn("error", result)
        self.assertIn("Failed to upload query metadata: DB error", result["error"])
