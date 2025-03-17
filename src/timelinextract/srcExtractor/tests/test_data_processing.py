from django.test import TestCase
from pathlib import Path
from unittest.mock import patch, mock_open
from srcExtractor.utils.data_processing import (
    clean_text, extract_json, save_merged_data_to_json,
    csv_to_json, merge_json_files, similar, extract_time_points
)

class DataProcessingTests(TestCase):

    def test_clean_text(self):
        text = "Hello\nWorld【1:source】"
        expected = "Hello<br>World"
        self.assertEqual(clean_text(text), expected)

    def test_extract_json(self):
        text = "Some text ```json {\"key\": \"value\"} \n``` more text"
        expected = '{"key": "value"}'
        self.assertEqual(extract_json(text), expected)

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    @patch("srcExtractor.utils.data_validation.is_json", return_value=True)
    def test_save_merged_data_to_json(self, mock_is_json, mock_makedirs, mock_file):
        merged_data = '{"key": "value"}'
        pdf_path = "sample.pdf"
        response = save_merged_data_to_json(merged_data, pdf_path)
        self.assertIn("success", response)

    @patch("builtins.open", new_callable=mock_open, read_data="col1,col2\nval1,val2")
    def test_csv_to_json(self, mock_file):
        response = csv_to_json("sample.csv", "output.json")
        self.assertIn("success", response)

    @patch("os.listdir", return_value=["file1.json", "file2.json"])
    @patch("builtins.open", new_callable=mock_open, read_data='[{"key": "value"}]')
    def test_merge_json_files(self, mock_file, mock_listdir):
        response = merge_json_files("folder1", "folder2", "output.json")
        self.assertIn("success", response)

    def test_similar(self):
        self.assertEqual(similar("hello", "hello world"), 1.0)
        self.assertAlmostEqual(similar("hello", "hola"), 0.5, delta=0.5)

    def test_extract_time_points(self):
        entry = {"day1": "X", "day2": "Y", "day3": "x"}
        self.assertEqual(extract_time_points(entry), ["day1", "day3"])
