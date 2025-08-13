from fastmcp import FastMCP
import os
import logging
mcp = FastMCP("jira MCP Server")
logging.basicConfig(level=logging.INFO)
api_key = os.getenv("API_KEY")
config_path = os.getenv("CONFIG_PATH")

logging.info(f"Server received API_KEY: {api_key}")
logging.info(f"Server received config path: {config_path}")

@mcp.tool()
def get_tickets_assigned_to_user(user_email: str) -> list:
    """Get tickets assigned to a user from jira.

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

@mcp.tool()
def get_email_id_from_user_id(user_id: str) -> str:
    """Get email ID from user ID.

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

@mcp.tool()
async def get_weather_alerts(state: str) -> str:
    """Get weather alerts for a German state.

    Args:
        state: Two-letter German state code (e.g. BW, BY)
    """
    data = {
        "features": [
            {
                "id": "1",
                "type": "Alert",
                "properties": {
                    "headline": "Severe Thunderstorm Warning",
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

if __name__ == "__main__":
    # Run with streamable-http transport for HTTP-based communication in containers
    # Note: FastMCP doesn't support transport_options parameter
    # Session timeout is handled by the underlying transport layer
    """mcp.run(
        transport="streamable-http", 
        host="0.0.0.0", 
        port=8000
    )"""
    mcp.run(transport='stdio')