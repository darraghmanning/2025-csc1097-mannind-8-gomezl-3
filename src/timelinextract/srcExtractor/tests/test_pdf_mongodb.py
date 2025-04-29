import gzip
from django.test import TestCase
from unittest.mock import patch, MagicMock, mock_open
from bson.objectid import ObjectId
from srcExtractor.services.mongodb import pdf


class PDFMongoDBTests(TestCase):

    def test_get_unique_file_name_unique(self):
        """Returns the original name if no duplicate exists."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None
        result = pdf.get_unique_file_name("document.pdf", mock_collection)
        self.assertEqual(result, "document.pdf")

    def test_get_unique_file_name_duplicate(self):
        """Appends counter if duplicate exists."""
        mock_collection = MagicMock()
        mock_collection.find_one.side_effect = [True, None]  # First exists, second is unique
        result = pdf.get_unique_file_name("document.pdf", mock_collection)
        self.assertEqual(result, "document_1.pdf")

    @patch("srcExtractor.services.mongodb.pdf.mongodb.get_collection")
    @patch("srcExtractor.services.mongodb.pdf.mongodb.is_valid_object_id", return_value=False)
    def test_add_pdf_invalid_user_id_format(self, mock_valid_obj, mock_get_collection):
        """Should return error if ObjectId format is invalid"""
        result = pdf.add_pdf({
            "user_id": "invalid-id",
            "file_name": "file.pdf",
            "temp_file_path": "fake/path"
        })
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Invalid user_id format.")

    @patch("srcExtractor.services.mongodb.pdf.mongodb.get_collection")
    @patch("srcExtractor.services.mongodb.pdf.mongodb.is_valid_object_id", return_value=True)
    @patch("srcExtractor.services.mongodb.pdf.mongodb.is_user_id_valid", return_value=False)
    def test_add_pdf_user_id_not_found(self, mock_user_valid, mock_obj_valid, mock_get_collection):
        """Should return error if user ID doesn't exist in DB"""
        result = pdf.add_pdf({
            "user_id": str(ObjectId()),
            "file_name": "file.pdf",
            "temp_file_path": "fake/path"
        })
        self.assertIn("error", result)
        self.assertEqual(result["error"], "User ID does not exist in the Users collection.")

    @patch("srcExtractor.services.mongodb.pdf.mongodb.get_collection")
    def test_add_pdf_missing_fields(self, mock_get_collection):
        """Should return error if any required field is missing"""
        result = pdf.add_pdf({
            "user_id": str(ObjectId()),
            "file_name": ""
        })
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Missing required fields: user_id, file_name, or file_object.")

    @patch("srcExtractor.services.mongodb.pdf.os.path.exists", return_value=False)
    def test_compress_file_not_found(self, mock_exists):
        result = pdf.compress_file("nonexistent.pdf")
        self.assertIn("error", result)
        self.assertTrue("File not found" in result["error"])

    @patch("srcExtractor.services.mongodb.pdf.os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data=b"test data")
    def test_compress_file_success(self, mock_file, mock_exists):
        result = pdf.compress_file("dummy.pdf")
        self.assertIn("success", result)
        # Check that the compressed data is valid gzip
        self.assertTrue(gzip.decompress(result["success"]), b"test data")

    @patch("srcExtractor.services.mongodb.pdf.os.path.exists", return_value=True)
    @patch("builtins.open", side_effect=Exception("Read error"))
    def test_compress_file_exception(self, mock_file, mock_exists):
        result = pdf.compress_file("corrupt.pdf")
        self.assertIn("error", result)
        self.assertIn("Failed to compress file", result["error"])

    @patch("srcExtractor.services.mongodb.pdf.compress_file", return_value={"success": b"compressed_data"})
    @patch("srcExtractor.services.mongodb.pdf.get_unique_file_name", return_value="unique_file.pdf")
    @patch("srcExtractor.services.mongodb.pdf.mongodb.get_collection")
    @patch("srcExtractor.services.mongodb.pdf.mongodb.is_valid_object_id", return_value=True)
    @patch("srcExtractor.services.mongodb.pdf.mongodb.is_user_id_valid", return_value=True)
    def test_add_pdf_success(self, mock_user_valid, mock_obj_id, mock_get_collection, mock_unique_name, mock_compress):
        """Should successfully upload PDF metadata"""
        mock_pdf_collection = MagicMock()
        mock_pdf_collection.insert_one.return_value.inserted_id = "pdf123"
        mock_get_collection.side_effect = [mock_pdf_collection, MagicMock()]  # PDF, Users

        result = pdf.add_pdf({
            "user_id": str(ObjectId()),
            "file_name": "report.pdf",
            "temp_file_path": "/some/path"
        })

        self.assertIn("message", result)
        self.assertIn("pdf_id", result)
        self.assertEqual(result["message"], "PDF 'unique_file.pdf' uploaded successfully.")
        self.assertEqual(result["pdf_id"], "pdf123")

    @patch("srcExtractor.services.mongodb.pdf.compress_file", return_value={"error": "Compression failed"})
    @patch("srcExtractor.services.mongodb.pdf.get_unique_file_name", return_value="file.pdf")
    @patch("srcExtractor.services.mongodb.pdf.mongodb.get_collection")
    @patch("srcExtractor.services.mongodb.pdf.mongodb.is_valid_object_id", return_value=True)
    @patch("srcExtractor.services.mongodb.pdf.mongodb.is_user_id_valid", return_value=True)
    def test_add_pdf_compression_failure(self, *_):
        """Should return compression error during add_pdf"""
        result = pdf.add_pdf({
            "user_id": str(ObjectId()),
            "file_name": "doc.pdf",
            "temp_file_path": "fake/path"
        })

        self.assertIn("error", result)
        self.assertEqual(result["error"], "Compression failed")

    @patch("srcExtractor.services.mongodb.pdf.compress_file", return_value={"success": b"compressed_data"})
    @patch("srcExtractor.services.mongodb.pdf.get_unique_file_name", return_value="file.pdf")
    @patch("srcExtractor.services.mongodb.pdf.mongodb.get_collection")
    @patch("srcExtractor.services.mongodb.pdf.mongodb.is_valid_object_id", return_value=True)
    @patch("srcExtractor.services.mongodb.pdf.mongodb.is_user_id_valid", return_value=True)
    def test_add_pdf_db_exception(self, mock_user_valid, mock_obj_id, mock_get_collection, mock_unique_name, mock_compress):
        """Should handle DB write exceptions"""
        mock_pdf_collection = MagicMock()
        mock_pdf_collection.insert_one.side_effect = Exception("DB failure")
        mock_get_collection.side_effect = [mock_pdf_collection, MagicMock()]  # PDFs, Users

        result = pdf.add_pdf({
            "user_id": str(ObjectId()),
            "file_name": "doc.pdf",
            "temp_file_path": "fake/path"
        })

        self.assertIn("error", result)
        self.assertIn("Failed to upload PDF metadata: DB failure", result["error"])
