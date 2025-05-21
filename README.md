# Cal.com FastMCP Server

> ⚠️ **Disclaimer**: This project is not affiliated with or endorsed by Cal.com. I am an independent developer and have no association with Cal.com in any official capacity.

This project provides a FastMCP server for interacting with the Cal.com API. It allows Language Learning Models (LLMs) to use tools to connect with important Cal.com functionalities like managing event types and bookings.

## Prerequisites

- Python 3.8+
- A Cal.com account and API Key (v2)

## Setup

1.  **Clone the repository (if applicable) or download the files.**

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up the Cal.com API Key:**
    You need to set the `CALCOM_API_KEY` environment variable. You can get your API key from your Cal.com settings page (usually under Developer or Security settings).

    -   **Linux/macOS:**
        ```bash
        export CALCOM_API_KEY="your_actual_api_key_here"
        ```
        To make it permanent, add this line to your shell configuration file (e.g., `.bashrc`, `.zshrc`).

    -   **Windows (PowerShell):**
        ```powershell
        $env:CALCOM_API_KEY="your_actual_api_key_here"
        ```
        To make it permanent, you can set it through the System Properties > Environment Variables.

## Running the Server

Once the setup is complete, you can run the FastMCP server:

```bash
fastmcp run app.py --transport sse --port 8010
```

The server will start at localhost:8010, and you should see output indicating it's running. If the `CALCOM_API_KEY` is not set, a warning will be displayed.

## Available Tools

The server currently provides the following tools for LLM interaction:

-   `get_api_status()`: Checks if the Cal.com API key is configured in the environment.
-   `list_event_types()`: Fetches a list of all event types from Cal.com.
-   `get_bookings(...)`: Fetches a list of bookings from Cal.com, with optional filters (event_type_id, user_id, status, date_from, date_to, limit).
-   `create_booking(...)`: Creates a new booking in Cal.com. Requires parameters like start_time, attendee details, and event type identifiers.

## Development Notes

-   The Cal.com API base URL is set to `https://api.cal.com/v2`.
-   Authentication is primarily handled using a Bearer token with the `CALCOM_API_KEY`.
-   The `create_booking` tool uses the `cal-api-version: 2024-08-13` header as specified in the Cal.com API v2 documentation for that endpoint.
-   Error handling is included in the API calls to provide informative responses.

## Important Security Note

**Never hardcode your `CALCOM_API_KEY` directly into the source code.** Always use environment variables as described in the setup instructions to keep your API key secure.