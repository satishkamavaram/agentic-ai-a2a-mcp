
from google.adk.agents import SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
import asyncio
from google.genai import types
from jira_agent import (
    JiraAgent,
)
from email_lookup_agent import (
    EmailLookupAgent,
)


APP_NAME = "sequential_pipeline_agent"
USER_ID = "1234"
SESSION_ID = "session1234"


jira_agent = JiraAgent().get_agent()
email_lookup_agent = EmailLookupAgent().get_agent()


code_pipeline_agent = SequentialAgent(
    name="sequentialPipelineAgent",
    sub_agents=[email_lookup_agent,jira_agent],
    description="Executes a sequence of email_lookup_agent and jira_agent related tasks.",
)


async def main():
    session_service = InMemorySessionService()
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=code_pipeline_agent, app_name=APP_NAME, session_service=session_service)

    def call_agent(query):
        content = types.Content(role='user', parts=[types.Part(text=query)])
        events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
        for event in events:
            print(f"****************************************************")
            print(f"\\nDEBUG EVENT: {event}")
            if event.is_final_response() and event.content:
                final_answer = event.content.parts[0].text.strip()
                print(f":::::::::::::::::::::::::::::::::::::::::::::::::::")
                print(f"FINAL ANSWER : {final_answer}")

    #call_agent("schedule a appointment on 4th sept 2026 at 4:30 am  from email satish.k@test.com and to these users test1@test.com test2@test.com to discuss about future of agentic AI")
    call_agent("jira tickets assigned to 1234 and give count and my emailId")

if __name__ == "__main__":
    asyncio.run(main())