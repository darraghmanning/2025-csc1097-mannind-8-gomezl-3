from django.test import TestCase
from unittest.mock import patch, mock_open, MagicMock
from srcExtractor.utils.data_validation import extract_text_from_pdf, load_common_words, is_verbal_text, is_json

class DataValidationTests(TestCase):

    @patch("srcExtractor.utils.data_validation.is_verbal_text")
    @patch("srcExtractor.utils.data_validation.PdfReader")
    def test_extract_text_from_pdf(self, mock_pdf_reader, mock_is_verbal_text):
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Clinical trial Sample extracted téxt"
        mock_pdf_reader.return_value.pages = [mock_page]
        mock_is_verbal_text.return_value = True
        response = extract_text_from_pdf("sample.pdf")
        self.assertIn("success", response)

    @patch("builtins.open", new_callable=mock_open, read_data="the\nand\nis\na\n")
    def test_load_common_words(self, mock_file):
        words = load_common_words("common_words.txt")
        self.assertIn("the", words)
        self.assertIn("and", words)

    @patch("srcExtractor.utils.data_validation.load_common_words", return_value={"the", "is", "a"})
    def test_is_verbal_text(self, mock_load_words):
        self.assertTrue(is_verbal_text("The cat is on a mat."))
        self.assertFalse(is_verbal_text("XJKLDSJFLJSDFLKJ"))

    def test_is_json(self):
        valid_json = '{"key": "value"}'
        invalid_json = "{key: value}"
        self.assertTrue(is_json(valid_json))
        self.assertFalse(is_json(invalid_json))
