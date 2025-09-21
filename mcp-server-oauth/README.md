> **⚠️ POC DISCLAIMER: This is a Proof of Concept (POC) implementation. Please do not evaluate this code for production-level code structure, modularity, or best practices. This project is designed for educational and demonstration purposes only.**

## 🎉 **SUCCESS STORY: OAuth Integration Breakthrough!**

**✅ Successfully integrated OAuth2 (Keycloak) authentication flow between VS Code GitHub Copilot and MCP Server!**

This implementation demonstrates a complete end-to-end OAuth authentication pipeline, enabling secure communication between AI agents and MCP services with enterprise-grade identity management.

## Table of Contents

- [Weather MCP Server with OAuth Authentication](#weather-mcp-server-with-oauth-authentication)
  - [Features](#features)
  - [🚀 Quick Start](#-quick-start)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Keycloak Setup](#keycloak-setup)
    - [1. Create Realm](#1-create-realm)
    - [2. Create Private Client for MCP Server](#2-create-private-client-for-mcp-server)
    - [3. Client Configuration](#3-client-configuration)
  - [Usage](#usage)
    - [Running the MCP Server](#running-the-mcp-server)
    - [VS Code Integration](#vs-code-integration)
    - [Start typing queries in vscode IDE co-pilot](#start-typing-queries-in-vscode-ide-co-pilot-to-get-response-from-configured-mcp-server)

# Weather MCP Server with OAuth Authentication

A FastMCP-based weather alert server that demonstrates OAuth2 authentication integration with Keycloak for Model Context Protocol (MCP) applications.

## Features

- **OAuth2 Authentication**: Integrates with Keycloak using FastMCP's OAuthProxy
- **Personalized Prompts**: Each tool can ask you questions in its own style, thanks to support for `@mcp.prompt`.
- **Interactive Conversations**: The server can ask follow-up questions and guide you step-by-step using elicitation, making your experience more engaging and tailored.
- **Weather Alerts**: Provides weather alert information for German states (mock response)
- **Interactive Prompts**: Uses MCP's elicit functionality for user input
- **JWT Token Validation**: Validates tokens from Keycloak
- **VS Code Integration**: Compatible with VS Code MCP client (version used during dev: 1.103.2)


## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Required dependencies (see `requirements.txt`)
- Keycloak (see `https://www.keycloak.org/downloads` - version 26)

### Installation 

```bash
# Clone or navigate to the project directory
cd $HOME/ai-mcp/mcp-server-oauth/

# install with pip
python3 -m venv ai-mcp-server-oauth
source ai-mcp-server-oauth/bin/activate
pip install -r ../requirements.txt

```

## Keycloak Setup

### 1. Create Realm
- Create a new realm named `satishrealm` in Keycloak
- Access the realm at: `http://127.0.0.1:8080/admin/master/console/#/satishrealm`

### 2. Create Private Client for MCP Server
- Create a new client with ID: `testmcpclient`
- Client Type: `Confidential`
- Generate client secret: `ZpyYMtFUelgEuMeijXl3D1hZGrQNzCub`
- This client enables Dynamic Client Registration for VS Code

### 3. Client Configuration
- **Access Type**: `confidential`
- **Valid Redirect URIs**: Add appropriate redirect URIs for your application
- **Web Origins**: Configure CORS settings as needed


## Usage

### Running the MCP Server

```bash
python mcp_server_oauth.py
```

The server will start on `http://127.0.0.1:8000` with the MCP endpoints available at `http://127.0.0.1:8000/mcp`.

### VS Code Integration

Add to your VS Code `mcp.json` configuration:

```json
{
  "weather-mcp-server-oauth": {
    "url": "http://127.0.0.1:8000/mcp",
    "type": "http"
  }
}
```

### Start typing queries in vscode IDE co-pilot to get response from configured mcp server