"""
JustTCG API interaction module for accessing trading card game data.
"""

import os
from typing import Any, Optional

import requests


class JustTCGClient:
    """Client for interacting with the JustTCG API."""

    BASE_URL = "https://api.justtcg.com/v1"

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the client with an API key."""
        self.api_key = api_key or os.getenv("JUSTTCG_API_KEY")
        self.session = requests.Session()
        self._auth()

    def _auth(self) -> None:
        """Authenticate the user and set up authorization headers."""
        if not self.api_key:
            raise ValueError(
                "API key is required. Set JUSTTCG_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.session.headers.update(
            {"x-api-key": self.api_key, "Content-Type": "application/json"}
        )

    def _get(
        self, endpoint: str, params: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Make a GET request to the JustTCG API and return the response."""
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"GET request failed: {e}") from e

    def _post(
        self, endpoint: str, data: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Make a POST request to the JustTCG API and return the response."""
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"

        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"POST request failed: {e}") from e

    def get_card_info(self, card_id: str) -> dict[str, Any]:
        """
        Get card information by card ID.

        Args:
            card_id: The TCGPlayer ID of the card

        Returns:
            Dictionary containing the card information
        """
        params = {"tcgplayerId": card_id}
        return self._get("cards", params=params)
