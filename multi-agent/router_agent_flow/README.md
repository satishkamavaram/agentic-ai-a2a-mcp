> **⚠️ POC DISCLAIMER: This is a Proof of Concept (POC) implementation. Please do not evaluate this code for production-level code structure, modularity, or best practices. This project is designed for educational and demonstration purposes only.**

## 📚 Table of Contents

- [Introduction](#introduction)
- [How It Works](#how-it-works)
- [🚀 Quick Start](#-quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Set up OpenAI Key](#set-up-openai-key)
  - [Run Router Agent](#run-router-agent)
  - [Sample Queries](#sample-queries)


# Introduction

This project demonstrates a multi-agent orchestration pattern using the Google ADK library, where a **Router LLM Agent** dynamically decides which specialized sub-agent(s) to invoke based on the user's query.

The router agent uses an LLM (e.g., ChatGPT Turbo) to interpret the user's intent and route the request to one or more sub-agents:

- **Jira Agent**: Handles Jira-related queries (e.g., ticket lookup, user info)
- **Appointment Agent**: Handles invite scheduling
- **Weather Agent**: Handles weather and alert queries

Each sub-agent exposes its own tools to execute domain-specific actions. The router agent enables natural language queries like "schedule a meeting next week" or "show my Jira tickets" and automatically delegates to the correct agent(s) without the user needing to know which agent to call.

This pattern demonstrates:
- How to use Google ADK's LlmAgent with sub-agents for routing
- How to build a modular, extensible multi-agent system
- How to provide a single natural language interface for multiple domains

---

## How It Works

1. The user enters a query (e.g., "schedule a meeting next week with Alice and Bob").
2. The router LLM agent analyzes the query and determines which sub-agent(s) are relevant.
3. The router agent forwards the query to the appropriate sub-agent(s).
4. The sub-agent executes its tools and returns a response.
5. The router agent returns the final answer to the user.

---


## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Required dependencies (see `requirements.txt`)

### Installation 

```bash
# Clone or navigate to the project directory
cd $HOME/ai-mcp/multi-agent/router_agent_flow

# install with pip
python3 -m venv ai-multi-agent
source ai-multi-agent/bin/activate
pip install -r ../requirements.txt

```

### Set up OpenAI Key
In .env file at the root of project or in this level configure your OPEN_API_KEY and OPENAI_API_BASE
```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
```

### Run router agent

```bash
python3 router_agent.py
```

**sample queries**:
- schedule a appointment on 4th sept 2026 at 4:30 am  from email satish.k@test.com and to these users test1@test.com test2@test.com to discuss about future of agentic AI
- jira tickets assigned to 1234
- weather info of BA state

***user query and output***
```
User Query: schedule a appointment next week tuesday morning 4:30 from email satish.k@test.com and to these users test1@test.com test2@test.com to discuss about future of agentic AI

FINAL ANSWER : The appointment to discuss the future of agentic AI has been successfully scheduled for September 9, 2025, at 4:30 AM. The attendees are test1@test.com and test2@test.com, and the organizer's email is satish.k@test.com.

User Query:  weather info of BA state

FINAL ANSWER : The current weather alert for BA (Bavaria) state includes a severe thunderstorm warning. You are advised to take cover immediately. The severity of this weather condition is marked as severe.

```