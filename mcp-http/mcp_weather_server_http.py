from fastmcp import FastMCP, Context
import os
import logging
from fastmcp.server.dependencies import get_http_headers
from dataclasses import dataclass
mcp = FastMCP("Weather MCP Server")
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

# Create the remote auth provider
auth = RemoteAuthProvider(
    token_verifier=token_verifier,
    authorization_servers=[AnyHttpUrl("http://127.0.0.1:8080/realms/satishrealm")],
    resource_server_url="http://127.0.0.1:8000"  # Your MCP server URL
)

# Attach OAuth to MCP Server
#mcp.auth = auth


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
    # Run the MCP server with HTTP transport : python mcp_server_http.py
    #raised oauth issue : https://github.com/jlowin/fastmcp/issues/972
    mcp.run(
        transport="http", 
        port=8001
    )