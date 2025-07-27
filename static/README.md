# TCG Card Lookup UI

A static HTML interface for looking up trading card information using TCGPlayer IDs.

## Features

- Clean, responsive design
- Real-time card information lookup
- Organized display of card details (basic info, pricing, additional details)
- Raw JSON view toggle
- Error handling and loading states
- Mobile-friendly interface

## Usage

1. **Start the FastAPI backend:**
   ```bash
   # From the project root
   uvicorn tcg_analytics.api.main:app --reload
   ```

2. **Open the HTML file:**
   Open `static/index.html` in your web browser

3. **Enter a TCGPlayer ID:**
   - Input a valid TCGPlayer ID in the search field
   - Click "Search" to fetch card information
   - View the organized card details or toggle to see raw JSON

## Configuration

The UI is configured to connect to the local FastAPI server at `http://localhost:8000`. If your server runs on a different port, update the `API_BASE_URL` variable in the JavaScript section.

## API Requirements

- The FastAPI backend must be running
- A valid JustTCG API key must be configured (via `JUSTTCG_API_KEY` environment variable)
- The `/api/v1/cards/{card_id}` endpoint must be accessible
