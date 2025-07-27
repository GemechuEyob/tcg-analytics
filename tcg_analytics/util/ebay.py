import base64
from typing import Any, Optional

import requests


class EbayClient:
    """
    eBay API client supporting Browse API and Catalog API operations.
    """

    BROWSE_BASE_URL = "https://api.ebay.com/buy/browse/v1"
    CATALOG_BASE_URL = "https://api.ebay.com/commerce/catalog/v1_beta"

    def __init__(self, access_token: str, marketplace_id: str = "EBAY_US"):
        """
        Initialize eBay client.

        Args:
            access_token: OAuth 2.0 access token
            marketplace_id: eBay marketplace (default: EBAY_US)
        """
        self.access_token = access_token
        self.marketplace_id = marketplace_id
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {access_token}",
                "X-EBAY-C-MARKETPLACE-ID": marketplace_id,
                "Content-Type": "application/json",
            }
        )

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling."""
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response

    # Browse API Methods

    def search_items(
        self,
        q: Optional[str] = None,
        category_ids: Optional[str] = None,
        filter_: Optional[str] = None,
        sort: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Search for items using the Browse API.

        Args:
            q: Search query string
            category_ids: Category IDs to search within
            filter_: Refinement filters
            sort: Sort order
            limit: Number of items to return (max 200)
            offset: Number of items to skip

        Returns:
            Search results dictionary
        """
        url = f"{self.BROWSE_BASE_URL}/item_summary/search"

        params = {"limit": min(limit, 200), "offset": offset}

        if q:
            params["q"] = q
        if category_ids:
            params["category_ids"] = category_ids
        if filter_:
            params["filter"] = filter_
        if sort:
            params["sort"] = sort

        params.update(kwargs)

        response = self._make_request("GET", url, params=params)
        return response.json()

    def search_items_by_image(
        self,
        image_data: bytes,
        category_ids: Optional[str] = None,
        filter_: Optional[str] = None,
        sort: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """
        Search for items using image recognition.

        Args:
            image_data: Binary image data
            category_ids: Category IDs to search within
            filter_: Refinement filters
            sort: Sort order
            limit: Number of items to return
            offset: Number of items to skip

        Returns:
            Search results dictionary
        """
        url = f"{self.BROWSE_BASE_URL}/item_summary/search_by_image"

        # Encode image as base64
        encoded_image = base64.b64encode(image_data).decode("utf-8")

        payload = {"image": encoded_image, "limit": min(limit, 200), "offset": offset}

        if category_ids:
            payload["category_ids"] = category_ids
        if filter_:
            payload["filter"] = filter_
        if sort:
            payload["sort"] = sort

        response = self._make_request("POST", url, json=payload)
        return response.json()

    def get_item(
        self, item_id: str, fieldgroups: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Get detailed information for a specific item.

        Args:
            item_id: eBay item ID
            fieldgroups: Additional data to include

        Returns:
            Item details dictionary
        """
        url = f"{self.BROWSE_BASE_URL}/item/{item_id}"

        params = {}
        if fieldgroups:
            params["fieldgroups"] = fieldgroups

        response = self._make_request("GET", url, params=params)
        return response.json()

    def get_items_by_item_group(self, item_group_id: str) -> dict[str, Any]:
        """
        Get items that are part of an item group (variations).

        Args:
            item_group_id: eBay item group ID

        Returns:
            Item group details dictionary
        """
        url = f"{self.BROWSE_BASE_URL}/item/get_items_by_item_group"

        params = {"item_group_id": item_group_id}

        response = self._make_request("GET", url, params=params)
        return response.json()

    # Catalog API Methods

    def search_products(
        self,
        q: Optional[str] = None,
        category_ids: Optional[str] = None,
        gtin: Optional[str] = None,
        mpn: Optional[str] = None,
        limit: int = 200,
        offset: int = 0,
    ) -> dict[str, Any]:
        """
        Search for products in the eBay catalog.

        Args:
            q: Search query string
            category_ids: Category IDs to search within
            gtin: Global Trade Item Number
            mpn: Manufacturer Part Number
            limit: Number of products to return (max 200)
            offset: Number of products to skip

        Returns:
            Product search results dictionary
        """
        url = f"{self.CATALOG_BASE_URL}/product_summary/search"

        params = {"limit": min(limit, 200), "offset": offset}

        if q:
            params["q"] = q
        if category_ids:
            params["category_ids"] = category_ids
        if gtin:
            params["gtin"] = gtin
        if mpn:
            params["mpn"] = mpn

        response = self._make_request("GET", url, params=params)
        return response.json()

    def get_product(self, epid: str) -> dict[str, Any]:
        """
        Get detailed information for a specific product.

        Args:
            epid: eBay Product ID

        Returns:
            Product details dictionary
        """
        url = f"{self.CATALOG_BASE_URL}/product/{epid}"

        response = self._make_request("GET", url)
        return response.json()

    # Utility Methods

    def set_marketplace(self, marketplace_id: str):
        """
        Change the marketplace for subsequent requests.

        Args:
            marketplace_id: eBay marketplace ID (e.g., EBAY_US, EBAY_GB)
        """
        self.marketplace_id = marketplace_id
        self.session.headers["X-EBAY-C-MARKETPLACE-ID"] = marketplace_id

    def build_filter(self, conditions: dict[str, Any]) -> str:
        """
        Build a filter string for search requests.

        Args:
            conditions: Dictionary of filter conditions

        Returns:
            Formatted filter string
        """
        filters = []
        for key, value in conditions.items():
            if isinstance(value, list):
                value = "|".join(str(v) for v in value)
            filters.append(f"{key}:{value}")
        return ",".join(filters)
