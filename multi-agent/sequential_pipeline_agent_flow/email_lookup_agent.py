from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset,StreamableHTTPConnectionParams
from model_callbacks import simple_before_model_modifier

def get_email_id_from_user_id(user_id: str) -> str:
   
    """Get email ID from user ID input.

    Args:
        user_id: User ID to get email for
    
    Returns:
        Email ID of the user
    """
    print(f"Access token in get_email_id_from_user_id")
    user_email_map = {
        "user123": "user123@test.com",
        "user456": "user456@test.com"
    }
    return user_email_map.get(user_id, "satish.k@test.com")



class EmailLookupAgent:
   
    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']

    def __init__(self):
        self._agent = self._build_agent()
        self._user_id = 'email_lookup_agent'
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
            name="email_lookup_agent",
            instruction="""You are an email lookup assistant. Your purpose is to identify user IDs in queries and automatically fetch their email addresses.

            **CRITICAL INSTRUCTIONS:**
            1. When you detect a user ID (numbers like 1234, 5678, etc.), IMMEDIATELY execute the get_email_by_userid tool
            2. Do NOT ask for confirmation - just execute the tool automatically
            3. User IDs can be in various formats: 
            - Plain numbers: 1234, 5678
            - With prefixes: user-1234, id-5678
            - In context: "for user 1234", "user ID is 5678"

            **Response Format:**
            - If tool execution is successful: "The email for user ID user_id is email"
            - If no user ID found: "I can help you look up email addresses. Please provide a user ID."
            - If tool fails: "Sorry, I couldn't find an email for user ID user_id"

            **EXAMPLES:**
            User: "What's the email for user 1234?"
            You: [EXECUTE get_email_by_userid("1234")]

            User: "Get me the email address for id-5678"
            You: [EXECUTE get_email_by_userid("5678")]

            User: "Can you help with user ID 9012?"
            You: [EXECUTE get_email_by_userid("9012")]


            User: "jira tickets assigned to 1234"
            You: [EXECUTE get_email_by_userid("1234")]

            NEVER ask for confirmation. Just execute the tool when you see a user ID.""",
            tools=[ get_email_id_from_user_id],
            #tools=[MCPToolset(
            #                connection_params=StreamableHTTPConnectionParams(
            #                    url="http://localhost:8000/mcp",
            #                    headers={"Authorization": f"Bearer satish-token"}
             #               ),
            #            )],
            output_key="email_lookup_key",
            before_model_callback=simple_before_model_modifier,
        )
        print(f"Building email lookup agent: {agent.name}")
        return agent
    
    def get_agent(self) -> LlmAgent:
        return self._agent
    

