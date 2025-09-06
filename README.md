> **⚠️ POC DISCLAIMER: This is a Proof of Concept (POC) implementation. Please do not evaluate this code for production-level code structure, modularity, or best practices. This project is designed for educational and demonstration purposes only.**

## Project Components & Demos

This repository showcases a series of demonstrations on how to build advanced, secure, and interconnected AI agent systems using the Model Context Protocol (MCP) and Agent to Agent Protocol(A2A). Each folder highlights a unique architectural pattern.

---

###  1. Basic MCP: Client & Server (stdio)
*   **What it is:** This is the foundational example. It shows how an AI agent (the "client") can directly communicate with a set of tools (the "server") on the same machine, as if they were connected by a simple wire.
*   **How it works:** The client and server processes communicate using **Standard I/O (stdio)**. This is a direct, low-latency communication channel perfect for local development and simple agent-tool integration.

---

### 2. Advanced HTTP Client (`mcp-http/`)
*   **What it is:** This module features a more powerful client, similar to an IDE agent like VS Code Copilot. It can connect to and use tools from **multiple different MCP servers** at the same time, all managed through a single configuration file mcp.json.
*   **How it works:** The client communicates with servers over **HTTP**. It uses a central `mcp.json` configuration file to discover and manage connections to multiple upstream MCP servers, enabling sophisticated, multi-server tool chaining.

---

### 3. Secure OAuth Server (`mcp-server-auth/`)
*   **What it is:** This is an enterprise-grade tool server that requires users to log in before they can use its tools. It's designed to integrate securely with applications like VS Code, ensuring only authorized users have access.
*   **How it works:** This MCP server is protected by an **OAuth 2.0 (Keycloak)** authentication layer. It forces clients like the VS Code Copilot to complete a full OAuth login flow before granting access, providing robust, industry-standard security.

---

###  4. Google ADK Agent (`adk-jira-agent/`)
*   **What it is:** This demonstrates how an agent built with **Google's Agent Development Kit (ADK)** can connect to and use tools from an MCP server, allowing it to perform tasks like interacting with Jira.
*   **How it works:** The agent, built using the Google ADK library, acts as a standard MCP client. It communicates over **HTTP** to an MCP server to leverage its tools, showing how different agent frameworks can interoperate with the MCP ecosystem.

---

###  5. Agent-to-Agent (A2A) Communication (`a2a-jira-agent/`)
*   **What it is:** This is the most advanced example, showcasing a complete, autonomous agent ecosystem. Here, one agent (a "client agent") can discover, connect to, and delegate tasks to another specialized agent (a "server agent").
*   **How it works:** This module implements a  **Agent-to-Agent (A2A) protocol**.
    1.  The "server agent" exposes an **Agent Card**, which is like a business card that describes its capabilities.
    2.  The "client agent" discovers this card and initiates a secure, token-based connection.
    3.  The client agent can then delegate complex tasks (like a Jira request) to the server agent, which in turn uses its own MCP connection to perform the work. This demonstrates a powerful, decentralized agent collaboration pattern.

---

###  6. Multi-Agent Flows with Google ADK (`multi-agent/`)
*   **What it is:** This folder contains advanced multi-agent patterns built with **Google's Agent Development Kit (ADK)**. It demonstrates how to orchestrate multiple, specialized sub-agents to accomplish complex tasks that a single agent cannot handle alone. Two primary patterns are showcased:
    *   **Router-based Agents:** A central "Router Agent" analyzes the user's request and dynamically delegates it to the most appropriate sub-agent (e.g., a Jira Agent, an Appointment Agent, or a Weather Agent).
    *   **Sequential Pipeline Agents:** A "Sequential Agent" executes a predefined chain of sub-agents in order, passing the output of one agent as the input to the next. This is perfect for multi-step workflows, like looking up a user's email before fetching their assigned tickets.
*   **How it works:**
    *   The **Router Agent** uses an LLM to understand the user's intent and select one or more sub-agents from a pool of available specialists. This allows for a flexible, natural language interface that can handle a wide variety of tasks.
    *   The **Sequential Agent** follows a fixed pipeline, ensuring that a series of operations is performed in the correct order to resolve a dependency. For example, it first runs an `Email Lookup Agent` and then passes the result to a `Jira Agent`.

---

## �📚 Table of Contents

