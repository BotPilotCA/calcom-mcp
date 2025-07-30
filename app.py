import os
import logging
import requests
from typing import Optional, Dict, Any, List
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP
mcp = FastMCP("Cal.com MCP")

# Cal.com API configuration
CALCOM_API_BASE = "https://api.cal.com/v2"
CALCOM_API_KEY = os.environ.get("CALCOM_API_KEY")

def get_headers() -> Dict[str, str]:
    """Get headers for Cal.com API requests"""
    if not CALCOM_API_KEY:
        return {}
    return {
        "Authorization": f"Bearer {CALCOM_API_KEY}",
        "Content-Type": "application/json"
    }

def make_api_request(method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
    """Make a request to the Cal.com API"""
    if not CALCOM_API_KEY:
        return {
            "error": "API key not configured",
            "message": "CALCOM_API_KEY environment variable is not set"
        }
    
    url = f"{CALCOM_API_BASE}/{endpoint.lstrip('/')}"
    headers = get_headers()
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, params=params)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data, params=params)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, params=params)
        else:
            return {"error": "Unsupported HTTP method", "method": method}
        
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        else:
            return {
                "error": "API request failed",
                "status_code": response.status_code,
                "response": response.text
            }
    except requests.exceptions.RequestException as e:
        return {
            "error": "Request exception",
            "message": str(e)
        }

@mcp.tool()
def get_api_status() -> str:
    """Check if the Cal.com API key is configured in the environment."""
    if CALCOM_API_KEY:
        return "Cal.com API key is configured and ready to use."
    else:
        return "Cal.com API key is not configured. Please set the CALCOM_API_KEY environment variable."

@mcp.tool()
def list_event_types() -> Dict[str, Any]:
    """Fetch a list of all event types from Cal.com for the authenticated account."""
    return make_api_request("GET", "/event-types")

@mcp.tool()
def get_bookings(
    event_type_id: Optional[int] = None,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Fetch a list of bookings from Cal.com with optional filters.
    
    Args:
        event_type_id: Filter by specific event type ID
        user_id: Filter by specific user ID
        status: Filter by booking status (e.g., 'confirmed', 'cancelled')
        date_from: Filter bookings from this date (ISO format)
        date_to: Filter bookings until this date (ISO format)
        limit: Maximum number of bookings to return
    """
    params = {}
    if event_type_id is not None:
        params["eventTypeId"] = event_type_id
    if user_id is not None:
        params["userId"] = user_id
    if status:
        params["status"] = status
    if date_from:
        params["dateFrom"] = date_from
    if date_to:
        params["dateTo"] = date_to
    if limit is not None:
        params["limit"] = limit
    
    return make_api_request("GET", "/bookings", params=params)

@mcp.tool()
def create_booking(
    start_time: str,
    attendee_name: str,
    attendee_email: str,
    event_type_id: int,
    attendee_timezone: Optional[str] = None,
    attendee_language: Optional[str] = None,
    meeting_url: Optional[str] = None,
    booking_questions: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Create a new booking in Cal.com.
    
    Args:
        start_time: The start time of the booking (ISO format)
        attendee_name: Name of the attendee
        attendee_email: Email of the attendee
        event_type_id: ID of the event type to book
        attendee_timezone: Timezone of the attendee
        attendee_language: Language preference of the attendee
        meeting_url: Custom meeting URL if applicable
        booking_questions: List of additional booking questions and answers
    """
    data = {
        "start": start_time,
        "eventTypeId": event_type_id,
        "attendee": {
            "name": attendee_name,
            "email": attendee_email
        }
    }
    
    if attendee_timezone:
        data["attendee"]["timeZone"] = attendee_timezone
    if attendee_language:
        data["attendee"]["language"] = attendee_language
    if meeting_url:
        data["meetingUrl"] = meeting_url
    if booking_questions:
        data["bookingQuestions"] = booking_questions
    
    # Add the specific API version header for booking creation
    headers = get_headers()
    headers["cal-api-version"] = "2024-08-13"
    
    url = f"{CALCOM_API_BASE}/bookings"
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        else:
            return {
                "error": "Booking creation failed",
                "status_code": response.status_code,
                "response": response.text
            }
    except requests.exceptions.RequestException as e:
        return {
            "error": "Request exception",
            "message": str(e)
        }

@mcp.tool()
def list_schedules(
    user_id: Optional[int] = None,
    team_id: Optional[int] = None,
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    List all schedules available to the authenticated user.
    
    Args:
        user_id: Filter by specific user ID
        team_id: Filter by specific team ID
        limit: Maximum number of schedules to return
    """
    params = {}
    if user_id is not None:
        params["userId"] = user_id
    if team_id is not None:
        params["teamId"] = team_id
    if limit is not None:
        params["limit"] = limit
    
    return make_api_request("GET", "/schedules", params=params)

@mcp.tool()
def list_teams(limit: Optional[int] = None) -> Dict[str, Any]:
    """
    List all teams available to the authenticated user.
    
    Args:
        limit: Maximum number of teams to return
    """
    params = {}
    if limit is not None:
        params["limit"] = limit
    
    return make_api_request("GET", "/teams", params=params)

@mcp.tool()
def list_users(limit: Optional[int] = None) -> Dict[str, Any]:
    """
    List all users available to the authenticated account.
    
    Args:
        limit: Maximum number of users to return
    """
    params = {}
    if limit is not None:
        params["limit"] = limit
    
    return make_api_request("GET", "/users", params=params)

@mcp.tool()
def list_webhooks(limit: Optional[int] = None) -> Dict[str, Any]:
    """
    List all webhooks configured for the authenticated account.
    
    Args:
        limit: Maximum number of webhooks to return
    """
    params = {}
    if limit is not None:
        params["limit"] = limit
    
    return make_api_request("GET", "/webhooks", params=params)

if __name__ == "__main__":
    # Get port from environment variable (Render.com requirement)
    port = int(os.environ.get("PORT", 8000))
    
    logger.info(f"Starting MCP server on port {port}")
    logger.info(f"Cal.com API key configured: {'Yes' if CALCOM_API_KEY else 'No'}")
    
    # Configure for web deployment
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=port,
        path="/mcp"
    )
