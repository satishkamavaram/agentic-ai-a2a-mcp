from fastmcp import FastMCP, Context
import os
import logging
from fastmcp.server.dependencies import get_http_headers
from dataclasses import dataclass
from starlette.responses import JSONResponse

logging.basicConfig(level=logging.DEBUG)
from fastmcp.server.auth.providers.jwt import JWTVerifier


from fastmcp.server.auth import OAuthProxy

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
@mcp.custom_route("/mcp/.well-known/oauth-protected-resource", methods=["GET"])
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

if __name__ == "__main__":
    mcp.run(
        transport="http",
        port=8000
    )