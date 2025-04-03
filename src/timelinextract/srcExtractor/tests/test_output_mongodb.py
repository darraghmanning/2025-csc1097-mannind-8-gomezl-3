import json
from django.test import TestCase
from unittest.mock import patch, MagicMock
from bson.objectid import ObjectId
from srcExtractor.services.mongodb import output


class OutputMongoDBTests(TestCase):

    def setUp(self):
        self.valid_user_id = str(ObjectId())
        self.valid_pdf_id = str(ObjectId())
        self.valid_query_id = str(ObjectId())
        self.valid_table_id = str(ObjectId())
        self.valid_output = json.dumps({"result": "some generated content"})
        self.response_time = "123ms"

    @patch("srcExtractor.services.mongodb.output.mongodb.get_collection")
    def test_add_output_missing_fields(self, mock_get_collection):
        """Should return error if required fields are missing"""
        result = output.add_output({})
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Missing required fields: user_id, pdf_id, query_id, table_id, or output.")

    @patch("srcExtractor.services.mongodb.output.mongodb.get_collection")
    @patch("srcExtractor.services.mongodb.output.mongodb.is_valid_object_id", return_value=False)
    def test_add_output_invalid_user_id_format(self, _, mock_get_collection):
        """Should return error if user_id format is invalid"""
        result = output.add_output({
            "user_id": "invalid",
            "pdf_id": self.valid_pdf_id,
            "query_id": self.valid_query_id,
            "table_id": self.valid_table_id,
            "output": self.valid_output,
            "response_time": self.response_time
        })
        self.assertEqual(result["error"], "Invalid user_id format.")

    @patch("srcExtractor.services.mongodb.output.mongodb.get_collection")
    @patch("srcExtractor.services.mongodb.output.mongodb.is_valid_object_id", side_effect=[True, True])
    @patch("srcExtractor.services.mongodb.output.mongodb.is_user_id_valid", return_value=False)
    def test_add_output_user_not_found(self, _, __, mock_get_collection):
        """Should return error if user_id does not exist in Users collection"""
        result = output.add_output({
            "user_id": self.valid_user_id,
            "pdf_id": self.valid_pdf_id,
            "query_id": self.valid_query_id,
            "table_id": self.valid_table_id,
            "output": self.valid_output,
            "response_time": self.response_time
        })
        self.assertEqual(result["error"], "user_id does not exist in the Users collection.")

    @patch("srcExtractor.services.mongodb.output.mongodb.get_collection")
    @patch("srcExtractor.services.mongodb.output.mongodb.is_valid_object_id", side_effect=[True, True, False])
    @patch("srcExtractor.services.mongodb.output.mongodb.is_user_id_valid", return_value=True)
    def test_add_output_invalid_query_id_format(self, _, __, mock_get_collection):
        """Should return error if query_id format is invalid"""
        result = output.add_output({
            "user_id": self.valid_user_id,
            "pdf_id": self.valid_pdf_id,
            "query_id": "badqueryid",
            "table_id": self.valid_table_id,
            "output": self.valid_output,
            "response_time": self.response_time
        })
        self.assertEqual(result["error"], "Invalid query_id format.")

    @patch("srcExtractor.services.mongodb.output.mongodb.get_collection")
    @patch("srcExtractor.services.mongodb.output.mongodb.is_valid_object_id", side_effect=[True] * 4)
    @patch("srcExtractor.services.mongodb.output.mongodb.is_user_id_valid", return_value=True)
    @patch("srcExtractor.services.mongodb.output.mongodb.is_pdf_id_valid", return_value=True)
    @patch("srcExtractor.services.mongodb.output.mongodb.is_query_id_valid", return_value=False)
    def test_add_output_query_id_not_found(self, *_):
        result = output.add_output({
            "user_id": self.valid_user_id,
            "pdf_id": self.valid_pdf_id,
            "query_id": self.valid_query_id,
            "table_id": self.valid_table_id,
            "output": self.valid_output,
            "response_time": self.response_time
        })
        self.assertEqual(result["error"], "query_id does not exist in the Queries collection.")

    @patch("srcExtractor.services.mongodb.output.mongodb.get_collection")
    def test_add_output_invalid_output(self, mock_get_collection):
        """Should return error if output is not a valid JSON object"""
        result = output.add_output({
            "user_id": self.valid_user_id,
            "pdf_id": self.valid_pdf_id,
            "query_id": self.valid_query_id,
            "table_id": self.valid_table_id,
            "output": {},
            "response_time": self.response_time
        })
        self.assertEqual(result["error"], "Output must be a non-empty string.")

    @patch("srcExtractor.services.mongodb.output.mongodb.get_collection")
    def test_add_output_invalid_response_time(self, mock_get_collection):
        """Should return error if response_time is not a string"""
        result = output.add_output({
            "user_id": self.valid_user_id,
            "pdf_id": self.valid_pdf_id,
            "query_id": self.valid_query_id,
            "table_id": self.valid_table_id,
            "output": self.valid_output,
            "response_time": ""
        })
        self.assertEqual(result["error"], "response_time must be a non-empty string.")

    @patch("srcExtractor.services.mongodb.output.mongodb.get_collection")
    @patch("srcExtractor.services.mongodb.output.mongodb.is_table_id_valid", return_value=True)
    @patch("srcExtractor.services.mongodb.output.mongodb.is_query_id_valid", return_value=True)
    @patch("srcExtractor.services.mongodb.output.mongodb.is_pdf_id_valid", return_value=True)
    @patch("srcExtractor.services.mongodb.output.mongodb.is_user_id_valid", return_value=True)
    @patch("srcExtractor.services.mongodb.output.mongodb.is_valid_object_id", return_value=True)
    def test_add_output_success(self, mock_obj, mock_user, mock_pdf, mock_query, mock_table, mock_get_collection):
        """Should successfully insert output"""
        mock_output_collection = MagicMock()
        mock_output_collection.insert_one.return_value = None
        mock_get_collection.side_effect = [
            mock_output_collection, MagicMock(), MagicMock(), MagicMock(), MagicMock()
        ]

        result = output.add_output({
            "user_id": self.valid_user_id,
            "pdf_id": self.valid_pdf_id,
            "query_id": self.valid_query_id,
            "table_id": self.valid_table_id,
            "output": self.valid_output,
            "response_time": self.response_time
        })

        self.assertEqual(result, {"message": "Output metadata uploaded successfully."})

    @patch("srcExtractor.services.mongodb.output.mongodb.get_collection")
    @patch("srcExtractor.services.mongodb.output.mongodb.is_table_id_valid", return_value=True)
    @patch("srcExtractor.services.mongodb.output.mongodb.is_query_id_valid", return_value=True)
    @patch("srcExtractor.services.mongodb.output.mongodb.is_pdf_id_valid", return_value=True)
    @patch("srcExtractor.services.mongodb.output.mongodb.is_user_id_valid", return_value=True)
    @patch("srcExtractor.services.mongodb.output.mongodb.is_valid_object_id", return_value=True)
    def test_add_output_db_failure(self, mock_obj, mock_user, mock_pdf, mock_query, mock_table, mock_get_collection):
        """Should handle DB exceptions"""
        mock_output_collection = MagicMock()
        mock_output_collection.insert_one.side_effect = Exception("DB is down")
        mock_get_collection.side_effect = [
            mock_output_collection, MagicMock(), MagicMock(), MagicMock(), MagicMock()
        ]

        result = output.add_output({
            "user_id": self.valid_user_id,
            "pdf_id": self.valid_pdf_id,
            "query_id": self.valid_query_id,
            "table_id": self.valid_table_id,
            "output": self.valid_output,
            "response_time": self.response_time
        })

        self.assertIn("error", result)
        self.assertIn("Failed to upload output metadata: DB is down", result["error"])