- [Introduction](#introduction)
- [🔄 Complete Processing Flow](#-complete-processing-flow)
- [🚀 Quick Start](#-quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Set up OpenAI Key](#set-up-openai-key)
  - [Run AI Agent/MCP Client](#run-ai-agentmcp-client)
- [Sample Output UI](#sample-output-ui)
- [Sample Output CLI](#sample-output-cli)


# Introduction

A sophisticated Model Context Protocol (MCP) client that provides a **ui and command line based chat interface** with **privacy-first data redaction**. This client enables natural language queries to OpenAI LLM, which intelligently selects and orchestrates **multiple MCP server tool calls includes dynamic tool chaining** as needed, while ensuring **sensitive data never reaches external OpenAI LLMs** through redaction and reconstruction mechanisms.

The system demonstrates **intelligent tool chaining** where the LLM dynamically identifies dependencies between tools. For example, when a user provides only a `userId`, the LLM automatically:
1. **Recognizes the data dependency** - determines that an email address is needed for the target operation
2. **Orchestrates tool sequence** - first calls `get_email_id_from_user_id` to resolve the userId to an email
3. **Chains subsequent calls** - uses the retrieved email to call tools like `get_tickets_assigned_to_user`

This **autonomous tool orchestration** eliminates the need for users to understand internal data relationships or tool dependencies, enabling natural language queries like *"show jira tickets for user 1234"* to be automatically expanded into the correct sequence of tool calls.

## 🔄 Complete Processing Flow

When a user enters a query like *"Give me jira projects assigned to satish.k@test.com"*:

1. **Input Redaction**: Sensitive data (emails) replaced with tokens
2. **LLM Query Analysis**: Redacted query sent to OpenAI to identify required tools
3. **Tool Selection**: OpenAI response interpreted to select appropriate MCP tools
4. **Argument Reconstruction**: Original sensitive data restored for tool parameters
5. **Tool Execution**: MCP server tool invoked with real (unredacted) arguments
6. **Response Redaction**: MCP server response redacted before sending to LLM
7. **LLM Formatting**: Redacted data sent to OpenAI for response formatting
8. **LLM Response**: Structured response received with redacted tokens. **Repeat steps 3 to 7 , if response has tool disconvery**
9. **Response Reconstruction**: Original data restored in LLM-formatted response
10. **Final Delivery**: Complete, structured response with real data sent to user

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Required dependencies (see `requirements.txt`)

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
In .env file at the root of project configure your OPEN_API_KEY  
```
OPENAI_API_KEY=your_openai_api_key_here
```

### Run AI Agent/MCP Client 

Run the MCP client ui which automatically starts mcp server. 

```bash
python mcp_client_ui.py ./mcp_server.py
```

Run the MCP client cli which automatically starts mcp server. 

```bash
python mcp_client.py ./mcp_server.py
```


## Sample Output UI

When you run the UI version you'll see a graphical interface:

```bash
(ai-mcp) satish@Satishs-Air ai-mcp % python mcp_client_ui.py ./mcp_server.py


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
│    📦 Transport:       STDIO                                               │
│                                                                            │
│    📚 Docs:            https://gofastmcp.com                               │
│    🚀 Deploy:          https://fastmcp.cloud                               │
│                                                                            │
│    🏎️  FastMCP version: 2.11.0                                              │
│    🤝 MCP version:     1.12.3                                              │
│                                                                            │
╰────────────────────────────────────────────────────────────────────────────╯


[08/03/25 19:15:57] INFO     Starting MCP server 'jira MCP Server' with transport 'stdio'                                                                                                         server.py:1442

```

### Login Window
![Login Window](mcp_client_login.png)


### Chat Interface
![Chat Interface](mcp_client_chat.png)



## Sample Output CLI

```bash
(ai-mcp) satish@Satishs-Air ai-mcp % python mcp_client.py ./mcp_server.py


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
│    📦 Transport:       STDIO                                               │
│                                                                            │
│    📚 Docs:            https://gofastmcp.com                               │
│    🚀 Deploy:          https://fastmcp.cloud                               │
│                                                                            │
│    🏎️  FastMCP version: 2.11.0                                              │
│    🤝 MCP version:     1.12.3                                              │
│                                                                            │
╰────────────────────────────────────────────────────────────────────────────╯


[08/03/25 19:15:57] INFO     Starting MCP server 'jira MCP Server' with transport 'stdio'                                                                                                         server.py:1442

Connected to server with tools: ['get_tickets_assigned_to_user']

MCP Client Started!
Type your queries or 'quit' to exit.

**Query:** what is weather of BA state and tickets assigned to 1234 and give me in tabular format and include assignee emailId for each ticket



**user query:** what is weather of BA state and tickets assigned to 1234 and give me in tabular format and include assignee emailId for each ticket


**user query redacted:** what is weather of BA state and tickets assigned to 1234 and give me in tabular format and include assignee emailId for each ticket


INFO:mcp.server.lowlevel.server:Processing request of type ListToolsRequest
**sending user query to openapi llm to find if any mcp tool to use:** [{'role': 'user', 'content': 'what is weather of BA state and tickets assigned to 1234 and give me in tabular format and include assignee emailId for each ticket'}]


**Going to call these mcp tool:** [ChatCompletionMessageToolCall(id='call_pumEvAThH1bCoGZ3fOAn3StF', function=Function(arguments='{"state": "BA"}', name='get_alerts'), type='function'), ChatCompletionMessageToolCall(id='call_ub2uDhYG1rWEL0Bj3TsvTMAK', function=Function(arguments='{"user_id": "1234"}', name='get_email_id_from_user_id'), type='function')] 


**Processing tool call:** ChatCompletionMessageToolCall(id='call_pumEvAThH1bCoGZ3fOAn3StF', function=Function(arguments='{"state": "BA"}', name='get_alerts'), type='function')


**redacted input args:** {'state': 'BA'}


**reconstructed input args for sendint to mcp tool:** {'state': 'BA'}


INFO:mcp.server.lowlevel.server:Processing request of type CallToolRequest
**mcp tool response:** meta=None content=[TextContent(type='text', text='\nHeadline: Severe Thunderstorm Warning\nDescription: A severe thunderstorm is approaching your area. Take cover immediately.\nSeverity: Severe\n', annotations=None, meta=None)] structuredContent={'result': '\nHeadline: Severe Thunderstorm Warning\nDescription: A severe thunderstorm is approaching your area. Take cover immediately.\nSeverity: Severe\n'} isError=False


**mcp tool response redacted:** meta=None content=[TextContent(type='text', text='\nHeadline: Severe Thunderstorm Warning\nDescription: A severe thunderstorm is approaching your area. Take cover immediately.\nSeverity: Severe\n', annotations=None, meta=None, meta=None)] structuredContent={'result': '\nHeadline: Severe Thunderstorm Warning\nDescription: A severe thunderstorm is approaching your area. Take cover immediately.\nSeverity: Severe\n'} isError=False


**Processing tool call:** ChatCompletionMessageToolCall(id='call_ub2uDhYG1rWEL0Bj3TsvTMAK', function=Function(arguments='{"user_id": "1234"}', name='get_email_id_from_user_id'), type='function')


**redacted input args:** {'user_id': '1234'}


**reconstructed input args for sendint to mcp tool:** {'user_id': '1234'}


INFO:mcp.server.lowlevel.server:Processing request of type CallToolRequest
**mcp tool response:** meta=None content=[TextContent(type='text', text='satish.k@test.com', annotations=None, meta=None)] structuredContent={'result': 'satish.k@test.com'} isError=False


**mcp tool response redacted:** meta=None content=[TextContent(type='text', text='EAMIL_54b2079f', annotations=None, meta=None, meta=None)] structuredContent={'result': 'satish.k@test.com'} isError=False


**sending tools response to openapi llm:** [{'role': 'user', 'content': 'what is weather of BA state and tickets assigned to 1234 and give me in tabular format and include assignee emailId for each ticket'}, {'role': 'assistant', 'content': '', 'tool_calls': [ChatCompletionMessageToolCall(id='call_pumEvAThH1bCoGZ3fOAn3StF', function=Function(arguments='{"state": "BA"}', name='get_alerts'), type='function'), ChatCompletionMessageToolCall(id='call_ub2uDhYG1rWEL0Bj3TsvTMAK', function=Function(arguments='{"user_id": "1234"}', name='get_email_id_from_user_id'), type='function')]}, {'role': 'tool', 'name': 'get_alerts', 'content': [TextContent(type='text', text='\nHeadline: Severe Thunderstorm Warning\nDescription: A severe thunderstorm is approaching your area. Take cover immediately.\nSeverity: Severe\n', annotations=None, meta=None, meta=None)], 'tool_call_id': 'call_pumEvAThH1bCoGZ3fOAn3StF'}, {'role': 'tool', 'name': 'get_email_id_from_user_id', 'content': [TextContent(type='text', text='EAMIL_54b2079f', annotations=None, meta=None, meta=None)], 'tool_call_id': 'call_ub2uDhYG1rWEL0Bj3TsvTMAK'}]


**openai llm response:** ChatCompletion(id='chatcmpl-C2ji1qkiFMJ0XCYBQRx8bn9qGh8qk', choices=[Choice(finish_reason='tool_calls', index=0, logprobs=None, message=ChatCompletionMessage(content=None, refusal=None, role='assistant', annotations=[], audio=None, function_call=None, tool_calls=[ChatCompletionMessageToolCall(id='call_Bo08hGI7guf7kB8nA0wTp4St', function=Function(arguments='{"user_email":"EAMIL_54b2079f"}', name='get_tickets_assigned_to_user'), type='function')]))], created=1754768397, model='gpt-4-turbo-2024-04-09', object='chat.completion', service_tier='default', system_fingerprint='fp_de235176ee', usage=CompletionUsage(completion_tokens=25, prompt_tokens=339, total_tokens=364, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0)))


**Going to call these mcp tool:** [ChatCompletionMessageToolCall(id='call_Bo08hGI7guf7kB8nA0wTp4St', function=Function(arguments='{"user_email":"EAMIL_54b2079f"}', name='get_tickets_assigned_to_user'), type='function')] 


**Processing tool call:** ChatCompletionMessageToolCall(id='call_Bo08hGI7guf7kB8nA0wTp4St', function=Function(arguments='{"user_email":"EAMIL_54b2079f"}', name='get_tickets_assigned_to_user'), type='function')


**redacted input args:** {'user_email': 'EAMIL_54b2079f'}


**reconstructed input args for sendint to mcp tool:** {'user_email': 'satish.k@test.com'}


INFO:mcp.server.lowlevel.server:Processing request of type CallToolRequest
**mcp tool response:** meta=None content=[TextContent(type='text', text='[{"ticket_id":"PROJ-2024-001","summary":"Fix authentication vulnerability in user login system","description":"Critical security issue affecting user accounts","assignee":"satish.k@test.com","priority":"HIGH","status":"IN_PROGRESS"},{"ticket_id":"PROJ-2024-002","summary":"Update customer database schema for GDPR compliance","description":"Database contains PII that needs protection","assignee":"satish.k@test.com","priority":"MEDIUM","status":"OPEN"}]', annotations=None, meta=None)] structuredContent={'result': [{'ticket_id': 'PROJ-2024-001', 'summary': 'Fix authentication vulnerability in user login system', 'description': 'Critical security issue affecting user accounts', 'assignee': 'satish.k@test.com', 'priority': 'HIGH', 'status': 'IN_PROGRESS'}, {'ticket_id': 'PROJ-2024-002', 'summary': 'Update customer database schema for GDPR compliance', 'description': 'Database contains PII that needs protection', 'assignee': 'satish.k@test.com', 'priority': 'MEDIUM', 'status': 'OPEN'}]} isError=False


**mcp tool response redacted:** meta=None content=[TextContent(type='text', text='[{"ticket_id":"PROJ-2024-001","summary":"Fix authentication vulnerability in user login system","description":"Critical security issue affecting user accounts","assignee":"EAMIL_54b2079f","priority":"HIGH","status":"IN_PROGRESS"},{"ticket_id":"PROJ-2024-002","summary":"Update customer database schema for GDPR compliance","description":"Database contains PII that needs protection","assignee":"EAMIL_54b2079f","priority":"MEDIUM","status":"OPEN"}]', annotations=None, meta=None, meta=None)] structuredContent={'result': [{'ticket_id': 'PROJ-2024-001', 'summary': 'Fix authentication vulnerability in user login system', 'description': 'Critical security issue affecting user accounts', 'assignee': 'satish.k@test.com', 'priority': 'HIGH', 'status': 'IN_PROGRESS'}, {'ticket_id': 'PROJ-2024-002', 'summary': 'Update customer database schema for GDPR compliance', 'description': 'Database contains PII that needs protection', 'assignee': 'satish.k@test.com', 'priority': 'MEDIUM', 'status': 'OPEN'}]} isError=False


**sending tools response to openapi llm:** [{'role': 'user', 'content': 'what is weather of BA state and tickets assigned to 1234 and give me in tabular format and include assignee emailId for each ticket'}, {'role': 'assistant', 'content': '', 'tool_calls': [ChatCompletionMessageToolCall(id='call_pumEvAThH1bCoGZ3fOAn3StF', function=Function(arguments='{"state": "BA"}', name='get_alerts'), type='function'), ChatCompletionMessageToolCall(id='call_ub2uDhYG1rWEL0Bj3TsvTMAK', function=Function(arguments='{"user_id": "1234"}', name='get_email_id_from_user_id'), type='function')]}, {'role': 'tool', 'name': 'get_alerts', 'content': [TextContent(type='text', text='\nHeadline: Severe Thunderstorm Warning\nDescription: A severe thunderstorm is approaching your area. Take cover immediately.\nSeverity: Severe\n', annotations=None, meta=None, meta=None)], 'tool_call_id': 'call_pumEvAThH1bCoGZ3fOAn3StF'}, {'role': 'tool', 'name': 'get_email_id_from_user_id', 'content': [TextContent(type='text', text='EAMIL_54b2079f', annotations=None, meta=None, meta=None)], 'tool_call_id': 'call_ub2uDhYG1rWEL0Bj3TsvTMAK'}, {'role': 'assistant', 'content': '', 'tool_calls': [ChatCompletionMessageToolCall(id='call_Bo08hGI7guf7kB8nA0wTp4St', function=Function(arguments='{"user_email":"EAMIL_54b2079f"}', name='get_tickets_assigned_to_user'), type='function')]}, {'role': 'tool', 'name': 'get_tickets_assigned_to_user', 'content': [TextContent(type='text', text='[{"ticket_id":"PROJ-2024-001","summary":"Fix authentication vulnerability in user login system","description":"Critical security issue affecting user accounts","assignee":"EAMIL_54b2079f","priority":"HIGH","status":"IN_PROGRESS"},{"ticket_id":"PROJ-2024-002","summary":"Update customer database schema for GDPR compliance","description":"Database contains PII that needs protection","assignee":"EAMIL_54b2079f","priority":"MEDIUM","status":"OPEN"}]', annotations=None, meta=None, meta=None)], 'tool_call_id': 'call_Bo08hGI7guf7kB8nA0wTp4St'}]


**openai llm response:** ChatCompletion(id='chatcmpl-C2ji2UqgnJNR9VxbUrlvxt1vsFnmQ', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='### Weather Alert for BA State\n- **Headline**: Severe Thunderstorm Warning\n- **Description**: A severe thunderstorm is approaching your area. Take cover immediately.\n- **Severity**: Severe\n\n### Tickets Assigned to User (EAMIL_54b2079f)\n\n| Ticket ID        | Summary                                             | Description                                       | Assignee Email ID | Priority | Status       |\n|------------------|-----------------------------------------------------|---------------------------------------------------|-------------------|----------|--------------|\n| PROJ-2024-001    | Fix authentication vulnerability in user login system | Critical security issue affecting user accounts   | EAMIL_54b2079f    | HIGH     | IN_PROGRESS |\n| PROJ-2024-002    | Update customer database schema for GDPR compliance | Database contains PII that needs protection       | EAMIL_54b2079f    | MEDIUM   | OPEN        |', refusal=None, role='assistant', annotations=[], audio=None, function_call=None, tool_calls=None))], created=1754768398, model='gpt-4-turbo-2024-04-09', object='chat.completion', service_tier='default', system_fingerprint='fp_de235176ee', usage=CompletionUsage(completion_tokens=182, prompt_tokens=481, total_tokens=663, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0)))


**Final Response:** 
[Calling tool get_alerts with args {'state': 'BA'}]
[Calling tool get_email_id_from_user_id with args {'user_id': '1234'}]
[Calling tool get_tickets_assigned_to_user with args {'user_email': 'satish.k@test.com'}]
### Weather Alert for BA State
- **Headline**: Severe Thunderstorm Warning
- **Description**: A severe thunderstorm is approaching your area. Take cover immediately.
- **Severity**: Severe

### Tickets Assigned to User (satish.k@test.com)

| Ticket ID        | Summary                                             | Description                                       | Assignee Email ID | Priority | Status       |
|------------------|-----------------------------------------------------|---------------------------------------------------|-------------------|----------|--------------|
| PROJ-2024-001    | Fix authentication vulnerability in user login system | Critical security issue affecting user accounts   | satish.k@test.com    | HIGH     | IN_PROGRESS |
| PROJ-2024-002    | Update customer database schema for GDPR compliance | Database contains PII that needs protection       | satish.k@test.com    | MEDIUM   | OPEN        |

Please take the necessary precautions for the approaching severe weather.
```

