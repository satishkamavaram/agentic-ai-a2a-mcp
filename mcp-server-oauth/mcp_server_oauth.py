from fastmcp import FastMCP, Context
from fastmcp.server.dependencies import get_http_headers
from dataclasses import dataclass
from starlette.responses import JSONResponse
from fastmcp.server.auth import OAuthProxy
from fastmcp.server.auth.providers.jwt import JWTVerifier
from pydantic import BaseModel, Field
from typing import List
import datetime
import os
import logging

logging.basicConfig(level=logging.DEBUG)
CURRENT_YEAR = datetime.datetime.now().year

# setup keycloak server : create realm satishrealm and create private client with client id and secret for mcp server

# In Keycloak 
## creates 'Visual Studio Code' as client and client_is as random uuid in keycloak and in jwt token aud field value will be None
""" sample decoded jwt token 
{
  "exp": 1757013717,
  "iat": 1757013417,
  "jti": "onrtna:929cf910-370e-9949-8f9b-46ec3913e753",
  "iss": "http://localhost:8080/realms/satishrealm",
  "sub": "8ede11cf-58a5-4bc2-91e2-aebd381f52cc",
  "typ": "Bearer",
  "azp": "ed6bfa06-4b96-4a37-aa29-40cc4f1965f0",
  "sid": "48eb9b22-db6a-4c27-8417-eac0af6092f4",
  "acr": "1",
  "allowed-origins": [
    "http://127.0.0.1:33418",
    "http://127.0.0.1",
    "http://localhost:33418",
    "https://vscode.dev",
    "http://localhost",
    "https://insiders.vscode.dev"
  ],
  "scope": "openid profile email",
  "email_verified": false,
  "name": "s f",
  "preferred_username": "satish2",
  "given_name": "s",
  "family_name": "f",
  "email": "satish2@test.com"
}
"""

"""
configure in mcp.json vscode client

"weather-mcp-server-oauth": {
			"url": "http://127.0.0.1:8000/mcp",
			"type": "http"
		}
"""
# Configure token validation for Keycloak
token_verifier = JWTVerifier(
    jwks_uri="http://127.0.0.1:8080/realms/satishrealm/protocol/openid-connect/certs",
    issuer="http://127.0.0.1:8080/realms/satishrealm",
    #audience="account" #in token claim "aud" field value is None
)

# Create the auth proxy to enable FastMCP servers to authenticate with OAuth providers that don’t support Dynamic Client Registration (DCR). In this case keycloak.
# create a private client with client id and secret in keycloak for mcp server which helps to create dynamic client registration. In this case, Visual Studio Code public client is created in keycloak.
# use discovery endpoint to get authorization and token endpoints - http://127.0.0.1:8080/realms/satishrealm/.well-known/openid-configuration
auth = OAuthProxy(
    # Provider's OAuth endpoints (from their documentation)
    upstream_authorization_endpoint="http://127.0.0.1:8080/realms/satishrealm/protocol/openid-connect/auth",
    upstream_token_endpoint="http://127.0.0.1:8080/realms/satishrealm/protocol/openid-connect/token",
    upstream_client_id="testmcpclient",
    upstream_client_secret="ZpyYMtFUelgEuMeijXl3D1hZGrQNzCub",
    token_verifier=token_verifier,
    base_url="http://127.0.0.1:8000",
    resource_server_url="http://127.0.0.1:8000/mcp",
)
mcp = FastMCP("Weather MCP Server",auth=auth)

# This is needed for vscode mcp client to discover the OAuth protected resource as a workaround until fix is available in fastmcp sdk.
#https://github.com/modelcontextprotocol/python-sdk/pull/1288
#https://github.com/seanhoughton/mcp-python-sdk/pull/1
#https://github.com/modelcontextprotocol/python-sdk/issues/1264
# for vscode copilot IDE client
@mcp.custom_route("/mcp/.well-known/oauth-protected-resource", methods=["GET"])
async def custom_well_known_endpoint(request):
    return JSONResponse({
        "resource": f"http://127.0.0.1:8000/mcp",
        "authorization_servers": ["http://127.0.0.1:8080/realms/satishrealm"],
        "scopes_supported": ["openid", "email", "profile"],
        "bearer_methods_supported": ["header"]
    })

# for cursor IDE client
@mcp.custom_route("/.well-known/oauth-protected-resource/mcp", methods=["GET"])
async def custom_well_known_endpoint(request):
    return JSONResponse({
        "resource": f"http://127.0.0.1:8000/mcp",
        "authorization_servers": ["http://127.0.0.1:8080/realms/satishrealm"],
        "scopes_supported": ["openid", "email", "profile"],
        "bearer_methods_supported": ["header"]
    })

@dataclass
class StateInfo:
    state: str


