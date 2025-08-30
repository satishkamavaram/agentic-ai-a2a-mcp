from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset,StreamableHTTPConnectionParams

class JiraAgent:
   
    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']

    def __init__(self):
        self._agent = self._build_agent()
        self._user_id = 'jira_remote_agent'
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
            instruction="You are a Jira assistant agent. You can fetch Jira tickets assigned to a user by email and retrieve email IDs for given user IDs. Answer user queries about Jira tickets and user emails using the available tools. You can create appointments",
            #tools=[get_tickets_assigned_to_user, get_email_id_from_user_id],
            tools=[MCPToolset(
                            connection_params=StreamableHTTPConnectionParams(
                                url="http://localhost:8000/mcp",
                                headers={"Authorization": f"Bearer satish-token"}
                            ),
                        )],
        )
        print(f"Building jira agent: {agent.name}")
        return agent