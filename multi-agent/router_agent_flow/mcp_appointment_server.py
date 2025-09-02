
from fastmcp import FastMCP
import os
import logging
from fastmcp.server.dependencies import get_http_headers
from typing import List
from pydantic import BaseModel, Field
from fastmcp.server.auth import RemoteAuthProvider
from fastmcp.server.auth.providers.jwt import JWTVerifier
from pydantic import AnyHttpUrl
import datetime

logging.basicConfig(level=logging.DEBUG)
CURRENT_YEAR = datetime.datetime.now().year


# Configure token validation for Keycloak
token_verifier = JWTVerifier(
    jwks_uri="http://127.0.0.1:8080/realms/satishrealm/protocol/openid-connect/certs",
    issuer="http://127.0.0.1:8080/realms/satishrealm",
    audience="account" #"testclient"  # Configure this with "aud" field value in jwt token you received.
)


# Create the remote auth provider
auth = RemoteAuthProvider(
    token_verifier=token_verifier,
    authorization_servers=[AnyHttpUrl("http://127.0.0.1:8080/realms/satishrealm")],
    resource_server_url="http://127.0.0.1:8000"  # Your MCP server URL
)

mcp = FastMCP("jira MCP Server",auth=token_verifier) # for auth login, configure like this FastMCP("jira MCP Server",auth=auth)






class AppointmentRequest(BaseModel):
    """
    Simple model for creating an appointment with clear field descriptions.
    """
    to_emails: List[str] = Field(
        ...,
        description="List of email addresses for all meeting attendees or invitees. Example: ['user1@example.com', 'user2@example.com']"
    )
    
    from_email: str = Field(
        ...,
        description="Email address of the meeting organizer or sender or from. Example: 'organizer@example.com'"
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


@mcp.tool(description=f"Create an appointment with to_emails, from_email, subject, date, and time. Always provide the date in YYYY-MM-DD format, including the year. If the user omits the year, use {CURRENT_YEAR}.")
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
    headers = get_http_headers()
    logging.info(f"create_appointment_pydantic headers received: {headers}")
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