> **⚠️ POC DISCLAIMER: This is a Proof of Concept (POC) implementation. Please do not evaluate this code for production-level code structure, modularity, or best practices. This project is designed for educational and demonstration purposes only.**

## 📚 Table of Contents

- [Introduction](#introduction)
- [How It Works](#how-it-works)
- [🚀 Quick Start](#-quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Set up OpenAI Key](#set-up-openai-key)
  - [Run Sequential Agent Pipeline](#run-sequential-agent-pipeline)
  - [Sample Queries](#sample-queries)


# Introduction

This project demonstrates a **sequential multi-agent pipeline** using the Google ADK library, where a **SequentialAgent** runs a series of sub-agents one after another, carrying forward context/results from each step.

For example, if a user asks "jira tickets assigned to 1234", the pipeline will:
- First, use an **Email Lookup Agent** to resolve the user ID (`1234`) to an email address.
- Then, pass the email to the **Jira Agent** to fetch tickets assigned to that email.

The user only needs to provide a high-level query (like a user ID), and the pipeline handles all intermediate steps and data passing between agents.

This pattern demonstrates:
- How to use Google ADK's SequentialAgent to chain multiple agents
- How to build a pipeline where each agent's output becomes the next agent's input
- How to provide a natural language interface for multi-step workflows

---

## How It Works

1. The user enters a query (e.g., "jira tickets assigned to 1234").
2. The sequential agent pipeline first runs the Email Lookup Agent to get the email for user ID 1234.
3. The pipeline then runs the Jira Agent, passing the resolved email as input.
4. The final answer is returned to the user.

---


## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Required dependencies (see `requirements.txt`)

### Installation 

```bash
# Clone or navigate to the project directory
cd $HOME/ai-mcp/multi-agent/sequential_pipeline_agent_flow

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

### Run sequential agent pipeline flow

```bash
python3 sequential_agent.py
```

**sample queries**:
- jira tickets assigned to 1234

***user query and output***
```
User Query:  jira tickets assigned to 1234

FINAL ANSWER : Satish Kumar has two Jira tickets assigned to him:

1. **Ticket ID:** PROJ-2024-001
   - **Summary:** Fix authentication vulnerability in user login system
   - **Description:** Critical security issue affecting user accounts
   - **Priority:** HIGH
   - **Status:** IN PROGRESS

2. **Ticket ID:** PROJ-2024-002
   - **Summary:** Update customer database schema for GDPR compliance
   - **Description:** Database contains PII that needs protection
   - **Priority:** MEDIUM
   - **Status:** OPEN

The count of assigned Jira tickets is 2.

```