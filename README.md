HotelHive
=========

HotelHive is a conversational hotel search assistant powered by LangGraph, LangChain, and an MCP tool server. It grounds responses in your local Excel datasets and supports follow-up questions with conversational memory.

Features
- Conversational agent with memory (multi-turn chat)
- MCP tool `hotel_list` backed by your Excel data
- Schema-free prompting: the assistant infers fields directly from the records
- Flexible queries by city/county/price/amenities/etc.
- Lists all matching hotels with optional pagination

Project Structure
- `client.py`: Runs the chat client, connects to the MCP server via stdio, loads tools, and maintains conversation history.
- `server/hotelinfo_server.py`: FastMCP server exposing the `hotel_list` tool, reading data from `data/hotels.xlsx`.
- `agent/hotel_finder.py`: Prompt + LLM runnable used by the server tool to generate grounded answers.
- `data/`: Excel files (`hotels.xlsx`, etc.) used as the knowledge source.
- `type/`: Pydantic models (not required in current schema-free flow).
- `requirements.txt`: Python dependencies.

Prerequisites
- Python 3.12+
- A Google Generative AI API key (`API_KEY`) and model name (`MODEL`, e.g., `gemini-2.0-flash`).

Setup
1. Create and activate a virtual environment:
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Create a `.env` file in the project root with:
   - `API_KEY=your_google_genai_key`
   - `MODEL=gemini-2.0-flash`
4. Ensure your data file exists:
   - `data/hotels.xlsx`

Run
- From the project root, activate the venv and run:
  - `python3 client.py`
- Interact in the console (type `exit` to quit). Examples:
  - `suggest hotels under 150 in chicago`
  - `list all hotels in miami`
  - `share details for hotel_85`

Notes
- The assistant answers using only the provided Excel data; if a requested field doesn’t exist, it will say it’s not available.
- Large result sets will paginate (first 50 shown) and continue when you confirm.

Troubleshooting
- If you see import/module errors, ensure the client launches the server with `python -m server.hotelinfo_server` (already configured in `client.py`).
- If responses seem off, confirm your `.env` variables and that `data/hotels.xlsx` contains the expected columns and values.

License
- MIT


