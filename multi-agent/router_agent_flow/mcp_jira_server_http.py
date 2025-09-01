
from fastmcp import FastMCP,Context
import os
import logging
from fastmcp.server.dependencies import get_http_headers
#from fastmcp.auth import AuthContext


logging.basicConfig(level=logging.INFO)
api_key = os.getenv("API_KEY")
config_path = os.getenv("CONFIG_PATH")

logging.info(f"Server received API_KEY: {api_key}")
logging.info(f"Server received config path: {config_path}")

from fastmcp.server.auth import RemoteAuthProvider
from fastmcp.server.auth.providers.jwt import JWTVerifier
from pydantic import AnyHttpUrl

# Configure token validation for Keycloak
token_verifier = JWTVerifier(
    jwks_uri="http://127.0.0.1:8080/realms/satishrealm/protocol/openid-connect/certs",
    issuer="http://127.0.0.1:8080/realms/satishrealm",
    audience="testclient"  # Your Keycloak client ID
)
mcp = FastMCP("jira MCP Server")#,auth=token_verifier)

# Create the remote auth provider
auth = RemoteAuthProvider(
    token_verifier=token_verifier,
    authorization_servers=[AnyHttpUrl("http://127.0.0.1:8080/realms/satishrealm")],
    resource_server_url="http://127.0.0.1:8000"  # Your MCP server URL
)

# Attach OAuth to MCP Server
#mcp.auth = auth
#@mcp.auth()
#@mcp.middleware()
#async def authenticate(auth: AuthContext) -> bool:
async def authenticate(ctx: Context, call_next) -> bool:
    """Authenticate requests using bearer token"""
    auth_header = ctx.headers.get("authorization", "")
    logging.info(f"auth headers received: {ctx.headers}")
    if not auth_header.startswith("Bearer "):
        logging.warning("Missing or invalid Authorization header")
        return False
    
    return await call_next()


@mcp.tool(description="Get tickets assigned to a user from JIRA using emailId")
def get_tickets_assigned_to_user(user_email: str) -> list:
    headers = get_http_headers()
    logging.info(f"headers received: {headers}")
    """Get tickets assigned to a user from jira using emailId.

    Args:
        user_email: email of the user to get tickets assigned to user
    
        
    Returns:
        A list of tickets assigned to the user in JSON format (with sensitive data redacted)
    """
    
    real_tickets = [
        {
            "ticket_id": "PROJ-2024-001", 
            "summary": "Fix authentication vulnerability in user login system",
            "description": "Critical security issue affecting user accounts",
            "assignee": user_email,
            "priority": "HIGH",
            "status": "IN_PROGRESS"
        },
        {
            "ticket_id": "PROJ-2024-002", 
            "summary": "Update customer database schema for GDPR compliance",
            "description": "Database contains PII that needs protection",
            "assignee": user_email,
            "priority": "MEDIUM",
            "status": "OPEN"
        },
    ]
    
    return real_tickets


@mcp.tool(description="Get email ID from user ID input")
def get_email_id_from_user_id(user_id: str) -> str:
    headers = get_http_headers()
    logging.info(f"headers received: {headers}")
    """Get email ID from user ID input.

    Args:
        user_id: User ID to get email for
    
    Returns:
        Email ID of the user
    """
    user_email_map = {
        "user123": "user123@test.com",
        "user456": "user456@test.com"
    }
    return user_email_map.get(user_id, "satish.k@test.com")

import datetime
CURRENT_YEAR = datetime.datetime.now().year

#@mcp.tool(description=f"Create an appointment with attendees, subject, date, and time. Always provide the date in YYYY-MM-DD format, including the year. If the user omits the year, use {CURRENT_YEAR}.")
def create_appointment(to_emails: list, from_email: str, subject: str, date: str, time: str) -> dict:
    headers = get_http_headers()
    logging.info(f"headers received: {headers}")
    """
    Create an appointment and return confirmation details.

    Args:
        to_emails (list): List of attendee email addresses
        from_email (str): Organizer's email address
        subject (str): Appointment subject
        date (str): Date of the appointment. Format: YYYY-MM-DD (e.g., 2025-09-01). Always include the year. If the user omits the year, use {CURRENT_YEAR}.
        time (str): Time of the appointment. Format: HH:MM (24-hour, e.g., 14:30)
    Returns:
        dict: Confirmation details

    Note:
        - date must always be in ISO format: YYYY-MM-DD (e.g., 2025-09-01). The year is required. If the user omits the year, use {CURRENT_YEAR}.
        - time must be in 24-hour format: HH:MM (e.g., 14:30)
    """
    appointment = {
        "to": to_emails,
        "from": from_email,
        "subject": subject,
        "date": date,
        "time": time,
        "status": "created",
        "appointment_id": f"APT-{date.replace('-', '')}-{time.replace(':', '')}"
    }
    logging.info(f"Appointment created: {appointment}")
    return appointment



from typing import List
from pydantic import BaseModel, Field

class AppointmentRequest(BaseModel):
    """
    Simple model for creating an appointment with clear field descriptions.
    """
    to_emails: List[str] = Field(
        ...,
        description="List of email addresses for all meeting attendees. Example: ['user1@example.com', 'user2@example.com']"
    )
    
    from_email: str = Field(
        ...,
        description="Email address of the meeting organizer. Example: 'organizer@example.com'"
    )
    
    subject: str = Field(
        ...,
        description="Title or subject of the appointment. Example: 'Team Meeting'"
    )
    
    date: str = Field(
        ...,
        description="Date of the appointment in YYYY-MM-DD format. Always include 4-digit year. Example: '2025-09-01'"
    )
    
    time: str = Field(
        ...,
        description="Time of the appointment in HH:MM 24-hour format. Example: '14:30' for 2:30 PM"
    )


@mcp.tool(description=f"Create an appointment with attendees, subject, date, and time. Always provide the date in YYYY-MM-DD format, including the year. If the user omits the year, use {CURRENT_YEAR}.")
def create_appointment_pydantic(appointment: AppointmentRequest) -> dict:
    """
    Create an appointment and return confirmation details.
    
    This function takes appointment details in a structured format and creates
    a calendar appointment with a unique ID.
    
    Args:
        appointment: AppointmentRequest object containing all necessary details
        
    Returns:
        dict: Confirmation details including appointment ID and all information
        
    Example:
        >>> request = AppointmentRequest(
        >>>     to_emails=["test1@test.com", "test2@test.com"],
        >>>     from_email="satish.k@test.com",
        >>>     subject="Team Sync",
        >>>     date="2025-09-01",
        >>>     time="14:30"
        >>> )
        >>> create_appointment(request)
    """
    appointment_details = {
        "to": appointment.to_emails,
        "from": appointment.from_email,
        "subject": appointment.subject,
        "date": appointment.date,
        "time": appointment.time,
        "status": "created",
        "appointment_id": f"APT-{appointment.date.replace('-', '')}-{appointment.time.replace(':', '')}"
    }
    return appointment_details

if __name__ == "__main__":
    # Run the MCP server with HTTP transport : python mcp_server_http.py
    #raised oauth issue : https://github.com/jlowin/fastmcp/issues/972
    mcp.run(
        transport="http", 
        port=8000
    )