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

This project demonstrates how to build a intelligent Jira assistant using the A2A protocol and MCP server architecture with Authentication enabled:

- **A2A Jira Client**: The user enters a natural language query in the client tool.
- **A2A Jira Server**: Receives the query, consults the LLM (OpenAI/ChatGPT), and orchestrates tool calls to the Jira MCP server.
- **Jira MCP Server**: Exposes Jira-related tools (e.g., fetch tickets, resolve user IDs,create appointment) as MCP endpoints.

The A2A Jira Server acts as an agent, using the A2A protocol to communicate with clients and the MCP protocol to interact with backend tools. The agent card (discovery document) is accessible at `/.well-known/agent-card` and describes the agent's capabilities and skills.

This project demonstrates:
- How A2A protocol enables agent remote invocation with authentication enabled
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

***user query and output***
```
User Query:  schedule a appointment on 4th sept 2026 at 4:30 am  from email satish.k@test.com and to these users test1@test.com test2@test.com to discuss about future of agentic AI

Response from jira agent : root=SendMessageSuccessResponse(id='4b51e944d33343dbb52503564eaad765', jsonrpc='2.0', result=Task(artifacts=[Artifact(artifact_id='b9922ba7-e47c-43fd-ae00-5a49772db76e', description=None, extensions=None, metadata=None, name=None, parts=[Part(root=TextPart(kind='text', metadata=None, text="I don't have the capability to directly schedule appointments or access calendars. I recommend using your email or a calendar application like Google Calendar or Microsoft Outlook to schedule your meeting for September 4, 2026, at 4:30 AM with the attendees you mentioned to discuss the future of agentive AI. \n\nIf there is anything else I can assist with, such as fetching Jira tickets or user details, please let me know!"))])], context_id='8f228802-406f-493e-940e-804188a48aab', history=[Message(context_id='8f228802-406f-493e-940e-804188a48aab', extensions=None, kind='message', message_id='ffcb9d40f0354accb8def82a61c3fc69', metadata=None, parts=[Part(root=TextPart(kind='text', metadata=None, text='schedule a appointment on 4th sept 2026 at 4:30 am  from email satish.k@test.com and to these users test1@test.com test2@test.com to discuss about future of agentic AI'))], reference_task_ids=None, role=<Role.user: 'user'>, task_id='54584f03-1c6d-4f45-baf0-52dc8d61a471')], id='54584f03-1c6d-4f45-baf0-52dc8d61a471', kind='task', metadata=None, status=TaskStatus(message=None, state=<TaskState.completed: 'completed'>, timestamp='2025-08-31T10:37:41.089149+00:00')))

User Query:  tickets assigned 1234

Response from jira agent : root=SendMessageSuccessResponse(id='ab695361a53343d6b9dfe795cb066cab', jsonrpc='2.0', result=Task(artifacts=[Artifact(artifact_id='fcdbe579-2df9-4745-987a-9eca90551a1e', description=None, extensions=None, metadata=None, name=None, parts=[Part(root=TextPart(kind='text', metadata=None, text='Here are the tickets currently assigned to Satish:\n\n1. **Ticket ID:** PROJ-2024-001\n   - **Summary:** Fix authentication vulnerability in user login system\n   - **Description:** Critical security issue affecting user accounts\n   - **Priority:** HIGH\n   - **Status:** IN PROGRESS\n\n2. **Ticket ID:** PROJ-2024-002\n   - **Summary:** Update customer database schema for GDPR compliance\n   - **Description:** Database contains PII that needs protection\n   - **Priority:** MEDIUM\n   - **Status:** OPEN'))])], context_id='5f900e3b-c84e-44b8-b4c9-575fdd26b735', history=[Message(context_id='5f900e3b-c84e-44b8-b4c9-575fdd26b735', extensions=None, kind='message', message_id='2ef3116c3eb94e0aa20bbd0d0a53c7e7', metadata=None, parts=[Part(root=TextPart(kind='text', metadata=None, text='tickets assigned 1234'))], reference_task_ids=None, role=<Role.user: 'user'>, task_id='a05d78ae-754c-45e4-9cca-4a2060092889'), Message(context_id='5f900e3b-c84e-44b8-b4c9-575fdd26b735', extensions=None, kind='message', message_id='aca07267-0b71-47df-91b7-86b5cc2d9ab8', metadata=None, parts=[], reference_task_ids=None, role=<Role.agent: 'agent'>, task_id='a05d78ae-754c-45e4-9cca-4a2060092889'), Message(context_id='5f900e3b-c84e-44b8-b4c9-575fdd26b735', extensions=None, kind='message', message_id='2ace1fef-d167-4bf0-90c8-5c14bc6dd471', metadata=None, parts=[], reference_task_ids=None, role=<Role.agent: 'agent'>, task_id='a05d78ae-754c-45e4-9cca-4a2060092889')], id='a05d78ae-754c-45e4-9cca-4a2060092889', kind='task', metadata=None, status=TaskStatus(message=None, state=<TaskState.completed: 'completed'>, timestamp='2025-08-31T10:38:36.061076+00:00')))

```