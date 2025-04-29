from django.test import TestCase
from unittest.mock import patch, mock_open
from srcExtractor.utils.pdf_processing import extract_and_classify_tables


class PDFProcessingTests(TestCase):

    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake pdf content")
    @patch("srcExtractor.utils.pdf_processing.extract_tables", return_value={"success": True})
    @patch("srcExtractor.utils.pdf_processing.classify_all_tables_in_folder", return_value={"success": ["table1.csv", "table2.csv"]})
    @patch("srcExtractor.utils.data_processing.convert_valid_files_to_json")
    def test_extract_and_classify_tables_success(self, mock_convert_json, mock_classify, mock_extract, mock_file, mock_mkdir):
        """Test successful extraction and classification of tables from a PDF."""

        result = extract_and_classify_tables("sample.pdf", "sample")

        self.assertIn("valid_files", result)
        self.assertEqual(result["valid_files"], ["table1.csv", "table2.csv"])

    @patch("builtins.open", new_callable=mock_open, read_data=b"fake pdf content")
    @patch("srcExtractor.utils.pdf_processing.extract_tables", return_value={"error": "Extraction failed"})
    def test_extract_and_classify_tables_extraction_error(self, mock_extract, mock_file):
        """Test handling of errors during table extraction."""
        result = extract_and_classify_tables("sample.pdf", "sample")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Extraction failed")

    @patch("builtins.open", new_callable=mock_open, read_data=b"fake pdf content")
    @patch("srcExtractor.utils.pdf_processing.extract_tables", return_value={"success": True})
    @patch(
        "srcExtractor.utils.pdf_processing.classify_all_tables_in_folder",
        return_value={"error": "No Schedule of Events table found in the protocol."}
    )
    def test_extract_and_classify_tables_no_valid_files(self, mock_classify, mock_extract, mock_file):
        """Test when no valid tables are found after classification."""
        result = extract_and_classify_tables("sample.pdf", "sample")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "No Schedule of Events table found in the protocol.")

    @patch("builtins.open", new_callable=mock_open, read_data=b"fake pdf content")
    @patch("srcExtractor.utils.pdf_processing.extract_tables", return_value={"success": True})
    @patch("srcExtractor.utils.pdf_processing.classify_all_tables_in_folder", side_effect=Exception("Unexpected error"))
    def test_extract_and_classify_tables_exception(self, mock_classify, mock_extract, mock_file):
        """Test exception handling in extract_and_classify_tables."""
        result = extract_and_classify_tables("sample.pdf", "sample")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Failed to extract or classify tables")
