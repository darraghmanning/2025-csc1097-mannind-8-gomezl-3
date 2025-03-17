import json
from django.test import TestCase
from unittest.mock import patch
from srcExtractor.utils.match_questionnaires import find_matching_questionnaires, match_questionnaires_with_timelines

class MatchQuestionnairesTests(TestCase):

    @patch("builtins.open", read_data=json.dumps({
        "questionnaires": [
            {"longName": "Test Questionnaire", "shortName": "TQ", "questionnaireTiming": []}
        ]
    }))
    @patch("os.listdir", return_value=["timeline1.json"])
    @patch("json.load")
    @patch("srcExtractor.utils.data_processing.similar", return_value=0.8)
    def test_find_matching_questionnaires_success(self, mock_similar, mock_json_load, mock_listfir, mock_open):
        """Test successful questionnaire matching."""

        # Mocking JSON load return values
        mock_json_load.side_effect = [
            {"questionnaires": [{"longName": "Test Questionnaire", "shortName": "TQ", "questionnaireTiming": ["Week 1"]}]},
            [{"studyProcedure": "test questionnaire"}]
        ]

        result = find_matching_questionnaires("questionnaire.json", "timeline_folder", 0.6)
        self.assertIn("success", result)
        self.assertEqual(result["success"]["questionnaires"][0]["questionnaireTiming"], ["Week 1"])

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_find_matching_questionnaires_file_not_found(self, mock_open):
        """Test when the questionnaire JSON file is missing."""
        result = find_matching_questionnaires("missing.json", "timeline_folder", 0.6)
        self.assertIn("error", result)
        self.assertTrue("Failed to find matching questionnaires" in result["error"])

    @patch("os.listdir", side_effect=FileNotFoundError)
    def test_find_matching_questionnaires_missing_timeline_folder(self, mock_listdir):
        """Test when the timeline folder does not exist."""
        result = find_matching_questionnaires("questionnaire.json", "missing_folder", 0.6)
        self.assertIn("error", result)
        self.assertTrue("Failed to find matching questionnaires" in result["error"])

    @patch("builtins.open", read_data="invalid json")
    def test_find_matching_questionnaires_invalid_json(self, mock_open):
        """Test for invalid JSON data handling."""
        result = find_matching_questionnaires("invalid.json", "timeline_folder", 0.6)
        self.assertIn("error", result)
        self.assertTrue("Failed to find matching questionnaires" in result["error"])

    @patch("srcExtractor.utils.match_questionnaires.find_matching_questionnaires", side_effect=Exception("Unexpected error"))
    def test_match_questionnaires_with_timelines_exception_handling(self, mock_find_matching_questionnaires):
        """Test exception handling in match_questionnaires_with_timelines."""
        result = match_questionnaires_with_timelines("test_pdf")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Failed to match questionnaires")
