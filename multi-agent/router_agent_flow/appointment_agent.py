from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset,StreamableHTTPConnectionParams
from model_callbacks import simple_before_model_modifier
from typing import List


from typing import List
from pydantic import BaseModel, Field

class AppointmentRequest(BaseModel):
    """
    Simple model for creating an appointment with clear field descriptions.
    """
    to_emails: List[str] = Field(
        ...,
        description="List of email addresses for all meeting attendees. Example: ['user1@example.com', 'user2@example.com']"
    )
    
    from_email: str = Field(
        ...,
        description="Email address of the meeting organizer. Example: 'organizer@example.com'"
    )
    
    subject: str = Field(
        ...,
        description="Title or subject of the appointment. Example: 'Team Meeting'"
    )
    
    date: str = Field(
        ...,
        description="Date of the appointment in YYYY-MM-DD format. Always include 4-digit year. Example: '2025-09-01'"
    )
    
    time: str = Field(
        ...,
        description="Time of the appointment in HH:MM 24-hour format. Example: '14:30' for 2:30 PM"
    )

def create_appointment_pydantic(appointment: AppointmentRequest) -> dict:
    """
    Create an appointment and return confirmation details.
    
    This function takes appointment details in a structured format and creates
    a calendar appointment with a unique ID.
    
    Args:
        appointment: AppointmentRequest object containing all necessary details
        
    Returns:
        dict: Confirmation details including appointment ID and all information
        
    Example:
        >>> request = AppointmentRequest(
        >>>     to_emails=["test1@test.com", "test2@test.com"],
        >>>     from_email="satish.k@test.com",
        >>>     subject="Team Sync",
        >>>     date="2025-09-01",
        >>>     time="14:30"
        >>> )
        >>> create_appointment(request)
    """
    appointment_details = {
        "to": appointment.to_emails,
        "from": appointment.from_email,
        "subject": appointment.subject,
        "date": appointment.date,
        "time": appointment.time,
        "status": "created",
        "appointment_id": f"APT-{appointment.date.replace('-', '')}-{appointment.time.replace(':', '')}"
    }
    return appointment_details

def create_appointment(to_emails: List[str], from_email: str, subject: str, date: str, time: str) -> dict:

    """
    Create an appointment and return confirmation details.

    Args:
        to_emails (list): List of attendee email addresses
        from_email (str): Organizer's email address
        subject (str): Appointment subject
        date (str): Date of the appointment. Format: YYYY-MM-DD (e.g., 2025-09-01). Always include the year. If the user omits the year, use {CURRENT_YEAR}.
        time (str): Time of the appointment. Format: HH:MM (24-hour, e.g., 14:30)
    Returns:
        dict: Confirmation details

    Note:
        - date must always be in ISO format: YYYY-MM-DD (e.g., 2025-09-01). The year is required. If the user omits the year, use {CURRENT_YEAR}.
        - time must be in 24-hour format: HH:MM (e.g., 14:30)
    """
    appointment = {
        "to": to_emails,
        "from": from_email,
        "subject": subject,
        "date": date,
        "time": time,
        "status": "created",
        "appointment_id": f"APT-{date.replace('-', '')}-{time.replace(':', '')}"
    }
    return appointment


class AppointmentAgent:
   
    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']

    def __init__(self):
        self._agent = self._build_agent()
        self._user_id = 'appointment_agent'
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
            name="appointment_agent",
            instruction="You are an appointment scheduling assistant. Your purpose is to create appointments based on user queries.",
            #pass token in request , aud claim  in token should match what is configured in MCP server as audience. 
            #curl -X POST "http://127.0.0.1:8080/realms/satishrealm/protocol/openid-connect/token" -H "Content-Type: application/x-www-form-urlencoded" -d client_id=testclient -d grant_type=password -d username=satish -d password=admin -d scope=openid
            #tools=[create_appointment],
            tools=[MCPToolset(
                            connection_params=StreamableHTTPConnectionParams(
                                url="http://localhost:8000/mcp",
                                headers={"Authorization": f"Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJhQUtDT1lBMEQzOUhWVWI4RHREVm1BNEJIZTJiQ2NXMUxzMFlqNGFVNG9VIn0.eyJleHAiOjE3NTY4NDE4MDMsImlhdCI6MTc1Njg0MTUwMywianRpIjoib25ydHJvOjJjZGY5ZDJiLTk5M2ItNTZjYy0yZjk5LTEwNDUyYjhkMzNjZCIsImlzcyI6Imh0dHA6Ly8xMjcuMC4wLjE6ODA4MC9yZWFsbXMvc2F0aXNocmVhbG0iLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiZTA2ZTE2OWItMjliYi00YTAyLTkyZDMtM2JhZmM0ZjBhMjQwIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoidGVzdGNsaWVudCIsInNpZCI6IjAzYjVlZmYzLTAwODUtNDE2NC1iNjI4LWI3MjRkMDc0YzdjNSIsImFjciI6IjEiLCJhbGxvd2VkLW9yaWdpbnMiOlsiKiJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiIsImRlZmF1bHQtcm9sZXMtc2F0aXNocmVhbG0iXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJuYW1lIjoiU2F0aXNoIEthbWF2YXJhbSIsInByZWZlcnJlZF91c2VybmFtZSI6InNhdGlzaCIsImdpdmVuX25hbWUiOiJTYXRpc2giLCJmYW1pbHlfbmFtZSI6IkthbWF2YXJhbSIsImVtYWlsIjoic2F0aXNoa2FtYXZhcmFtQGdtYWlsLmNvbSJ9.eDegyXEa9mRr1mAAH0nXH10_O9OoCN0YSTcvcHc4eckbDonT9zmBBpfgbWbN2LWiUB4YWn_Ppt-IDs1bqcvQJ0HKTku1yzMXzCc6lf_V01Cao5rsdJvlbOrXztCmD7JmH_qqdDkghyJpBzCRFjjieVRb0KoroSLwyh8KWfHx7CuxHp-syC1DP6jqF1u71PTrnOU66FbaPGe56bTzWVYz55a7xQ-1KC2ZGaNbf6TogYF0YePVrBL3Kz39ot4q8u4fL-6V1AjYqrQTmXtdS8iO2YQ9hCgOB9BwZUpgVzt9bq_HT3JLO8i8-rSF7qrolLz0eLF3Dmaxv7BMShFXvODVkw"}
                            ),
                        )],
            output_key="appointment_key",
            before_model_callback=simple_before_model_modifier,
        )
        
        print(f"Building appointment agent: {agent.name}")
        return agent
    
    def get_agent(self) -> LlmAgent:
        return self._agent
    

