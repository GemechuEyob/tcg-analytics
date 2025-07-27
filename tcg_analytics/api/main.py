"""
FastAPI application for TCG analytics.
"""

import os
import sys
from typing import Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from tcg_analytics.util.ebay import EbayClient
from tcg_analytics.util.justtcg import JustTCGClient

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))


app = FastAPI(
    title="TCG Analytics API",
    description="API for trading card game analytics and data retrieval",
    version="1.0.0",
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = os.path.join(os.path.dirname(__file__), "..", "..", "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.get("/api/v1/health_check", response_model=dict[str, str])
async def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "healthy", "message": "API is running"}


async def _get_ebay_data(card_name: str) -> dict[str, Any]:
    """
    Fetch relevant card data from eBay API.

    Args:
        card_name: The name of the card to search for

    Returns:
        Dictionary containing eBay data or empty dict if no data found
    """
    try:
        ebay_token = os.getenv("EBAY_ACCESS_TOKEN")
        if not ebay_token:
            return {}

        ebay_client = EbayClient(ebay_token)
        search_query = f"{card_name} trading card"

        # Search for items on eBay
        ebay_results = ebay_client.search_items(
            q=search_query,
            category_ids="2536",  # Trading Cards category
            limit=10,
        )

        # Extract relevant data
        ebay_data = {
            "ebay_listings": [],
            "ebay_price_range": {},
            "ebay_total_results": ebay_results.get("total", 0),
        }

        if "itemSummaries" in ebay_results:
            for item in ebay_results["itemSummaries"]:
                listing = {
                    "title": item.get("title", ""),
                    "price": item.get("price", {}).get("value", ""),
                    "currency": item.get("price", {}).get("currency", ""),
                    "condition": item.get("condition", ""),
                    "item_web_url": item.get("itemWebUrl", ""),
                    "seller": item.get("seller", {}).get("username", ""),
                }
                ebay_data["ebay_listings"].append(listing)

            # Calculate price range from listings
            prices = []
            for item in ebay_results["itemSummaries"]:
                if "price" in item and "value" in item["price"]:
                    try:
                        prices.append(float(item["price"]["value"]))
                    except (ValueError, TypeError):
                        continue

            if prices:
                ebay_data["ebay_price_range"] = {
                    "min": min(prices),
                    "max": max(prices),
                    "average": sum(prices) / len(prices),
                }

        return ebay_data

    except Exception:
        # Return empty dict if eBay API fails
        return {}


@app.get("/api/v1/cards/{card_id}", response_model=dict[str, Any])
async def get_card(card_id: str):
    """
    Get card information by card ID using the JustTCG API and eBay data.

    Args:
        card_id: The TCGPlayer ID of the card

    Returns:
        Dictionary containing the card information with eBay data if available
    """
    try:
        # Get JustTCG data
        client = JustTCGClient()
        card_data = client.get_card_info(card_id)

        # Extract card name for eBay search
        card_name = ""
        if "data" in card_data and card_data["data"]:
            if isinstance(card_data["data"], list) and len(card_data["data"]) > 0:
                card_name = card_data["data"][0].get("name", "")
            elif isinstance(card_data["data"], dict):
                card_name = card_data["data"].get("name", "")

        # Get eBay data if card name is available
        ebay_data = {}
        if card_name:
            ebay_data = await _get_ebay_data(card_name)

        # Concatenate eBay data with JustTCG response
        if ebay_data:
            card_data["ebay_data"] = ebay_data

        return card_data

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Configuration error: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve card information: {str(e)}",
        ) from e
