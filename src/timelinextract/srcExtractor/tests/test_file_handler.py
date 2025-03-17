from django.test import TestCase
from unittest.mock import patch, MagicMock
from srcExtractor.utils.file_handler import save_temp_pdf, remove_temp_file

class FileHandlerTests(TestCase):

    @patch("srcExtractor.utils.file_handler.default_storage.save")
    @patch("srcExtractor.utils.file_handler.ContentFile")
    def test_save_temp_pdf(self, mock_content_file, mock_save):
        mock_file = MagicMock()
        mock_file.name = "test.pdf"
        mock_file.read.return_value = b"PDF content"
        
        mock_save.return_value = "temp/test.pdf"
        
        result = save_temp_pdf(mock_file)
        self.assertEqual(result, "temp/test.pdf")
        mock_save.assert_called_once()

    @patch("os.path.exists", return_value=True)
    @patch("os.remove")
    @patch("srcExtractor.utils.file_handler.logging.info")
    def test_remove_temp_file(self, mock_logging, mock_remove, mock_exists):
        file_path = "temp/test.pdf"
        remove_temp_file(file_path)
        mock_exists.assert_called_once_with(file_path)
        mock_remove.assert_called_once_with(file_path)
        mock_logging.assert_called_once()
