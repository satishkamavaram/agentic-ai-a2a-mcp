# HTTP-Based Model Context Protocol (MCP) Implementation

> **⚠️ POC DISCLAIMER: This is a Proof of Concept (POC) implementation. Please do not evaluate this code for production-level code structure, modularity, or best practices. This project is designed for educational and demonstration purposes only.**

## 📚 Table of Contents

- [Introduction](#introduction)
- [🔄 Architecture Overview](#-architecture-overview)
- [🚀 Quick Start](#-quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Set up OpenAI Key](#set-up-openai-key)
  - [Running the HTTP MCP Server](#running-the-http-mcp-server)
  - [Running the HTTP MCP CLI Client](#running-the-http-mcp-cli-client)
  - [Running the HTTP MCP UI Client](#running-the-http-mcp-ui-client)

## Introduction

This HTTP implementation provides a **web-based Model Context Protocol (MCP) architecture** that enables client-server communication over HTTP transport instead of stdio. The system includes:

- **HTTP MCP Server** (`mcp_server_http.py`) - FastMCP-based server 
- **HTTP CLI Client** (`mcp_client_http.py`) - Command-line interface with persistent HTTP connections
- **HTTP UI Client** (`mcp_client_http_ui.py`) - PyQt5-based graphical interface with configuration management

## 🔄 Architecture Overview

```
┌─────────────────┐    HTTP/JSON     ┌─────────────────┐
│   MCP Client    │ ←──────────────→ │   MCP Server    │
│  (CLI/UI)       │    Port 8000     │  (FastMCP)      │
└─────────────────┘                  └─────────────────┘
         │                                    
         │                                    
    ┌────▼────┐                          
    │ OpenAI  │                          
    │   LLM   │                          
    └─────────┘                          
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

### Running the HTTP MCP Server

The MCP server runs as a standalone HTTP service on port 8000:

```bash
# Navigate to the http directory
cd http

# Start the HTTP MCP server
python mcp_server_http.py
```

You should see output similar to:
```
╭INFO:root:Server received API_KEY: None
INFO:root:Server received config path: None


╭─ FastMCP 2.0 ──────────────────────────────────────────────────────────────╮
│                                                                            │
│        _ __ ___ ______           __  __  _____________    ____    ____     │
│       _ __ ___ / ____/___ ______/ /_/  |/  / ____/ __ \  |___ \  / __ \    │
│      _ __ ___ / /_  / __ `/ ___/ __/ /|_/ / /   / /_/ /  ___/ / / / / /    │
│     _ __ ___ / __/ / /_/ (__  ) /_/ /  / / /___/ ____/  /  __/_/ /_/ /     │
│    _ __ ___ /_/    \__,_/____/\__/_/  /_/\____/_/      /_____(_)____/      │
│                                                                            │
│                                                                            │
│                                                                            │
│    🖥️  Server name:     jira MCP Server                                     │
│    📦 Transport:       Streamable-HTTP                                     │
│    🔗 Server URL:      http://127.0.0.1:8000/mcp                           │
│                                                                            │
│    📚 Docs:            https://gofastmcp.com                               │
│    🚀 Deploy:          https://fastmcp.cloud                               │
│                                                                            │
│    🏎️  FastMCP version: 2.11.3                                              │
│    🤝 MCP version:     1.13.0                                              │
│                                                                            │
╰────────────────────────────────────────────────────────────────────────────╯


[08/18/25 21:40:57] INFO     Starting MCP server 'jira MCP Server' with transport 'http' on http://127.0.0.1:8000/mcp   
```


### Running the HTTP MCP CLI Client

The command-line client connects to the HTTP server and provides an interactive chat interface:

```bash
# In a new terminal, navigate to the http directory  
cd http

# Start the CLI client (server must be running)
python mcp_client_http.py  http://127.0.0.1:8000/mcp
```

**Interactive Commands:**
- Type your queries in natural language


**Example Usage:**
```
MCP HTTP Client Started!
Type your queries or 'quit' to exit.

Query: Show me tickets assigned to john@company.com

[Calling tool get_tickets_assigned_to_user with args {'user_email': 'john@company.com'}]

| Ticket ID     | Summary                           | Assignee          | Priority | Status      |
|---------------|-----------------------------------|-------------------|----------|-------------|
| PROJ-2024-001 | Fix authentication vulnerability  | john@company.com  | HIGH     | IN_PROGRESS |
| PROJ-2024-002 | Update database schema           | john@company.com  | MEDIUM   | OPEN        |
```

### Running the HTTP MCP UI Client

#### 🔧 Configuration

The HTTP clients use the `mcp.json` configuration file for server connection settings:

```json
{
  "mcpServers": {
    "jira_server": {
      "transport": "http",
      "url": "http://127.0.0.1:8000/mcp",
      "headers": {
        "Authorization": "Bearer your_oauth_token_here",
        "X-Custom-Header": "custom-value"
      },
      "auth": "oauth"
    }
  }
}
```

The graphical client provides a PyQt5-based interface with configuration management:

```bash
# In a new terminal, navigate to the http directory
cd http

# Start the UI client (server must be running)
python mcp_client_http_ui.py http://127.0.0.1:8000/mcp
```


