# Introduction

A sophisticated Model Context Protocol (MCP) client that provides an **command line basedchat interface** with **privacy-first data redaction**. This client enables natural language queries to LLM and MCP server while ensuring **sensitive data never reaches external OPENAI LLMs** through redaction and reconstruction mechanisms.

### 🔐 Privacy-First Architecture

This client implements a **sophisticated data redaction and reconstruction flow** to ensure sensitive information never leaves your environment:

```
User Query → User Query Redaction → Invoke OpenAI LLM → Check MCP Tool Selection from OpenAI LLM response → 
Argument Reconstruction for tool → Invoke selected tool(MCP Server) → Tool(MCP Server) Response -> Tool(MCP Server) Response Redaction → 
Invoke OpenAI LLM → LLM response Reconstruction for user → Send User Response
```

### 🔄 Complete Processing Flow

When a user enters a query like *"Give me jira projects assigned to john@company.com"*:

1. **🛡️ Input Redaction**: Sensitive data (emails) replaced with tokens
2. **🤖 LLM Query Analysis**: Redacted query sent to OpenAI to identify required tools
3. **🔍 Tool Selection**: OpenAI response interpreted to select appropriate MCP tools
4. **🔧 Argument Reconstruction**: Original sensitive data restored for tool parameters
5. **⚡ Tool Execution**: MCP server tool invoked with real (unredacted) arguments
6. **🛡️ Response Redaction**: MCP server response redacted before sending to LLM
7. **🤖 LLM Formatting**: Redacted data sent to OpenAI for response formatting
8. **📨 LLM Response**: Structured response received with redacted tokens
9. **🔧 Response Reconstruction**: Original data restored in LLM-formatted response
10. **✅ Final Delivery**: Complete, structured response with real data sent to user

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Required dependencies (see `requirements.txt`)

### Installation 

```bash
# Clone or navigate to the project directory
cd $HOME$/ai-mcp

# install with pip
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt

```

### Pre-requisite
Create a .env file at the root of project with below line and configure your OPEN_API_KEY  
```
OPENAI_API_KEY=<<OPENAI_API_KEY>>
```

### Run AI Agent/MCP Client 

Run the MCP client which automatically starts mcp server. 

```bash
python mcp_client.py $HOME/ai-mcp/mcp_server.py
```

## 📁 Project Structure

```
mcp-client/
├── mcp_client.py      # Main MCP client implementation
├── mcp_server.py      # MCP server implementation with dummy jira projects
├── requirements.txt   # python dependencies
└── README.md          # This file
```

## 🔧 Modules

### MCP Client (`mcp_client.py`)

The client acts as an **intelligent Agentic AI chat interface** that:
- **Starts the MCP server** automatically when launched
- **Connects to OpenAI LLM** for natural language understanding
- **Provides interactive CLI chat** for user queries
- **Translates natural language** to MCP tool calls
- **Formats responses** in human-readable structure
- **Handles complex queries** like "show me jira projects for user@email.com"

### MCP Server (`mcp_server.py`)

The server component that:
- **Exposes dummy business logic jira tool**
- **Handles tool execution** with proper parameters
- **Returns structured data** to the client
- **Provides dummy/mock data** for development and testing

## Sample Output

