"""
Unit tests for main.py FastAPI application.
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from tcg_analytics.api.main import app

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


class TestMainAPI:
    """Test cases for the main FastAPI application."""

    def setup_method(self):
        """Set up test client for each test method."""
        self.client = TestClient(app)

    def test_health_check_endpoint(self):
        """Test the health check endpoint returns correct response."""
        response = self.client.get("/api/v1/health_check")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy", "message": "API is running"}

    @patch("tcg_analytics.api.main.JustTCGClient")
    def test_get_card_success(self, mock_justtcg_client):
        """Test successful card retrieval."""
        # Setup
        mock_client_instance = Mock()
        mock_card_data = {
            "id": "123456",
            "name": "Test Card",
            "set": "Test Set",
            "price": 25.99,
        }
        mock_client_instance.get_card_info.return_value = mock_card_data
        mock_justtcg_client.return_value = mock_client_instance

        # Execute
        response = self.client.get("/api/v1/cards/123456")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == mock_card_data
        mock_justtcg_client.assert_called_once()
        mock_client_instance.get_card_info.assert_called_once_with("123456")

    @patch("tcg_analytics.api.main.JustTCGClient")
    def test_get_card_value_error(self, mock_justtcg_client):
        """Test card retrieval with ValueError (configuration error)."""
        # Setup
        mock_justtcg_client.side_effect = ValueError("API key is required")

        # Execute
        response = self.client.get("/api/v1/cards/123456")

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Configuration error: API key is required" in response.json()["detail"]

    @patch("tcg_analytics.api.main.JustTCGClient")
    def test_get_card_generic_exception(self, mock_justtcg_client):
        """Test card retrieval with generic exception."""
        # Setup
        mock_client_instance = Mock()
        mock_client_instance.get_card_info.side_effect = Exception("Network timeout")
        mock_justtcg_client.return_value = mock_client_instance

        # Execute
        response = self.client.get("/api/v1/cards/123456")

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert (
            "Failed to retrieve card information: Network timeout"
            in response.json()["detail"]
        )

    def test_get_card_with_special_characters(self):
        """Test card retrieval with special characters in card ID."""
        with patch("tcg_analytics.api.main.JustTCGClient") as mock_justtcg_client:
            mock_client_instance = Mock()
            mock_card_data = {"id": "abc-123_test", "name": "Special Card"}
            mock_client_instance.get_card_info.return_value = mock_card_data
            mock_justtcg_client.return_value = mock_client_instance

            response = self.client.get("/api/v1/cards/abc-123_test")

            assert response.status_code == status.HTTP_200_OK
            mock_client_instance.get_card_info.assert_called_once_with("abc-123_test")

    def test_app_metadata(self):
        """Test FastAPI app metadata configuration."""
        assert app.title == "TCG Analytics API"
        assert (
            app.description == "API for trading card game analytics and data retrieval"
        )
        assert app.version == "1.0.0"

    def test_invalid_endpoint_returns_404(self):
        """Test that invalid endpoints return 404."""
        response = self.client.get("/api/v1/invalid_endpoint")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_health_check_method_not_allowed(self):
        """Test that non-GET methods are not allowed on health check endpoint."""
        response = self.client.post("/api/v1/health_check")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_get_card_method_not_allowed(self):
        """Test that non-GET methods are not allowed on cards endpoint."""
        response = self.client.post("/api/v1/cards/123456")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


class TestIntegration:
    """Integration test cases."""

    def test_app_startup(self):
        """Test that the FastAPI app can be instantiated correctly."""
        test_client = TestClient(app)

        # Verify the app can handle basic requests
        response = test_client.get("/api/v1/health_check")
        assert response.status_code == status.HTTP_200_OK


@pytest.fixture
def mock_justtcg_client():
    """Fixture providing a mocked JustTCGClient."""
    with patch("tcg_analytics.api.main.JustTCGClient") as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        yield mock_instance
