"""
Unit tests for the JustTCG API interaction module.
"""

import unittest
from unittest.mock import Mock, patch
import requests
import os
from justtcg import JustTCGClient


class TestJustTCGClient(unittest.TestCase):
    """Test cases for the JustTCGClient class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.api_key = "test_api_key"
        self.mock_response_data = {
            "data": [
                {
                    "id": "123456",
                    "name": "Test Card",
                    "game": "mtg",
                    "price": 10.99
                }
            ],
            "meta": {"total": 1}
        }
    
    @patch.dict(os.environ, {"JUSTTCG_API_KEY": "env_api_key"})
    def test_init_with_env_api_key(self):
        """Test client initialization with API key from environment variable."""
        with patch.object(JustTCGClient, '_auth'):
            client = JustTCGClient()
            self.assertEqual(client.api_key, "env_api_key")
    
    def test_init_with_passed_api_key(self):
        """Test client initialization with API key passed as parameter."""
        with patch.object(JustTCGClient, '_auth'):
            client = JustTCGClient(api_key=self.api_key)
            self.assertEqual(client.api_key, self.api_key)
    
    def test_auth_with_valid_api_key(self):
        """Test authentication with valid API key."""
        with patch.object(JustTCGClient, '_auth'):
            client = JustTCGClient(api_key=self.api_key)
            client._auth()
            
            self.assertEqual(client.session.headers["x-api-key"], self.api_key)
            self.assertEqual(client.session.headers["Content-Type"], "application/json")
    
    def test_auth_without_api_key(self):
        """Test authentication raises error when no API key is provided."""
        with patch.object(JustTCGClient, '_auth'):
            client = JustTCGClient.__new__(JustTCGClient)
            client.api_key = None
            client.session = requests.Session()
            
            with self.assertRaises(ValueError) as context:
                client._auth()
            
            self.assertIn("API key is required", str(context.exception))
    
    @patch('requests.Session.get')
    def test_get_success(self, mock_get):
        """Test successful GET request."""
        mock_response = Mock()
        mock_response.json.return_value = self.mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with patch.object(JustTCGClient, '_auth'):
            client = JustTCGClient(api_key=self.api_key)
            result = client._get("cards", params={"tcgplayerId": "123456"})
            
            self.assertEqual(result, self.mock_response_data)
            mock_get.assert_called_once_with(
                "https://api.justtcg.com/v1/cards",
                params={"tcgplayerId": "123456"}
            )
    
    @patch('requests.Session.get')
    def test_get_request_exception(self, mock_get):
        """Test GET request with exception."""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        with patch.object(JustTCGClient, '_auth'):
            client = JustTCGClient(api_key=self.api_key)
            
            with self.assertRaises(Exception) as context:
                client._get("cards")
            
            self.assertIn("GET request failed", str(context.exception))
    
    @patch('requests.Session.post')
    def test_post_success(self, mock_post):
        """Test successful POST request."""
        mock_response = Mock()
        mock_response.json.return_value = self.mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        test_data = {"tcgplayerIds": ["123456", "789012"]}
        
        with patch.object(JustTCGClient, '_auth'):
            client = JustTCGClient(api_key=self.api_key)
            result = client._post("cards", data=test_data)
            
            self.assertEqual(result, self.mock_response_data)
            mock_post.assert_called_once_with(
                "https://api.justtcg.com/v1/cards",
                json=test_data
            )
    
    @patch('requests.Session.post')
    def test_post_request_exception(self, mock_post):
        """Test POST request with exception."""
        mock_post.side_effect = requests.exceptions.RequestException("Network error")
        
        with patch.object(JustTCGClient, '_auth'):
            client = JustTCGClient(api_key=self.api_key)
            
            with self.assertRaises(Exception) as context:
                client._post("cards", data={})
            
            self.assertIn("POST request failed", str(context.exception))
    
    @patch.object(JustTCGClient, '_get')
    def test_get_card_info_success(self, mock_get):
        """Test successful card info retrieval."""
        mock_get.return_value = self.mock_response_data
        
        with patch.object(JustTCGClient, '_auth'):
            client = JustTCGClient(api_key=self.api_key)
            result = client.get_card_info("123456")
            
            self.assertEqual(result, self.mock_response_data)
            mock_get.assert_called_once_with("cards", params={"tcgplayerId": "123456"})
    
    @patch('requests.Session.get')
    def test_get_with_endpoint_leading_slash(self, mock_get):
        """Test GET request with endpoint that has leading slash."""
        mock_response = Mock()
        mock_response.json.return_value = self.mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with patch.object(JustTCGClient, '_auth'):
            client = JustTCGClient(api_key=self.api_key)
            client._get("/cards")
            
            mock_get.assert_called_once_with(
                "https://api.justtcg.com/v1/cards",
                params=None
            )
    
    @patch('requests.Session.post')
    def test_post_with_endpoint_leading_slash(self, mock_post):
        """Test POST request with endpoint that has leading slash."""
        mock_response = Mock()
        mock_response.json.return_value = self.mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        with patch.object(JustTCGClient, '_auth'):
            client = JustTCGClient(api_key=self.api_key)
            client._post("/cards")
            
            mock_post.assert_called_once_with(
                "https://api.justtcg.com/v1/cards",
                json=None
            )
    
    @patch('requests.Session.get')
    def test_get_http_error(self, mock_get):
        """Test GET request with HTTP error response."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        with patch.object(JustTCGClient, '_auth'):
            client = JustTCGClient(api_key=self.api_key)
            
            with self.assertRaises(Exception) as context:
                client._get("cards")
            
            self.assertIn("GET request failed", str(context.exception))
    
    @patch('requests.Session.post')
    def test_post_http_error(self, mock_post):
        """Test POST request with HTTP error response."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("400 Bad Request")
        mock_post.return_value = mock_response
        
        with patch.object(JustTCGClient, '_auth'):
            client = JustTCGClient(api_key=self.api_key)
            
            with self.assertRaises(Exception) as context:
                client._post("cards")
            
            self.assertIn("POST request failed", str(context.exception))


if __name__ == '__main__':
    unittest.main()