@mcp.tool(description="Collect state information interactively from user if not provided")
async def collect_state_info(ctx: Context) -> str:
    """Collect state information through interactive prompts."""
    result = await ctx.elicit(
        message="Please provide your two letter German state code (e.g. BW, BY)",
        response_type=StateInfo
    )
    
    if result.action == "accept":
        state = result.data
        return get_weather_alerts(state.state)
    elif result.action == "decline":
        return "Information not provided"
    else:
        return "Operation cancelled"

@mcp.prompt()
async def get_prompt_weather_alerts(state_name: str) -> str:
    return f"weather info {state_name} state"

@mcp.tool(description="Get weather alerts for a German state")
async def get_weather_alerts(state: str) -> str:
    """Get weather alerts for a German state.

    Args:
        state: Two-letter German state code (e.g. BW, BY)
    """
    headers = get_http_headers()
    logging.info(f"headers received: {headers}")

    data = {
        "features": [
            {
                "id": "1",
                "state": state,
                "type": "Alert",
                "properties": {
                    "headline": "Severe Thunderstorm BA Warning",
                    "description": "A severe thunderstorm is approaching your area. Take cover immediately.",
                    "severity": "Severe",
                    "effective": "2024-10-01T14:00:00Z",
                    "expires": "2024-10-01T15:00:00Z"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [-120.0, 37.0]
                }
            }
        ]
    }
    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)



def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Headline: {props.get('headline', 'Unknown')}
Description: {props.get('description', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
"""

@mcp.prompt()
async def get_prompt_tickets_assigned_to_user(user_email: str) -> str:
    return f"jira issues assigned {user_email}"

@mcp.tool()
def get_tickets_assigned_to_user(user_email: str) -> list:
   
    """Get tickets assigned to a user from jira using emailId.

    Args:
        user_email: email of the user to get tickets assigned to user
    
        
    Returns:
        A list of tickets assigned to the user in JSON format (with sensitive data redacted)
    """
    print(f"Access token in get_tickets_assigned_to_user")
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




class AppointmentRequest(BaseModel):
    """
    Simple model for creating an appointment with clear field descriptions.
    """
    to_emails: str = Field(
        ...,
        description="comma seperated email addresses for all meeting attendees or invitees. Example: ['user1@example.com', 'user2@example.com']"
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


@mcp.prompt()
async def get_prompt_schedule_appointment(appointment: AppointmentRequest) -> str:
    return f"schedule appointment with {appointment.to_emails} users from my emailId {appointment.from_email} {appointment.date} {appointment.time} about {appointment.subject}"


@mcp.prompt()
async def get_prompt_create_appointment(to_emails: str = Field(
        ...,
        description="comma seperated email addresses for all meeting attendees or invitees. Example: ['user1@example.com', 'user2@example.com']"), from_email: str = Field(
        ...,
        description="Email address of the meeting organizer or sender or from. Example: 'organizer@example.com'"
    ), subject: str= Field(
        ...,
        description="Title or subject of the appointment. Example: 'Team Meeting'"
    ), date: str= Field(
        ...,
        description="Date of the appointment in YYYY-MM-DD format. Always include 4-digit year. Example: '2025-09-01'"
    ), time: str= Field(
        ...,
        description="Time of the appointment in HH:MM 24-hour format. Example: '14:30' for 2:30 PM"
    )) -> str:
    """
    Generate a prompt to schedule an appointment.

    Args:
        to_emails (list): List of attendee email addresses.
        from_email (str): Organizer's email address.
        subject (str): Appointment subject.
        date (str): Date of the appointment. Format: YYYY-MM-DD (e.g., 2025-09-01).
        time (str): Time of the appointment. Format: HH:MM (24-hour, e.g., 16:00).

    Returns:
        str: Prompt string for scheduling the appointment.
    """
    return f"schedule appointment with {to_emails} users from my emailId {from_email} {date} {time} about {subject}"

@mcp.tool(description=f"Create an appointment with attendees, subject, date, and time. Always provide the date in YYYY-MM-DD format, including the year. If the user omits the year, use {CURRENT_YEAR}.")
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


class IssueTypeSchema(BaseModel):
    issue_type: str = Field(
        description="Select the type of issue (Network/Hardware/Software/Other)",
        pattern="^(Network|Hardware|Software|Other)$"
    )
    issue_name: str = Field(
        description="Name of the issue")

@mcp.tool()
async def submit_ticket(ctx: Context, issue_type: str = "") -> str:
    """submit ticket"""
    allowed_types = {"Network", "Hardware", "Software", "Other"}
    while not issue_type or issue_type not in allowed_types:
        result = await ctx.elicit(message="What type of issue are you experiencing?",response_type=IssueTypeSchema)
        logging.info(f"result received: {result}")
        print(f"result received: {result}")
        if result.action == "accept":
            issue = result.data
            return f"Ticket submitted!\nType: {issue.issue_type}"
        elif result.action == "decline":
            return "Information not provided"
        else:  # cancel
            return "Operation cancelled"

if __name__ == "__main__":
    mcp.run(
        transport="http",
        port=8000
    )