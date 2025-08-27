> **⚠️ POC DISCLAIMER: This is a Proof of Concept (POC) implementation. Please do not evaluate this code for production-level code structure, modularity, or best practices. This project is designed for educational and demonstration purposes only.**

## 📚 Table of Contents

- [Introduction](#introduction)
- [🚀 Quick Start](#-quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Set up OpenAI Key](#set-up-openai-key)
  - [Run MCP server](#run-mcp-server)
  - [Run jira agent](#run-jira-agent)



# Introduction

## How It Works

The agent uses Google ADK to wrap OpenAI LLMs and MCP tools. When a user asks a Jira-related question, the agent:

1. Analyzes the query and determines which tools are needed
2. Resolves dependencies (e.g., userId → email)
3. Calls MCP tools in the correct order
4. Returns a natural language answer


A sophisticated jira agent client built using google adk library. This agent enables natural language queries to OpenAI LLM, which intelligently selects and orchestrates **multiple MCP server tool calls includes dynamic tool chaining**

The system demonstrates **intelligent tool chaining** where the LLM dynamically identifies dependencies between tools. For example, when a user provides only a `userId`, the LLM automatically:
1. **Recognizes the data dependency** - determines that an email address is needed for the target operation
2. **Orchestrates tool sequence** - first calls `get_email_id_from_user_id` to resolve the userId to an email
3. **Chains subsequent calls** - uses the retrieved email to call tools like `get_tickets_assigned_to_user`

This **autonomous tool orchestration** eliminates the need for users to understand internal data relationships or tool dependencies, enabling natural language queries like *"show jira tickets for user 1234"* to be automatically expanded into the correct sequence of tool calls.



## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Required dependencies (see `requirements.txt`)

### Installation 

```bash
# Clone or navigate to the project directory
cd $HOME/ai-mcp/adk-jira-agent

# install with pip
python3 -m venv ai-mcp
source ai-mcp/bin/activate
pip install -r ../requirements.txt

```

### Set up OpenAI Key
In .env file at the root of project or in this level configure your OPEN_API_KEY and OPENAI_API_BASE
```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
```

### Run MCP server 

Start mcp server. 

```bash
python mcp_jira_server_http.py
```

### Run jira agent

Run the jira agent 

```bash
python adk_agent_jira.py
```

