> **⚠️ POC DISCLAIMER: This is a Proof of Concept (POC) implementation. Please do not evaluate this code for production-level code structure, modularity, or best practices. This project is designed for educational and demonstration purposes only.**

## 📚 Table of Contents

- [Introduction](#introduction)
- [🚀 Quick Start](#-quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Set up OpenAI Key](#set-up-openai-key)
  - [Run MCP server](#run-mcp-server)
  - [Run A2A Jira Agent Server](#run-a2a-jira-agent-server)
  - [Run A2A Jira Agent Client](#run-a2a-jira-agent-client)


# Introduction

This project demonstrates how to build a intelligent Jira assistant using the A2A protocol and MCP server architecture:

- **A2A Jira Client**: The user enters a natural language query in the client tool.
- **A2A Jira Server**: Receives the query, consults the LLM (OpenAI/ChatGPT), and orchestrates tool calls to the Jira MCP server.
- **Jira MCP Server**: Exposes Jira-related tools (e.g., fetch tickets, resolve user IDs,create appointment) as MCP endpoints.

The A2A Jira Server acts as an agent, using the A2A protocol to communicate with clients and the MCP protocol to interact with backend tools. The agent card (discovery document) is accessible at `/.well-known/agent-card` and describes the agent's capabilities and skills.

This project demonstrates:
- How A2A protocol enables agent remote invocation
- How MCP server exposes business logic as composable tools
- How LLMs can orchestrate tool chaining and dependency resolution
- How agent cards enable discoverability and interoperability


## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Required dependencies (see `requirements.txt`)

### Installation 

```bash
# Clone or navigate to the project directory
cd $HOME/ai-mcp/a2a-jira-agent

# install with pip
python3 -m venv ai-a2a
source ai-a2a/bin/activate
pip install -r ../requirements.txt

```

### Set up OpenAI Key
In .env file at the root of project or in this level configure your OPEN_API_KEY and OPENAI_API_BASE
```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
```

### Run MCP server 

```bash
python mcp_jira_server_http.py
```

### Run A2A jira agent server

By default server runs on 10001 port. Agent Card can be accessed using 
http://localhost:10001/.well-known/agent-card

```bash
python a2a_jira_server.py
```


### Run A2A jira agent client

```bash
python a2a_jira_client.py
```

**sample queries**:
- schedule a appointment on 4th sept 2026 at 4:30 am  from email satish.k@test.com and to these users test1@test.com test2@test.com to discuss about future of agentic AI
- jira tickets assigned to 1234