from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset,StreamableHTTPConnectionParams
from model_callbacks import simple_before_model_modifier


def get_tickets_assigned_to_user(user_email: str) -> list:
   
    """Get tickets assigned to a user from jira using emailId.

    Args:
        user_email: email of the user to get tickets assigned to user
    
        
    Returns:
        A list of tickets assigned to the user in JSON format (with sensitive data redacted)
    """
    print(f"Access token in get_tickets_assigned_to_user")
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


class JiraAgent:
   
    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']

    def __init__(self):
        self._agent = self._build_agent()
        self._user_id = 'jira_agent'
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    def get_runner(self) -> Runner:
        return self._runner

    def _build_agent(self) -> LlmAgent:
        agent = LlmAgent(
            model=LiteLlm(model="openai/gpt-4-turbo"), # Using ChatGPT model
            name="jira_agent",
            instruction="You are a Jira assistant agent. You can fetch Jira tickets assigned to a user by email. Answer user queries about Jira tickets and user emails using the available tools. You can create appointments",
            tools=[get_tickets_assigned_to_user],
            #tools=[MCPToolset(
            #                connection_params=StreamableHTTPConnectionParams(
            #                    url="http://localhost:8000/mcp",
            #                    headers={"Authorization": f"Bearer satish-token"}
             #               ),
            #            )],
            output_key="jira_key",
            before_model_callback=simple_before_model_modifier,
        )
        print(f"Building jira agent: {agent.name}")
        return agent
    
    def get_agent(self) -> LlmAgent:
        return self._agent