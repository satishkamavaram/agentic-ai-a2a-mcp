from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset,StreamableHTTPConnectionParams
from model_callbacks import simple_before_model_modifier

async def get_weather_alerts(state: str) -> str:
    """Get weather alerts for a German state.

    Args:
        state: Two-letter German state code (e.g. BW, BY)
    """
   
    data = {
        "features": [
            {
                "id": "1",
                "type": "Alert",
                "properties": {
                    "headline": "Severe Thunderstorm Warning",
                    "description": "A severe thunderstorm is approaching your area. Take cover immediately.",
                    "severity": "Severe",
                    "effective": "2024-10-01T14:00:00Z",
                    "expires": "2024-10-01T15:00:00Z"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [-120.0, 37.0]
                }
            }
        ]
    }
    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)



def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Headline: {props.get('headline', 'Unknown')}
Description: {props.get('description', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
"""


class WeatherAgent:
   
    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']

    def __init__(self):
        self._agent = self._build_agent()
        self._user_id = 'weather_agent'
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
            name="weather_agent",
            instruction="You are a weather alert assistant. Your purpose is to identify locations in queries and automatically fetch their weather alerts.",
            tools=[get_weather_alerts],
            #tools=[MCPToolset(
            #                connection_params=StreamableHTTPConnectionParams(
            #                    url="http://localhost:8000/mcp",
            #                    headers={"Authorization": f"Bearer satish-token"}
             #               ),
            #            )],
            output_key="weather_alerts_key",
            before_model_callback=simple_before_model_modifier,
        )
        print(f"Building weather agent: {agent.name}")
        return agent
    
    def get_agent(self) -> LlmAgent:
        return self._agent
    

