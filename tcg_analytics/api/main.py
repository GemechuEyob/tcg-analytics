"""
FastAPI application for TCG analytics.
"""

import os
import sys
from typing import Any

from fastapi import FastAPI, HTTPException, status

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from tcg_analytics.util.justtcg import JustTCGClient

app = FastAPI(
    title="TCG Analytics API",
    description="API for trading card game analytics and data retrieval",
    version="1.0.0",
)


@app.get("/api/v1/health_check", response_model=dict[str, str])
async def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "healthy", "message": "API is running"}


@app.get("/api/v1/cards/{card_id}", response_model=dict[str, Any])
async def get_card(card_id: str):
    """
    Get card information by card ID using the JustTCG API.

    Args:
        card_id: The TCGPlayer ID of the card

    Returns:
        Dictionary containing the card information
    """
    try:
        client = JustTCGClient()
        card_data = client.get_card_info(card_id)
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
