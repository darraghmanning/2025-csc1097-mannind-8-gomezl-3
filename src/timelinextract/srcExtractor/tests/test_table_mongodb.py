import json
from django.test import TestCase
from unittest.mock import patch, MagicMock
from bson.objectid import ObjectId
from srcExtractor.services.mongodb import table


class TablesMongoDBTests(TestCase):

    def setUp(self):
        self.valid_user_id = str(ObjectId())
        self.valid_pdf_id = str(ObjectId())
        self.valid_classified_response = {"tables": ["Table 1", "Table 2"]}

    @patch("srcExtractor.services.mongodb.table.mongodb.get_collection")
    def test_add_tables_missing_fields(self, mock_get_collection):
        """Should return error if required fields are missing"""
        result = table.add_tables({})
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Missing required fields: user_id, pdf_id, or classified_response.")

    @patch("srcExtractor.services.mongodb.table.mongodb.get_collection")
    @patch("srcExtractor.services.mongodb.table.mongodb.is_valid_object_id", return_value=False)
    def test_add_tables_invalid_user_id_format(self, _, mock_get_collection):
        """Should return error if user_id format is invalid"""
        result = table.add_tables({
            "user_id": "invalid",
            "pdf_id": self.valid_pdf_id,
            "classified_response": self.valid_classified_response
        })
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Invalid user_id format.")

    @patch("srcExtractor.services.mongodb.table.mongodb.get_collection")
    @patch("srcExtractor.services.mongodb.table.mongodb.is_valid_object_id", side_effect=[True, True])
    @patch("srcExtractor.services.mongodb.table.mongodb.is_user_id_valid", return_value=False)
    def test_add_tables_user_id_not_found(self, mock_user_valid, mock_obj_id, mock_get_collection):
        """Should return error if user_id does not exist in Users collection"""
        result = table.add_tables({
            "user_id": self.valid_user_id,
            "pdf_id": self.valid_pdf_id,
            "classified_response": self.valid_classified_response
        })
        self.assertIn("error", result)
        self.assertEqual(result["error"], "user_id does not exist in the Users collection.")

    @patch("srcExtractor.services.mongodb.table.mongodb.get_collection")
    @patch("srcExtractor.services.mongodb.table.mongodb.is_valid_object_id", side_effect=[True, False])
    @patch("srcExtractor.services.mongodb.table.mongodb.is_user_id_valid", return_value=True)
    def test_add_tables_invalid_pdf_id_format(self, _, __, mock_get_collection):
        """Should return error if pdf_id format is invalid"""
        result = table.add_tables({
            "user_id": self.valid_user_id,
            "pdf_id": "invalid",
            "classified_response": self.valid_classified_response
        })
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Invalid pdf_id format.")

    @patch("srcExtractor.services.mongodb.table.mongodb.get_collection")
    @patch("srcExtractor.services.mongodb.table.mongodb.is_valid_object_id", side_effect=[True, True])
    @patch("srcExtractor.services.mongodb.table.mongodb.is_user_id_valid", return_value=True)
    @patch("srcExtractor.services.mongodb.table.mongodb.is_pdf_id_valid", return_value=False)
    def test_add_tables_pdf_id_not_found(self, *mocks):
        result = table.add_tables({
            "user_id": self.valid_user_id,
            "pdf_id": self.valid_pdf_id,
            "classified_response": self.valid_classified_response
        })
        self.assertIn("error", result)
        self.assertEqual(result["error"], "pdf_id does not exist in the PDFs collection.")

    @patch("srcExtractor.services.mongodb.table.mongodb.get_collection")
    def test_add_tables_empty_response(self, mock_get_collection):
        """Should fail if classified_response is empty"""
        result = table.add_tables({
            "user_id": self.valid_user_id,
            "pdf_id": self.valid_pdf_id,
            "classified_response": {}
        })
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Response must be a non-empty string.")

    @patch("srcExtractor.services.mongodb.table.mongodb.get_collection")
    @patch("srcExtractor.services.mongodb.table.mongodb.is_pdf_id_valid", return_value=True)
    @patch("srcExtractor.services.mongodb.table.mongodb.is_user_id_valid", return_value=True)
    @patch("srcExtractor.services.mongodb.table.mongodb.is_valid_object_id", return_value=True)
    def test_add_tables_success(self, mock_obj, mock_user, mock_pdf, mock_get_collection):
        """Should upload tables successfully"""
        mock_tables_collection = MagicMock()
        mock_tables_collection.insert_one.return_value.inserted_id = "table123"
        mock_get_collection.side_effect = [
            mock_tables_collection, MagicMock(), MagicMock()
        ]  # Tables, Users, PDFs

        result = table.add_tables({
            "user_id": self.valid_user_id,
            "pdf_id": self.valid_pdf_id,
            "classified_response": self.valid_classified_response
        })

        self.assertIn("message", result)
        self.assertEqual(result["message"], "Tables metadata uploaded successfully.")
        self.assertEqual(result["table_id"], "table123")

    @patch("srcExtractor.services.mongodb.table.mongodb.get_collection")
    @patch("srcExtractor.services.mongodb.table.mongodb.is_pdf_id_valid", return_value=True)
    @patch("srcExtractor.services.mongodb.table.mongodb.is_user_id_valid", return_value=True)
    @patch("srcExtractor.services.mongodb.table.mongodb.is_valid_object_id", return_value=True)
    def test_add_tables_db_failure(self, mock_obj, mock_user, mock_pdf, mock_get_collection):
        """Should handle DB write errors gracefully"""
        mock_tables_collection = MagicMock()
        mock_tables_collection.insert_one.side_effect = Exception("DB failure")
        mock_get_collection.side_effect = [
            mock_tables_collection, MagicMock(), MagicMock()
        ]

        result = table.add_tables({
            "user_id": self.valid_user_id,
            "pdf_id": self.valid_pdf_id,
            "classified_response": self.valid_classified_response
        })

        self.assertIn("error", result)
        self.assertIn("Failed to upload tables metadata: DB failure", result["error"])
