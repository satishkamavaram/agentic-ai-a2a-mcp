# HTTP-Based Model Context Protocol (MCP) Implementation

> **⚠️ POC DISCLAIMER: This is a Proof of Concept (POC) implementation. Please do not evaluate this code for production-level code structure, modularity, or best practices. This project is designed for educational and demonstration purposes only.**

## 📚 Table of Contents

- [Introduction](#introduction)
- [🔄 Architecture Overview](#-architecture-overview)
- [🚀 Quick Start](#-quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Set up OpenAI Key](#set-up-openai-key)
  - [Running the HTTP MCP Servers](#running-the-http-mcp-servers)
  - [Running the Multi-Server UI Client](#running-the-http-mcp-ui-client)


## Introduction

This HTTP implementation provides a **web-based Model Context Protocol (MCP) architecture** that enables MCP client-server communication over HTTP transport instead of stdio. The system features **multi-server support** through a unified client interface, allowing seamless integration with multiple MCP servers simultaneously. The system includes:

- **HTTP JIRA MCP Server** (`mcp_jira_server_http.py`) - Jira MCP Server (Port 8000)
- **HTTP Weather MCP Server** (`mcp_weather_server.py`) - Weather MCP Server (Port 8001)
- **Multi-Server MCP Client Config** (`mcp.json`) - Configuration file supporting multiple MCP servers
- **Unified Agentic UI Client** (`mcp_client_http_ui.py`) - Single interface connecting to multiple MCP servers

## 🔄 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Multi-Server MCP Client                      │
│                   (mcp_client_http_ui.py)                       │
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │      PII        │    │   OpenAI LLM    │                     │
│  │   Redaction     │    │   Integration   │                     │
│  └─────────────────┘    └─────────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
          │                           │
          │ HTTP/JSON                 │ HTTP/JSON
          │ Port 8000                 │ Port 8001
          ▼                           ▼
┌─────────────────┐           ┌─────────────────┐
│  JIRA MCP       │           │  Weather MCP    │
│  Server         │           │  Server         │
│  (FastMCP)      │           │  (FastMCP)      │
│                 │           │                 │
│ • Tickets       │           │ • Alerts        │
└─────────────────┘           └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Required dependencies (see `requirements.txt`)
- (Optional) Keycloak server for OAuth authentication

### Installation 

```bash
# Clone or navigate to the project directory
cd $HOME/ai-mcp

# install with pip
python3 -m venv ai-mcp
source ai-mcp/bin/activate
pip install -r requirements.txt
```

### Set up OpenAI Key
In .env file at the root of project configure your OPENAI_API_KEY  
```
OPENAI_API_KEY=your_openai_api_key_here
```

### Running the HTTP MCP Servers

The MCP servers run as standalone HTTP services on different ports:

```bash
# Navigate to the http directory
cd http

# Terminal 1: Start the HTTP JIRA MCP server
python mcp_jira_server_http.py

# Terminal 2: Start the HTTP Weather MCP server  
python mcp_weather_server_http.py
```

You should see output similar to:

**JIRA Server (Port 8000):**
```

╭─ FastMCP 2.0 ──────────────────────────────────────────────────────────────╮
│    🖥️  Server name:    jira MCP Server                                     │
│    📦 Transport:       Streamable-HTTP                                     │
│    🔗 Server URL:      http://127.0.0.1:8000/mcp                           │
│    🏎️  FastMCP version: 2.11.3                                             │
│    🤝 MCP version:     1.13.0                                              │
╰────────────────────────────────────────────────────────────────────────────╯
```

**Weather Server (Port 8001):**
```

╭─ FastMCP 2.0 ──────────────────────────────────────────────────────────────╮
│    🖥️  Server name:    Weather MCP Server                                  │
│    📦 Transport:       Streamable-HTTP                                     │
│    🔗 Server URL:      http://127.0.0.1:8001/mcp                           │
│    🏎️  FastMCP version: 2.11.3                                             │
│    🤝 MCP version:     1.13.0                                              │
╰────────────────────────────────────────────────────────────────────────────╯
```

### Running the HTTP MCP UI Client

#### 🔧 Multi-Server Configuration

The HTTP client uses the `mcp.json` configuration file to connect to multiple MCP servers simultaneously. Each server can have its own authentication headers and configuration:

```json
{
  "mcpServers": {
    "jira_server": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp",
      "headers": {
        "Authorization": "Bearer token-jira",
        "X-Custom-Header": "custom-value-jira"
      },
      "auth": "oauth"
    },
     "weather_server": {
      "type": "http",
      "url": "http://127.0.0.1:8001/mcp",
      "headers": {
        "Authorization": "Bearer token-weather", 
        "X-Custom-Header": "custom-value-weather"
      },
      "auth": "oauth"
    }
  }
}
```

#### 🚀 Starting the UI Client

```bash
# In a new terminal, navigate to the http directory
cd http

# Start the unified UI client (both jira and weather mcp servers must be running)
python mcp_client_http_ui.py
```

