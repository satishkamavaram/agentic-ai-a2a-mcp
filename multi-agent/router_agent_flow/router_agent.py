
from google.adk.agents import SequentialAgent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from model_callbacks import simple_before_model_modifier
import asyncio
from google.genai import types
from jira_agent import (
    JiraAgent,
    get_email_id_from_user_id,
)
from appointment_agent import (
    AppointmentAgent,
)
from weather_agent import (
    WeatherAgent,
)

APP_NAME = "sequential_pipeline_agent"
USER_ID = "1234"
SESSION_ID = "session1234"


jira_agent = JiraAgent().get_agent()
appointment_agent = AppointmentAgent().get_agent()
weather_agent = WeatherAgent().get_agent()

from datetime import date
today = date.today().strftime("%B %d, %Y")

router_agent = LlmAgent(
            model=LiteLlm(model="openai/gpt-4-turbo"), # Using ChatGPT model
            name="router_agent",
            instruction="""You are a router agent. Your purpose is to route user queries to the appropriate sub-agent.
           
            Route user requests: 
            user jira_agent for jira related queries
            user appointment_agent for appointment related queries
            user weather_agent for weather related queries
            """,
            sub_agents=[jira_agent,appointment_agent,weather_agent],
            #tools=[MCPToolset(
            #                connection_params=StreamableHTTPConnectionParams(
            #                    url="http://localhost:8000/mcp",
            #                    headers={"Authorization": f"Bearer satish-token"}
             #               ),
            #            )],
            output_key="jira_key",
            before_model_callback=simple_before_model_modifier,
            description="Main router agent",
        )
       


async def main():
    session_service = InMemorySessionService()
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=router_agent, app_name=APP_NAME, session_service=session_service)

    def call_agent(query):
        contextual_query = f"Current date is {today}. {query}"

        content = types.Content(role='user', parts=[types.Part(text=contextual_query)])
        events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
        for event in events:
            print(f"****************************************************")
            print(f"\\nDEBUG EVENT: {event}")
            if event.is_final_response() and event.content:
                final_answer = event.content.parts[0].text.strip()
                print(f":::::::::::::::::::::::::::::::::::::::::::::::::::")
                print(f"FINAL ANSWER : {final_answer}")

    call_agent("schedule a appointment next week tuesday morning 4:30 from email satish.k@test.com and to these users test1@test.com test2@test.com to discuss about future of agentic AI")
    #call_agent("schedule a appointment on 4th sept 2026 at 4:30 am  from email satish.k@test.com and to these users test1@test.com test2@test.com to discuss about future of agentic AI")
    #call_agent("schedule a meeting invite with test1@test.com test2@test.com on 4th sept 2026 at 4:30 am  from email satish.k@test.com to discuss about future of agentic AI")
    call_agent("jira tickets assigned to 1234 and give count and my emailId")
    call_agent("weather info of BA state")
    

if __name__ == "__main__":
    asyncio.run(main())