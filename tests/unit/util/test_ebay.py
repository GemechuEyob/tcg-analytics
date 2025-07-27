"""
Unit tests for eBay API client module.
"""

import base64
import os
import sys
from unittest.mock import Mock, patch

import pytest
import requests

from tcg_analytics.util.ebay import EbayClient

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


class TestEbayClient:
    """Test cases for EbayClient class."""

    def test_init_with_access_token(self):
        """Test initialization with provided access token."""
        access_token = "test_access_token_123"
        marketplace_id = "EBAY_US"
        client = EbayClient(access_token=access_token, marketplace_id=marketplace_id)

        assert client.access_token == access_token
        assert client.marketplace_id == marketplace_id
        assert isinstance(client.session, requests.Session)
        assert client.session.headers["Authorization"] == f"Bearer {access_token}"
        assert client.session.headers["X-EBAY-C-MARKETPLACE-ID"] == marketplace_id
        assert client.session.headers["Content-Type"] == "application/json"

    def test_init_with_default_marketplace(self):
        """Test initialization with default marketplace."""
        access_token = "test_token"
        client = EbayClient(access_token=access_token)

        assert client.marketplace_id == "EBAY_US"
        assert client.session.headers["X-EBAY-C-MARKETPLACE-ID"] == "EBAY_US"

    def test_init_sets_headers_correctly(self):
        """Test that initialization sets proper headers."""
        access_token = "test_token"
        marketplace_id = "EBAY_GB"
        client = EbayClient(access_token=access_token, marketplace_id=marketplace_id)

        expected_headers = {
            "Authorization": f"Bearer {access_token}",
            "X-EBAY-C-MARKETPLACE-ID": marketplace_id,
            "Content-Type": "application/json",
        }

        for key, value in expected_headers.items():
            assert client.session.headers[key] == value

    def test_constants(self):
        """Test that class constants are set correctly."""
        assert EbayClient.BROWSE_BASE_URL == "https://api.ebay.com/buy/browse/v1"
        assert (
            EbayClient.CATALOG_BASE_URL
            == "https://api.ebay.com/commerce/catalog/v1_beta"
        )

    @patch("requests.Session.request")
    def test_make_request_success(self, mock_request):
        """Test successful _make_request."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        client = EbayClient(access_token="test_token")
        result = client._make_request("GET", "http://test.com")

        assert result == mock_response
        mock_request.assert_called_once_with("GET", "http://test.com")
        mock_response.raise_for_status.assert_called_once()

    @patch("requests.Session.request")
    def test_make_request_http_error(self, mock_request):
        """Test _make_request with HTTP error."""
        mock_response = Mock()
        error_msg = "404 Not Found"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            error_msg
        )
        mock_request.return_value = mock_response

        client = EbayClient(access_token="test_token")

        with pytest.raises(requests.exceptions.HTTPError):
            client._make_request("GET", "http://test.com")

    @patch.object(EbayClient, "_make_request")
    def test_search_items_basic(self, mock_request):
        """Test basic search_items method."""
        mock_response = Mock()
        mock_response.json.return_value = {"itemSummaries": [{"itemId": "123"}]}
        mock_request.return_value = mock_response

        client = EbayClient(access_token="test_token")
        result = client.search_items(q="pokemon cards")

        assert result == {"itemSummaries": [{"itemId": "123"}]}
        mock_request.assert_called_once_with(
            "GET",
            f"{client.BROWSE_BASE_URL}/item_summary/search",
            params={"limit": 50, "offset": 0, "q": "pokemon cards"},
        )

    @patch.object(EbayClient, "_make_request")
    def test_search_items_all_params(self, mock_request):
        """Test search_items with all parameters."""
        mock_response = Mock()
        mock_response.json.return_value = {"itemSummaries": []}
        mock_request.return_value = mock_response

        client = EbayClient(access_token="test_token")
        client.search_items(
            q="test query",
            category_ids="123,456",
            filter_="price:[10..100]",
            sort="price",
            limit=100,
            offset=50,
            custom_param="custom_value",
        )

        expected_params = {
            "limit": 100,
            "offset": 50,
            "q": "test query",
            "category_ids": "123,456",
            "filter": "price:[10..100]",
            "sort": "price",
            "custom_param": "custom_value",
        }

        mock_request.assert_called_once_with(
            "GET",
            f"{client.BROWSE_BASE_URL}/item_summary/search",
            params=expected_params,
        )

    @patch.object(EbayClient, "_make_request")
    def test_search_items_limit_capped(self, mock_request):
        """Test search_items with limit capped at 200."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_request.return_value = mock_response

        client = EbayClient(access_token="test_token")
        client.search_items(limit=500)

        _, kwargs = mock_request.call_args
        assert kwargs["params"]["limit"] == 200

    @patch.object(EbayClient, "_make_request")
    def test_search_items_by_image(self, mock_request):
        """Test search_items_by_image method."""
        mock_response = Mock()
        mock_response.json.return_value = {"itemSummaries": [{"itemId": "456"}]}
        mock_request.return_value = mock_response

        client = EbayClient(access_token="test_token")
        image_data = b"fake_image_data"
        result = client.search_items_by_image(
            image_data=image_data,
            category_ids="123",
            filter_="condition:new",
            sort="price",
            limit=25,
            offset=10,
        )

        encoded_image = base64.b64encode(image_data).decode("utf-8")
        expected_payload = {
            "image": encoded_image,
            "limit": 25,
            "offset": 10,
            "category_ids": "123",
            "filter": "condition:new",
            "sort": "price",
        }

        assert result == {"itemSummaries": [{"itemId": "456"}]}
        mock_request.assert_called_once_with(
            "POST",
            f"{client.BROWSE_BASE_URL}/item_summary/search_by_image",
            json=expected_payload,
        )

    @patch.object(EbayClient, "_make_request")
    def test_search_items_by_image_limit_capped(self, mock_request):
        """Test search_items_by_image with limit capped at 200."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_request.return_value = mock_response

        client = EbayClient(access_token="test_token")
        client.search_items_by_image(image_data=b"test", limit=300)

        _, kwargs = mock_request.call_args
        assert kwargs["json"]["limit"] == 200

    @patch.object(EbayClient, "_make_request")
    def test_get_item_basic(self, mock_request):
        """Test basic get_item method."""
        mock_response = Mock()
        mock_response.json.return_value = {"itemId": "123", "title": "Test Item"}
        mock_request.return_value = mock_response

        client = EbayClient(access_token="test_token")
        result = client.get_item("v1|123|456")

        assert result == {"itemId": "123", "title": "Test Item"}
        mock_request.assert_called_once_with(
            "GET", f"{client.BROWSE_BASE_URL}/item/v1|123|456", params={}
        )

    @patch.object(EbayClient, "_make_request")
    def test_get_item_with_fieldgroups(self, mock_request):
        """Test get_item with fieldgroups parameter."""
        mock_response = Mock()
        mock_response.json.return_value = {"itemId": "123"}
        mock_request.return_value = mock_response

        client = EbayClient(access_token="test_token")
        client.get_item("v1|123|456", fieldgroups="PRODUCT,EXTENDED")

        mock_request.assert_called_once_with(
            "GET",
            f"{client.BROWSE_BASE_URL}/item/v1|123|456",
            params={"fieldgroups": "PRODUCT,EXTENDED"},
        )

    @patch.object(EbayClient, "_make_request")
    def test_get_items_by_item_group(self, mock_request):
        """Test get_items_by_item_group method."""
        mock_response = Mock()
        items_data = [{"itemId": "123"}, {"itemId": "456"}]
        mock_response.json.return_value = {"items": items_data}
        mock_request.return_value = mock_response

        client = EbayClient(access_token="test_token")
        result = client.get_items_by_item_group("group123")

        assert result == {"items": [{"itemId": "123"}, {"itemId": "456"}]}
        mock_request.assert_called_once_with(
            "GET",
            f"{client.BROWSE_BASE_URL}/item/get_items_by_item_group",
            params={"item_group_id": "group123"},
        )

    @patch.object(EbayClient, "_make_request")
    def test_search_products_basic(self, mock_request):
        """Test basic search_products method."""
        mock_response = Mock()
        mock_response.json.return_value = {"productSummaries": [{"epid": "123"}]}
        mock_request.return_value = mock_response

        client = EbayClient(access_token="test_token")
        result = client.search_products(q="iphone")

        assert result == {"productSummaries": [{"epid": "123"}]}
        mock_request.assert_called_once_with(
            "GET",
            f"{client.CATALOG_BASE_URL}/product_summary/search",
            params={"limit": 200, "offset": 0, "q": "iphone"},
        )

    @patch.object(EbayClient, "_make_request")
    def test_search_products_all_params(self, mock_request):
        """Test search_products with all parameters."""
        mock_response = Mock()
        mock_response.json.return_value = {"productSummaries": []}
        mock_request.return_value = mock_response

        client = EbayClient(access_token="test_token")
        client.search_products(
            q="test product",
            category_ids="456,789",
            gtin="1234567890123",
            mpn="TEST-MPN-123",
            limit=100,
            offset=25,
        )

        expected_params = {
            "limit": 100,
            "offset": 25,
            "q": "test product",
            "category_ids": "456,789",
            "gtin": "1234567890123",
            "mpn": "TEST-MPN-123",
        }

        mock_request.assert_called_once_with(
            "GET",
            f"{client.CATALOG_BASE_URL}/product_summary/search",
            params=expected_params,
        )

    @patch.object(EbayClient, "_make_request")
    def test_search_products_limit_capped(self, mock_request):
        """Test search_products with limit capped at 200."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_request.return_value = mock_response

        client = EbayClient(access_token="test_token")
        client.search_products(limit=500)

        _, kwargs = mock_request.call_args
        assert kwargs["params"]["limit"] == 200

    @patch.object(EbayClient, "_make_request")
    def test_get_product(self, mock_request):
        """Test get_product method."""
        mock_response = Mock()
        mock_response.json.return_value = {"epid": "123456", "title": "Test Product"}
        mock_request.return_value = mock_response

        client = EbayClient(access_token="test_token")
        result = client.get_product("123456")

        assert result == {"epid": "123456", "title": "Test Product"}
        mock_request.assert_called_once_with(
            "GET", f"{client.CATALOG_BASE_URL}/product/123456"
        )

    def test_set_marketplace(self):
        """Test set_marketplace method."""
        client = EbayClient(access_token="test_token", marketplace_id="EBAY_US")

        assert client.marketplace_id == "EBAY_US"
        assert client.session.headers["X-EBAY-C-MARKETPLACE-ID"] == "EBAY_US"

        client.set_marketplace("EBAY_GB")

        assert client.marketplace_id == "EBAY_GB"
        assert client.session.headers["X-EBAY-C-MARKETPLACE-ID"] == "EBAY_GB"

    def test_build_filter_simple(self):
        """Test build_filter with simple conditions."""
        client = EbayClient(access_token="test_token")

        conditions = {"price": "[10..100]", "condition": "new"}
        result = client.build_filter(conditions)

        # Since dict iteration order is not guaranteed in older Python versions,
        # we'll check both possible orders
        expected_results = [
            "price:[10..100],condition:new",
            "condition:new,price:[10..100]",
        ]
        assert result in expected_results

    def test_build_filter_with_list_values(self):
        """Test build_filter with list values."""
        client = EbayClient(access_token="test_token")

        conditions = {"categoryIds": ["123", "456", "789"], "condition": "new"}
        result = client.build_filter(conditions)

        # Check that list values are joined with |
        assert "categoryIds:123|456|789" in result
        assert "condition:new" in result

    def test_build_filter_empty(self):
        """Test build_filter with empty conditions."""
        client = EbayClient(access_token="test_token")

        result = client.build_filter({})
        assert result == ""

    def test_build_filter_mixed_types(self):
        """Test build_filter with mixed value types."""
        client = EbayClient(access_token="test_token")

        conditions = {
            "string_value": "test",
            "int_value": 42,
            "list_value": [1, 2, 3],
            "float_value": 3.14,
        }
        result = client.build_filter(conditions)

        # Check that all types are converted to strings properly
        assert "string_value:test" in result
        assert "int_value:42" in result
        assert "list_value:1|2|3" in result
        assert "float_value:3.14" in result


