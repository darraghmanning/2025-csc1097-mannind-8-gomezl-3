from django.test import TestCase
from unittest.mock import patch, MagicMock
from srcExtractor.services.mongodb import user


class UserMongoDBTests(TestCase):

    def test_is_valid_email(self):
        self.assertTrue(user.is_valid_email("user@example.com"))
        self.assertTrue(user.is_valid_email("user.name+tag@example.co.uk"))
        self.assertFalse(user.is_valid_email("not-an-email"))
        self.assertFalse(user.is_valid_email("missing@domain"))
        self.assertFalse(user.is_valid_email("user@.com"))

    def test_add_user_missing_email(self):
        """Should return error if email is missing"""
        result = user.add_user({})
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Missing required field: email.")

    def test_add_user_invalid_email(self):
        """Should return error if email format is invalid"""
        result = user.add_user({"email": "invalid-email"})
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Invalid email format.")

    @patch("srcExtractor.services.mongodb.user.mongodb.get_collection")
    def test_add_user_already_exists(self, mock_get_collection):
        """Should detect existing user and return message"""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {"_id": "abc123", "email": "user@example.com"}
        mock_get_collection.return_value = mock_collection

        result = user.add_user({"email": "user@example.com"})

        self.assertIn("message", result)
        self.assertEqual(result["message"], "User 'user@example.com' already exists.")
        self.assertEqual(result["user_id"], "abc123")

    @patch("srcExtractor.services.mongodb.user.mongodb.get_collection")
    def test_add_user_success(self, mock_get_collection):
        """Should create new user if not found"""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None
        mock_collection.insert_one.return_value.inserted_id = "newid456"
        mock_get_collection.return_value = mock_collection

        result = user.add_user({"email": "newuser@example.com"})

        self.assertIn("message", result)
        self.assertEqual(result["message"], "User 'newuser@example.com' created successfully.")
        self.assertEqual(result["user_id"], "newid456")

    @patch("srcExtractor.services.mongodb.user.mongodb.get_collection")
    def test_add_user_exception_handling(self, mock_get_collection):
        """Should handle exception during DB operations"""
        mock_collection = MagicMock()
        mock_collection.find_one.side_effect = Exception("DB error")
        mock_get_collection.return_value = mock_collection

        result = user.add_user({"email": "test@example.com"})

        self.assertIn("error", result)
        self.assertTrue(result["error"].startswith("Failed to add user: DB error"))
