# reference : https://google.github.io/adk-docs/agents/llm-agents/

import asyncio

from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset,StreamableHTTPConnectionParams
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from typing import Optional

APP_NAME = "jira_app"
USER_ID = "1234"
SESSION_ID = "session1234"

def get_tickets_assigned_to_user(user_email: str) -> list:
   
    """Get tickets assigned to a user from jira using emailId.

    Args:
        user_email: email of the user to get tickets assigned to user
    
        
    Returns:
        A list of tickets assigned to the user in JSON format (with sensitive data redacted)
    """
    
    real_tickets = [
        {
            "ticket_id": "PROJ-2024-001", 
            "summary": "Fix authentication vulnerability in user login system",
            "description": "Critical security issue affecting user accounts",
            "assignee": user_email,
            "priority": "HIGH",
            "status": "IN_PROGRESS"
        },
        {
            "ticket_id": "PROJ-2024-002", 
            "summary": "Update customer database schema for GDPR compliance",
            "description": "Database contains PII that needs protection",
            "assignee": user_email,
            "priority": "MEDIUM",
            "status": "OPEN"
        },
    ]
    
    return real_tickets


def get_email_id_from_user_id(user_id: str) -> str:
   
    """Get email ID from user ID input.

    Args:
        user_id: User ID to get email for
    
    Returns:
        Email ID of the user
    """
    user_email_map = {
        "user123": "user123@test.com",
        "user456": "user456@test.com"
    }
    return user_email_map.get(user_id, "satish.k@test.com")

def simple_before_model_modifier(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    agent_name = callback_context.agent_name
    print(f"[Callback] Before model call for agent: {agent_name}")

    # Inspect the last user message in the request contents
    last_user_message = ""
    if llm_request.contents and llm_request.contents[-1].role == 'user':
         if llm_request.contents[-1].parts:
            last_user_message = llm_request.contents[-1].parts[0].text
    print(f"[Callback] Inspecting last user message: '{last_user_message}'")
    return None

def simple_after_model_modifier(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    agent_name = callback_context.agent_name
    print(f"[Callback] After model call for agent: {agent_name}")
    original_text = ""
    if llm_response.content and llm_response.content.parts:
        if llm_response.content.parts[0].text:
            original_text = llm_response.content.parts[0].text
            print(f"[Callback] Inspected original response text: '{original_text[:100]}...'") # Log snippet
        elif llm_response.content.parts[0].function_call:
             print(f"[Callback] Inspected response: Contains function call '{llm_response.content.parts[0].function_call.name}'. No text modification.")
             return None # Don't modify tool calls in this example
        else:
             print("[Callback] Inspected response: No text content found.")
             return None
    elif llm_response.error_message:
        print(f"[Callback] Inspected response: Contains error '{llm_response.error_message}'. No modification.")
        return None
    else:
        print("[Callback] Inspected response: Empty LlmResponse.")
        return None 
    
agent = LlmAgent(
    model=LiteLlm(model="openai/gpt-4-turbo"), # Using ChatGPT model
    name="jira_agent",
    instruction="You are a Jira assistant agent. You can fetch Jira tickets assigned to a user by email and retrieve email IDs for given user IDs. Answer user queries about Jira tickets and user emails using the available tools.",
   # planner=planner,
    #tools=[get_tickets_assigned_to_user, get_email_id_from_user_id],
    tools=[MCPToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="http://localhost:8000/mcp",
                        headers={"Authorization": "Bearer satish-token"}
                    ),
                )],
    before_model_callback=simple_before_model_modifier,
    after_model_callback=simple_after_model_modifier
)

async def main():
    session_service = InMemorySessionService()
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)

    def call_agent(query):
        content = types.Content(role='user', parts=[types.Part(text=query)])
        events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
        for event in events:
            print(f"\\nDEBUG EVENT: {event}")
            if event.is_final_response() and event.content:
                final_answer = event.content.parts[0].text.strip()
                print(f"FINAL ANSWER : {final_answer}")

    call_agent("jira tickets assigned to 1234")
    #call_agent("weather info nw state")


if __name__ == "__main__":
    asyncio.run(main())