from django.test import TestCase
from unittest.mock import patch
from srcExtractor.utils.pdf_validation import handle_pdf_upload


class PDFUploadTests(TestCase):

    @patch("os.path.getsize", return_value=1024)
    @patch("srcExtractor.utils.pdf_validation.extract_text_from_pdf", return_value={"text": "Sample text from PDF"})
    def test_handle_pdf_upload_success(self, mock_extract_text, mock_getsize):
        """Test successful PDF file upload and text extraction."""

        result = handle_pdf_upload("test.pdf")

        self.assertIn("success", result)
        self.assertEqual(result["success"], "test.pdf")

    def test_handle_pdf_upload_no_file(self):
        """Test when no PDF file is provided."""
        result = handle_pdf_upload("")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "No PDF file in data.")

    @patch("os.path.getsize", return_value=1024)
    def test_handle_pdf_upload_invalid_file_type(self, mock_getsize):
        """Test when a non-PDF file is uploaded."""
        result = handle_pdf_upload("test.txt")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Only PDF files are allowed.")

    @patch("os.path.getsize", return_value=0)
    def test_handle_pdf_upload_empty_pdf(self, mock_getsize):
        """Test when an empty PDF file is uploaded."""
        result = handle_pdf_upload("empty.pdf")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Uploaded PDF file is empty.")

    @patch("os.path.getsize", side_effect=Exception("File not found"))
    def test_handle_pdf_upload_file_not_found(self, mock_getsize):
        """Test when the provided PDF file does not exist."""
        result = handle_pdf_upload("non_existent.pdf")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Error validating the file: File not found")

    @patch("os.path.getsize", return_value=1024)
    @patch("srcExtractor.utils.pdf_validation.extract_text_from_pdf", return_value={"error": "PDF extraction failed"})
    def test_handle_pdf_upload_extraction_error(self, mock_extract_text, mock_getsize):
        """Test when text extraction from the PDF fails."""

        result = handle_pdf_upload("corrupt.pdf")

        self.assertIn("error", result)
        self.assertEqual(result["error"], "PDF extraction failed")

    @patch("os.path.getsize", return_value=1024)
    @patch("srcExtractor.utils.pdf_validation.extract_text_from_pdf", side_effect=Exception("Extraction process failed"))
    def test_handle_pdf_upload_unexpected_extraction_exception(self, mock_extract_text, mock_getsize):
        """Test when an unexpected exception occurs during text extraction."""

        result = handle_pdf_upload("test.pdf")

        self.assertIn("error", result)
        self.assertEqual(result["error"], "Error extracting text from the PDF: Extraction process failed")