```bash
(ai-mcp) satish@Satishs-Air ai-mcp % python mcp_client.py /Users/satish/work/Learning/ai-mcp/mcp_server.py


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

**Query**: please give jira projects assigned to me satish.k@test.com and give in tabular format the jira projects



**user query**: please give jira projects assigned to me satish.k@test.com and give in tabular format the jira projects


**user query redacted**: please give jira projects assigned to me EAMIL_54b2079f and give in tabular format the jira projects


**sending user query to openapi llm to find if any mcp tool to use**: [{'role': 'user', 'content': 'please give jira projects assigned to me EAMIL_54b2079f and give in tabular format the jira projects'}]


**openai llm response**: ChatCompletion(id='chatcmpl-C0Wbvqm1LZGkLf2uhGPKuH25I1FI1', choices=[Choice(finish_reason='tool_calls', index=0, logprobs=None, message=ChatCompletionMessage(content=None, refusal=None, role='assistant', annotations=[], audio=None, function_call=None, tool_calls=[ChatCompletionMessageToolCall(id='call_vLhOXlI8kIayybUaCJMw2azZ', function=Function(arguments='{"user_email":"EAMIL_54b2079f"}', name='get_tickets_assigned_to_user'), type='function')]))], created=1754241391, model='gpt-4-turbo-2024-04-09', object='chat.completion', service_tier='default', system_fingerprint='fp_de235176ee', usage=CompletionUsage(completion_tokens=25, prompt_tokens=126, total_tokens=151, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))) 


**Calling mcp tool**: [ChatCompletionMessageToolCall(id='call_vLhOXlI8kIayybUaCJMw2azZ', function=Function(arguments='{"user_email":"EAMIL_54b2079f"}', name='get_tickets_assigned_to_user'), type='function')] 


**Processing tool call**: ChatCompletionMessageToolCall(id='call_vLhOXlI8kIayybUaCJMw2azZ', function=Function(arguments='{"user_email":"EAMIL_54b2079f"}', name='get_tickets_assigned_to_user'), type='function')


**redacted input args**: {'user_email': 'EAMIL_54b2079f'}


**reconstructed input args for sendint to mcp tool**: {'user_email': 'satish.k@test.com'}


**mcp tool response**: meta=None content=[TextContent(type='text', text='[{"ticket_id":"PROJ-2024-001","summary":"Fix authentication vulnerability in user login system","description":"Critical security issue affecting user accounts","assignee":"satish.k@test.com","priority":"HIGH","status":"IN_PROGRESS"},{"ticket_id":"PROJ-2024-002","summary":"Update customer database schema for GDPR compliance","description":"Database contains PII that needs protection","assignee":"satish.k@test.com","priority":"MEDIUM","status":"OPEN"}]', annotations=None, meta=None)] structuredContent={'result': [{'ticket_id': 'PROJ-2024-001', 'summary': 'Fix authentication vulnerability in user login system', 'description': 'Critical security issue affecting user accounts', 'assignee': 'satish.k@test.com', 'priority': 'HIGH', 'status': 'IN_PROGRESS'}, {'ticket_id': 'PROJ-2024-002', 'summary': 'Update customer database schema for GDPR compliance', 'description': 'Database contains PII that needs protection', 'assignee': 'satish.k@test.com', 'priority': 'MEDIUM', 'status': 'OPEN'}]} isError=False


**mcp tool response redacted**: meta=None content=[TextContent(type='text', text='[{"ticket_id":"PROJ-2024-001","summary":"Fix authentication vulnerability in user login system","description":"Critical security issue affecting user accounts","assignee":"EAMIL_54b2079f","priority":"HIGH","status":"IN_PROGRESS"},{"ticket_id":"PROJ-2024-002","summary":"Update customer database schema for GDPR compliance","description":"Database contains PII that needs protection","assignee":"EAMIL_54b2079f","priority":"MEDIUM","status":"OPEN"}]', annotations=None, meta=None, meta=None)] structuredContent={'result': [{'ticket_id': 'PROJ-2024-001', 'summary': 'Fix authentication vulnerability in user login system', 'description': 'Critical security issue affecting user accounts', 'assignee': 'satish.k@test.com', 'priority': 'HIGH', 'status': 'IN_PROGRESS'}, {'ticket_id': 'PROJ-2024-002', 'summary': 'Update customer database schema for GDPR compliance', 'description': 'Database contains PII that needs protection', 'assignee': 'satish.k@test.com', 'priority': 'MEDIUM', 'status': 'OPEN'}]} isError=False


**sending tool response to openapi llm** [{'role': 'user', 'content': 'please give jira projects assigned to me EAMIL_54b2079f and give in tabular format the jira projects'}, {'role': 'assistant', 'content': '', 'tool_calls': [ChatCompletionMessageToolCall(id='call_vLhOXlI8kIayybUaCJMw2azZ', function=Function(arguments='{"user_email":"EAMIL_54b2079f"}', name='get_tickets_assigned_to_user'), type='function')]}, {'role': 'tool', 'name': 'get_tickets_assigned_to_user', 'content': [TextContent(type='text', text='[{"ticket_id":"PROJ-2024-001","summary":"Fix authentication vulnerability in user login system","description":"Critical security issue affecting user accounts","assignee":"EAMIL_54b2079f","priority":"HIGH","status":"IN_PROGRESS"},{"ticket_id":"PROJ-2024-002","summary":"Update customer database schema for GDPR compliance","description":"Database contains PII that needs protection","assignee":"EAMIL_54b2079f","priority":"MEDIUM","status":"OPEN"}]', annotations=None, meta=None, meta=None)], 'tool_call_id': 'call_vLhOXlI8kIayybUaCJMw2azZ'}]


**openai llm response**: ChatCompletion(id='chatcmpl-C0WbwcGJhiYnVoNk5FEcVAByl2t06', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='Here are the Jira projects assigned to the user email "EAMIL_54b2079f" in a tabular format:\n\n| Ticket ID       | Summary                                         | Description                             | Assignee        | Priority | Status       |\n|-----------------|-------------------------------------------------|-----------------------------------------|-----------------|----------|--------------|\n| PROJ-2024-001   | Fix authentication vulnerability in user login  | Critical security issue affecting user  | EAMIL_54b2079f  | HIGH     | IN_PROGRESS  |\n|                 | system                                          | accounts                                |                 |          |              |\n| PROJ-2024-002   | Update customer database schema for GDPR        | Database contains PII that needs        | EAMIL_54b2079f  | MEDIUM   | OPEN         |\n|                 | compliance                                      | protection                              |                 |          |              |\n\nThese projects are currently assigned and tackle important issues ranging from security to GDPR compliance.', refusal=None, role='assistant', annotations=[], audio=None, function_call=None, tool_calls=None))], created=1754241392, model='gpt-4-turbo-2024-04-09', object='chat.completion', service_tier='default', system_fingerprint='fp_de235176ee', usage=CompletionUsage(completion_tokens=196, prompt_tokens=268, total_tokens=464, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0)))


**Final Response to User**
[Calling tool get_tickets_assigned_to_user with args {'user_email': 'satish.k@test.com'}]
Here are the Jira projects assigned to the user email "satish.k@test.com" in a tabular format:

| Ticket ID       | Summary                                         | Description                             | Assignee        | Priority | Status       |
|-----------------|-------------------------------------------------|-----------------------------------------|-----------------|----------|--------------|
| PROJ-2024-001   | Fix authentication vulnerability in user login  | Critical security issue affecting user  | satish.k@test.com  | HIGH     | IN_PROGRESS  |
|                 | system                                          | accounts                                |                 |          |              |
| PROJ-2024-002   | Update customer database schema for GDPR        | Database contains PII that needs        | satish.k@test.com  | MEDIUM   | OPEN         |
|                 | compliance                                      | protection                              |                 |          |              |

These projects are currently assigned and tackle important issues ranging from security to GDPR compliance.
```
