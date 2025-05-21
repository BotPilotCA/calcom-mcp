"""
Cal.com MCP Server

A FastMCP server for interacting with the Cal.com API. This enables LLMs to manage event types,
create bookings, and access Cal.com scheduling data programmatically.

Author: Arley Peter
License: MIT
Disclaimer: This project is not affiliated with or endorsed by Cal.com in any way.
"""

import os
import requests
from fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the FastMCP server
mcp = FastMCP(
    name="Cal.com MCP Server",
    description="A FastMCP server to interact with the Cal.com API, enabling LLMs to manage bookings, event types, and more."
)

# Get Cal.com API key from environment variable
CALCOM_API_KEY = os.getenv("CALCOM_API_KEY")
print(f"Cal.com API Key: {CALCOM_API_KEY}")
CALCOM_API_BASE_URL = "https://api.cal.com/v2"

@mcp.tool()
def get_api_status() -> str:
    """Checks if the Cal.com API key is configured in the environment."""
    if CALCOM_API_KEY:
        return "Cal.com API key is configured."
    else:
        return "Cal.com API key is NOT configured. Please set the CALCOM_API_KEY environment variable."

@mcp.tool()
def list_event_types() -> dict:
    """Fetches a list of all event types from Cal.com.
    Requires the CALCOM_API_KEY environment variable to be set.
    Returns a dictionary containing the API response or an error message.
    """
    if not CALCOM_API_KEY:
        return {"error": "Cal.com API key not configured. Please set the CALCOM_API_KEY environment variable."}

    headers = {
        "Authorization": f"Bearer {CALCOM_API_KEY}", # Assuming Bearer token based on some v1 docs, might need adjustment for v2 API key auth
        "Content-Type": "application/json"
    }
    # The Cal.com API docs suggest /event-types for v2, but let's try with apiKey query param first as it's a common pattern if Bearer doesn't work.
    # Update: The v2 docs are a bit ambiguous on API key auth. Sticking with Bearer for now as per some examples.
    # If direct API key usage is different (e.g. x-api-key header or specific query param), this needs to be updated.
    # The endpoint for listing event types is assumed to be /event-types based on documentation.
    # Example: curl -X GET https://api.cal.com/v2/event-types -H "Authorization: Bearer YOUR_API_KEY"
    # For API key specific auth, it might be https://api.cal.com/v2/event-types?apiKey=YOUR_API_KEY
    # Let's try the Bearer token approach first as it's more standard for API access.

    try:
        response = requests.get(f"{CALCOM_API_BASE_URL}/event-types", headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        return {"error": f"HTTP error occurred: {http_err}", "status_code": response.status_code, "response_text": response.text}
    except requests.exceptions.RequestException as req_err:
        return {"error": f"Request exception occurred: {req_err}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}


@mcp.tool()
def get_bookings(event_type_id: int = None, user_id: int = None, status: str = None, date_from: str = None, date_to: str = None, limit: int = 20) -> dict:
    """Fetches a list of bookings from Cal.com, with optional filters.
    Requires the CALCOM_API_KEY environment variable to be set.

    Args:
        event_type_id: Optional. Filter bookings by a specific event type ID.
        user_id: Optional. Filter bookings by a specific user ID (typically the user associated with the API key or a managed user).
        status: Optional. Filter bookings by status (e.g., 'ACCEPTED', 'PENDING', 'CANCELLED', 'REJECTED').
        date_from: Optional. Filter bookings from this date (ISO 8601 format, e.g., '2023-10-26T10:00:00.000Z').
        date_to: Optional. Filter bookings up to this date (ISO 8601 format, e.g., '2023-10-27T10:00:00.000Z').
        limit: Optional. Maximum number of bookings to return (default is 20).

    Returns:
        A dictionary containing the API response (list of bookings) or an error message.
    """
    if not CALCOM_API_KEY:
        return {"error": "Cal.com API key not configured. Please set the CALCOM_API_KEY environment variable."}

    headers = {
        "Authorization": f"Bearer {CALCOM_API_KEY}",
        "Content-Type": "application/json"
    }

    params = {}
    if event_type_id is not None:
        params['eventTypeId'] = event_type_id
    if user_id is not None:
        params['userId'] = user_id
    if status is not None:
        params['status'] = status
    if date_from is not None:
        params['dateFrom'] = date_from
    if date_to is not None:
        params['dateTo'] = date_to
    if limit is not None:
        params['take'] = limit # Common Cal.com parameter for limit

    try:
        response = requests.get(f"{CALCOM_API_BASE_URL}/bookings", headers=headers, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        return {"error": f"HTTP error occurred: {http_err}", "status_code": response.status_code, "response_text": response.text}
    except requests.exceptions.RequestException as req_err:
        return {"error": f"Request exception occurred: {req_err}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}


@mcp.tool()
def create_booking(
    start_time: str,
    attendee_name: str,
    attendee_email: str,
    attendee_timezone: str,
    event_type_id: int = None,
    event_type_slug: str = None,
    username: str = None, # Required with event_type_slug if event_type_id is not provided and it's a user event
    team_slug: str = None, # Required with event_type_slug if event_type_id is not provided and it's a team event
    organization_slug: str = None, # Optional, used with event_type_slug + username/team_slug
    attendee_phone_number: str = None,
    attendee_language: str = None,
    guests: list[str] = None,
    location_input: str = None, # Can be a string (e.g., Cal Video, Google Meet) or a custom URL. API expects an object for some cases.
    metadata: dict = None,
    length_in_minutes: int = None,
    booking_fields_responses: dict = None
) -> dict:
    """Creates a new booking in Cal.com.
    Requires the CALCOM_API_KEY environment variable to be set.

    Args:
        start_time: Required. The start time of the booking in ISO 8601 format in UTC (e.g., '2024-08-13T09:00:00Z').
        attendee_name: Required. The name of the primary attendee.
        attendee_email: Required. The email of the primary attendee.
        attendee_timezone: Required. The IANA time zone of the primary attendee (e.g., 'America/New_York').
        event_type_id: Optional. The ID of the event type to book. Either this or (eventTypeSlug + username/teamSlug) is required.
        event_type_slug: Optional. The slug of the event type. Used with username or team_slug if event_type_id is not provided.
        username: Optional. The username of the event owner. Used with event_type_slug.
        team_slug: Optional. The slug of the team owning the event type. Used with event_type_slug.
        organization_slug: Optional. The organization slug, used with event_type_slug and username/team_slug if applicable.
        attendee_phone_number: Optional. Phone number for the attendee (e.g., for SMS reminders).
        attendee_language: Optional. Preferred language for the attendee (e.g., 'en', 'it').
        guests: Optional. A list of additional guest email addresses.
        location_input: Optional. Specifies the meeting location. Can be a simple string for Cal Video, or a URL for custom locations.
                       The API might expect a more structured object for specific integrations.
        metadata: Optional. A dictionary of custom key-value pairs (max 50 keys, 40 char key, 500 char value).
        length_in_minutes: Optional. If the event type allows variable lengths, specify the desired duration.
        booking_fields_responses: Optional. A dictionary for responses to custom booking fields (slug: value).

    Returns:
        A dictionary containing the API response (booking details) or an error message.
    """
    if not CALCOM_API_KEY:
        return {"error": "Cal.com API key not configured. Please set the CALCOM_API_KEY environment variable."}

    if not event_type_id and not (event_type_slug and (username or team_slug)):
        return {"error": "Either 'event_type_id' or ('event_type_slug' and 'username'/'team_slug') must be provided."}

    headers = {
        "Authorization": f"Bearer {CALCOM_API_KEY}",
        "Content-Type": "application/json",
        "cal-api-version": "2024-08-13"  # As per Cal.com v2 API docs for create booking
    }

    payload = {
        "start": start_time,
        "attendee": {
            "name": attendee_name,
            "email": attendee_email,
            "timeZone": attendee_timezone
        }
    }

    if event_type_id:
        payload['eventTypeId'] = event_type_id
    else:
        payload['eventTypeSlug'] = event_type_slug
        if username:
            payload['username'] = username
        elif team_slug:
            payload['teamSlug'] = team_slug
        if organization_slug:
            payload['organizationSlug'] = organization_slug

    if attendee_phone_number:
        payload['attendee']['phoneNumber'] = attendee_phone_number
    if attendee_language:
        payload['attendee']['language'] = attendee_language
    if guests:
        payload['guests'] = guests
    if location_input: # The API docs suggest 'location' can be an object. For simplicity, we'll pass a string if provided.
                      # For more complex location types, this might need to be an object.
        payload['location'] = location_input
    if metadata:
        payload['metadata'] = metadata
    if length_in_minutes:
        payload['lengthInMinutes'] = length_in_minutes
    if booking_fields_responses:
        payload['bookingFieldsResponses'] = booking_fields_responses

    try:
        response = requests.post(f"{CALCOM_API_BASE_URL}/bookings", headers=headers, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        error_details = {"error": f"HTTP error occurred: {http_err}", "status_code": response.status_code}
        try:
            error_details["response_text"] = response.json() # Try to parse JSON error response
        except ValueError:
            error_details["response_text"] = response.text # Fallback to raw text
        return error_details
    except requests.exceptions.RequestException as req_err:
        return {"error": f"Request exception occurred: {req_err}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

if __name__ == "__main__":
    print("Starting Cal.com MCP Server...")
    if not CALCOM_API_KEY:
        print("WARNING: CALCOM_API_KEY environment variable is not set. Some tools may not function.")
    mcp.run()