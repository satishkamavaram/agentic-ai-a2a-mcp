from fastmcp import FastMCP
import os
import logging
import datetime
import requests
from typing import List, Union
from pydantic import BaseModel, Field
from fastmcp.server.auth import RemoteAuthProvider
from pydantic import AnyHttpUrl
import datetime
from starlette.responses import JSONResponse
from starlette.routing import Route
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.auth import OAuthProxy
from fastmcp.server.dependencies import get_http_headers

from fastmcp import FastMCP, Context
from fastmcp.server.dependencies import get_http_headers
from dataclasses import dataclass
from starlette.responses import JSONResponse
from starlette.routing import Route
from pydantic import AnyHttpUrl
from fastmcp.server.auth import OAuthProxy
from fastmcp.server.auth.providers.jwt import JWTVerifier
from pydantic import BaseModel, Field
from typing import List
import datetime
import os
import logging

logging.basicConfig(level=logging.DEBUG)
CURRENT_YEAR = datetime.datetime.now().year

import httpx

import json
from typing import Annotated, Any, Optional
from fastmcp.server.auth import RemoteAuthProvider

logging.basicConfig(level=logging.DEBUG)
CURRENT_YEAR = datetime.datetime.now().year

# For MCP IDE Clients
# Configure token validation for Keycloak
token_verifier = JWTVerifier(
    jwks_uri="https://test.keycloak.com/realms/vodafone/protocol/openid-connect/certs",
    issuer="https://test.keycloak.com/realms/vodafone",
    # audience="account" #in token claim "aud" field value is None
)
auth = OAuthProxy(
    upstream_authorization_endpoint="https://test.keycloak.com/realms/vodafone/protocol/openid-connect/auth",
    upstream_token_endpoint="https://test.keycloak.com/realms/vodafone/protocol/openid-connect/token",
    upstream_client_id="vscode_mcp",
    upstream_client_secret="1Sd6Do4LflYRWFjXzIHpL6HAsNZC0FgB",
    token_verifier=token_verifier,
    base_url="http://127.0.0.1:8000",
    resource_server_url="http://127.0.0.1:8000/mcp",
)

# For Application AI agents
# production setup - https://gofastmcp.com/deployment/http#custom-path
class CompanyAuthProvider(RemoteAuthProvider):
    def __init__(self):
        # handles token validation using IDP provider public keys
        token_verifier = JWTVerifier(
            # to fetch public keys for token validation
            jwks_uri="https://iam.keycloak.com/auth/realms/satishrealm/protocol/openid-connect/certs",
            issuer="https://iam.keycloak.com/auth/realms/satishrealm",
            audience="account",  # Configure this with "aud" field value in jwt token you received. so that intended service is using the token and not misused
        )

        super().__init__(
            token_verifier=token_verifier,
            authorization_servers=[
                AnyHttpUrl(
                    "https://iam.keycloak.com/auth/realms/satishrealm"
                )  # telling mcp clients list of IDPs to trust
            ],
            resource_server_url="http://127.0.0.1:8000/mcp",  # Your server base URL
        )

    # this is to just add custom routes , nothing related to token verification
    def get_routes(self) -> list[Route]:
        """Add custom endpoints to the standard protected resource routes."""

        # Get the standard OAuth protected resource routes
        routes = super().get_routes()

        # Add authorization server metadata forwarding for client convenience
        async def authorization_server_metadata(request):
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://iam.keycloak.com/auth/realms/satishrealm/.well-known/openid-configuration"
                )
                response.raise_for_status()
                return JSONResponse(response.json())

        # /.well-known/oauth-protected-resource
        # /mcp/.well-known/oauth-authorization-server
        routes.append(
            Route(
                "/mcp/.well-known/oauth-protected-resource",
                authorization_server_metadata,
            )
        )
        routes.append(Route("/test", test_endpoint))

        return routes


# mcp = FastMCP("DMX MCP Server", auth=auth)
mcp = FastMCP("DMX MCP Server", auth=CompanyAuthProvider())


# this is just custom endpoint not used during authentication
@mcp.custom_route("/mcp/.well-known/oauth-protected-resource", methods=["GET"])
async def custom_well_known_endpoint(request):
    return JSONResponse(
        {
            "resource": "http://127.0.0.1:8000/mcp",
            "authorization_servers": [
                "https://test.keycloak.com/realms/vodafone"
            ],
            "scopes_supported": ["openid", "email", "profile"],
            "bearer_methods_supported": ["header"],
        }
    )

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

if __name__ == "__main__":
    mcp.run(
        transport="http",
        port=8000
    )
