"""
Unit tests for JustTCG API client module.
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest
import requests

from tcg_analytics.util.justtcg import JustTCGClient

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


class TestJustTCGClient:
    """Test cases for JustTCGClient class."""

    def test_init_with_api_key(self):
        """Test initialization with provided API key."""
        api_key = "test_api_key_123"
        client = JustTCGClient(api_key=api_key)

        assert client.api_key == api_key
        assert isinstance(client.session, requests.Session)
        assert client.session.headers["x-api-key"] == api_key
        assert client.session.headers["Content-Type"] == "application/json"

    @patch.dict(os.environ, {"JUSTTCG_API_KEY": "env_api_key_456"})
    def test_init_with_env_api_key(self):
        """Test initialization with API key from environment variable."""
        client = JustTCGClient()

        assert client.api_key == "env_api_key_456"
        assert client.session.headers["x-api-key"] == "env_api_key_456"

    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_api_key_raises_error(self):
        """Test that initialization without API key raises ValueError."""
        with pytest.raises(ValueError, match="API key is required"):
            JustTCGClient()

    def test_auth_sets_headers(self):
        """Test that authentication sets proper headers."""
        api_key = "test_key"
        client = JustTCGClient(api_key=api_key)

        expected_headers = {"x-api-key": api_key, "Content-Type": "application/json"}

        for key, value in expected_headers.items():
            assert client.session.headers[key] == value

    @patch("requests.Session.get")
    def test_get_success(self, mock_get):
        """Test successful GET request."""
        # Setup
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success", "data": "test"}
        mock_get.return_value = mock_response

        client = JustTCGClient(api_key="test_key")

        # Execute
        result = client._get("test-endpoint", params={"param": "value"})

        # Assert
        assert result == {"status": "success", "data": "test"}
        mock_get.assert_called_once_with(
            f"{client.BASE_URL}/test-endpoint", params={"param": "value"}
        )
        mock_response.raise_for_status.assert_called_once()

    @patch("requests.Session.get")
    def test_get_with_leading_slash(self, mock_get):
        """Test GET request with leading slash in endpoint."""
        mock_response = Mock()
        mock_response.json.return_value = {"data": "test"}
        mock_get.return_value = mock_response

        client = JustTCGClient(api_key="test_key")
        client._get("/test-endpoint")

        mock_get.assert_called_once_with(
            f"{client.BASE_URL}/test-endpoint", params=None
        )

    @patch("requests.Session.get")
    def test_get_request_exception(self, mock_get):
        """Test GET request raising RequestException."""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        client = JustTCGClient(api_key="test_key")

        with pytest.raises(Exception, match="GET request failed: Network error"):
            client._get("test-endpoint")

    @patch("requests.Session.get")
    def test_get_http_error(self, mock_get):
        """Test GET request with HTTP error status."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "404 Not Found"
        )
        mock_get.return_value = mock_response

        client = JustTCGClient(api_key="test_key")

        with pytest.raises(Exception, match="GET request failed: 404 Not Found"):
            client._get("test-endpoint")

    @patch("requests.Session.post")
    def test_post_success(self, mock_post):
        """Test successful POST request."""
        # Setup
        mock_response = Mock()
        mock_response.json.return_value = {"status": "created", "id": 123}
        mock_post.return_value = mock_response

        client = JustTCGClient(api_key="test_key")
        test_data = {"name": "test", "value": 42}

        # Execute
        result = client._post("create-endpoint", data=test_data)

        # Assert
        assert result == {"status": "created", "id": 123}
        mock_post.assert_called_once_with(
            f"{client.BASE_URL}/create-endpoint", json=test_data
        )
        mock_response.raise_for_status.assert_called_once()

    @patch("requests.Session.post")
    def test_post_with_leading_slash(self, mock_post):
        """Test POST request with leading slash in endpoint."""
        mock_response = Mock()
        mock_response.json.return_value = {"data": "test"}
        mock_post.return_value = mock_response

        client = JustTCGClient(api_key="test_key")
        client._post("/create-endpoint", data={"test": "data"})

        mock_post.assert_called_once_with(
            f"{client.BASE_URL}/create-endpoint", json={"test": "data"}
        )

    @patch("requests.Session.post")
    def test_post_request_exception(self, mock_post):
        """Test POST request raising RequestException."""
        mock_post.side_effect = requests.exceptions.RequestException("Connection error")

        client = JustTCGClient(api_key="test_key")

        with pytest.raises(Exception, match="POST request failed: Connection error"):
            client._post("create-endpoint", data={"test": "data"})

    @patch("requests.Session.post")
    def test_post_http_error(self, mock_post):
        """Test POST request with HTTP error status."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "400 Bad Request"
        )
        mock_post.return_value = mock_response

        client = JustTCGClient(api_key="test_key")

        with pytest.raises(Exception, match="POST request failed: 400 Bad Request"):
            client._post("create-endpoint", data={"test": "data"})

    @patch.object(JustTCGClient, "_get")
    def test_get_card_info(self, mock_get):
        """Test get_card_info method."""
        # Setup
        expected_response = {
            "id": "12345",
            "name": "Test Card",
            "set": "Test Set",
            "price": 19.99,
        }
        mock_get.return_value = expected_response

        client = JustTCGClient(api_key="test_key")
        card_id = "12345"

        # Execute
        result = client.get_card_info(card_id)

        # Assert
        assert result == expected_response
        mock_get.assert_called_once_with("cards", params={"tcgplayerId": card_id})

    def test_base_url_constant(self):
        """Test that BASE_URL is set correctly."""
        assert JustTCGClient.BASE_URL == "https://api.justtcg.com/v1"

    @patch("requests.Session")
    def test_session_creation(self, mock_session_class):
        """Test that requests.Session is properly instantiated."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        client = JustTCGClient(api_key="test_key")

        assert client.session == mock_session
        mock_session_class.assert_called_once()


class TestIntegration:
    """Integration test cases."""

    def test_full_client_initialization_flow(self):
        """Test complete client initialization and header setup."""
        api_key = "integration_test_key"
        client = JustTCGClient(api_key=api_key)

        # Verify all components are properly initialized
        assert client.api_key == api_key
        assert isinstance(client.session, requests.Session)
        assert client.session.headers["x-api-key"] == api_key
        assert client.session.headers["Content-Type"] == "application/json"
        assert client.BASE_URL == "https://api.justtcg.com/v1"


@pytest.fixture
def mock_client():
    """Fixture providing a JustTCGClient instance with mocked requests."""
    with patch("requests.Session"):
        return JustTCGClient(api_key="test_fixture_key")


def test_fixture_usage(mock_client):
    """Test that the fixture works correctly."""
    assert mock_client.api_key == "test_fixture_key"
    assert mock_client.BASE_URL == "https://api.justtcg.com/v1"