class TestEbayClientIntegration:
    """Integration test cases."""

    def test_full_client_initialization_flow(self):
        """Test complete client initialization and header setup."""
        access_token = "integration_test_token"
        marketplace_id = "EBAY_DE"
        client = EbayClient(access_token=access_token, marketplace_id=marketplace_id)

        # Verify all components are properly initialized
        assert client.access_token == access_token
        assert client.marketplace_id == marketplace_id
        assert isinstance(client.session, requests.Session)
        assert client.session.headers["Authorization"] == f"Bearer {access_token}"
        assert client.session.headers["X-EBAY-C-MARKETPLACE-ID"] == marketplace_id
        assert client.session.headers["Content-Type"] == "application/json"
        assert client.BROWSE_BASE_URL == "https://api.ebay.com/buy/browse/v1"
        assert (
            client.CATALOG_BASE_URL == "https://api.ebay.com/commerce/catalog/v1_beta"
        )

    @patch.object(EbayClient, "_make_request")
    def test_search_workflow(self, mock_request):
        """Test a typical search workflow."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "itemSummaries": [
                {"itemId": "v1|123|456", "title": "Pokemon Card"},
                {"itemId": "v1|789|012", "title": "Yu-Gi-Oh Card"},
            ]
        }
        mock_request.return_value = mock_response

        client = EbayClient(access_token="test_token")

        # Search for items
        search_results = client.search_items(q="trading cards", limit=10)

        # Verify search results
        assert len(search_results["itemSummaries"]) == 2
        assert search_results["itemSummaries"][0]["title"] == "Pokemon Card"

        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            "GET",
            f"{client.BROWSE_BASE_URL}/item_summary/search",
            params={"limit": 10, "offset": 0, "q": "trading cards"},
        )


@pytest.fixture
def mock_ebay_client():
    """Fixture providing an EbayClient instance with mocked requests."""
    with patch("requests.Session"):
        return EbayClient(access_token="test_fixture_token", marketplace_id="EBAY_US")


@pytest.fixture
def sample_image_data():
    """Fixture providing sample image data for testing."""
    return b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"


def test_fixture_usage(mock_ebay_client):
    """Test that the fixture works correctly."""
    assert mock_ebay_client.access_token == "test_fixture_token"
    assert mock_ebay_client.marketplace_id == "EBAY_US"
    assert mock_ebay_client.BROWSE_BASE_URL == "https://api.ebay.com/buy/browse/v1"


def test_image_fixture_usage(sample_image_data):
    """Test that the image fixture works correctly."""
    assert isinstance(sample_image_data, bytes)
    assert len(sample_image_data) > 0


class TestEbayClientErrorHandling:
    """Test error handling scenarios."""

    @patch("requests.Session.request")
    def test_network_error_handling(self, mock_request):
        """Test handling of network errors."""
        error_msg = "Network unreachable"
        mock_request.side_effect = requests.exceptions.ConnectionError(error_msg)

        client = EbayClient(access_token="test_token")

        with pytest.raises(requests.exceptions.ConnectionError):
            client._make_request("GET", "http://test.com")

    @patch("requests.Session.request")
    def test_timeout_error_handling(self, mock_request):
        """Test handling of timeout errors."""
        mock_request.side_effect = requests.exceptions.Timeout("Request timed out")

        client = EbayClient(access_token="test_token")

        with pytest.raises(requests.exceptions.Timeout):
            client._make_request("GET", "http://test.com")

    @patch.object(EbayClient, "_make_request")
    def test_api_error_response(self, mock_request):
        """Test handling of API error responses."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "errors": [{"errorId": 123, "message": "Invalid request"}]
        }
        mock_request.return_value = mock_response

        client = EbayClient(access_token="test_token")
        result = client.search_items(q="test")

        # The client should still return the error response
        assert "errors" in result
        assert result["errors"][0]["message"] == "Invalid request"
