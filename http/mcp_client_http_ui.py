import asyncio
from typing import Optional, Any, Dict, List, Union
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall
from dotenv import load_dotenv
import re
import os
import hashlib
from openai import AsyncOpenAI
import json
import sys
import uuid
from fastmcp import Client

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QLineEdit,
    QPushButton, QVBoxLayout, QWidget
)
from PyQt5.QtCore import pyqtSignal, QObject, QTimer
from qasync import QEventLoop, asyncSlot, asyncClose
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout

load_dotenv()

# [Previous utility functions remain exactly the same...]
# Global cache for redaction mapping
REDACTION_CACHE: Dict[str, str] = {}

def generate_redaction_token(email: str) -> str:
    salt = "your_app_specific_salt"
    return f"EAMIL_{hashlib.sha256((salt + email).encode()).hexdigest()[:8]}"

def redact_emails_in_text(text: str) -> str:
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    for email in emails:
        token = generate_redaction_token(email)
        REDACTION_CACHE[token] = email
        text = text.replace(email, token)
    return text

def redact_emails_in_content(content: Union[List, Dict, Any]) -> Union[List, Dict, Any]:
    if hasattr(content, 'text') and hasattr(content, 'type'):
        # Handle TextContent-like objects
        redacted_text = redact_emails_in_text(content.text)
        return type(content)(
            type=content.type,
            text=redacted_text,
            annotations=getattr(content, 'annotations', None),
            meta=getattr(content, 'meta', None)
        )
    elif isinstance(content, list):
        return [redact_emails_in_content(item) for item in content]
    elif isinstance(content, dict):
        return {k: redact_emails_in_content(v) for k, v in content.items()}
    elif isinstance(content, str):
        return redact_emails_in_text(content)
    else:
        return content
    
def reconstruct_emails_in_content(content: Union[List, Dict, Any]) -> Union[List, Dict, Any]:
    if hasattr(content, 'text'):
        reconstructed_text = reconstruct_emails_in_text(content.text)
        return type(content)(
            type=content.type,
            text=reconstructed_text,
            annotations=getattr(content, 'annotations', None),
            meta=getattr(content, 'meta', None)
        )
    elif isinstance(content, list):
        return [reconstruct_emails_in_content(item) for item in content]
    elif isinstance(content, dict):
        return {k: reconstruct_emails_in_content(v) for k, v in content.items()}
    elif isinstance(content, str):
        for token, email in REDACTION_CACHE.items():
            content = content.replace(token, email)
        return content
    else:
        return content

def reconstruct_emails_in_text(text: str) -> str:
    """Reconstruct emails in plain text"""
    if not isinstance(text, str):
        return text
    for token, email in REDACTION_CACHE.items():
        text = text.replace(token, email)
    return text

def clear_redaction_cache():
    """Clear the redaction mapping"""
    global REDACTION_CACHE
    REDACTION_CACHE.clear()

def markdown_to_html(text: str) -> str:
    """Convert basic Markdown formatting to HTML for QTextEdit display"""
    if not text:
        return text
    
    # Convert **bold** to <strong>
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # Handle bullet points (•) - preserve as is with minimal spacing
    text = re.sub(r'^• (.+)$', r'• \1', text, flags=re.MULTILINE)
    
    # Handle numbered lists - preserve as is
    text = re.sub(r'^(\d+\.\s+.+)$', r'\1', text, flags=re.MULTILINE)
    
    # Handle dash bullet points
    text = re.sub(r'^- (.+)$', r'• \1', text, flags=re.MULTILINE)
    
    # Replace line breaks with HTML line breaks, but preserve the original structure
    # Don't add extra spacing - just convert \n to <br>
    lines = text.split('\n')
    html_lines = []
    
    for line in lines:
        if line.strip():  # If line has content
            html_lines.append(line)
        else:  # Empty line - preserve as single line break
            html_lines.append('')
    
    # Join with <br> tags to preserve original spacing
    result = '<br>'.join(html_lines)
    
    # Clean up any excessive breaks (more than 2 consecutive)
    result = re.sub(r'(<br>){3,}', '<br><br>', result)
    
    return result


class MCPClient(QObject):
    message_received = pyqtSignal(str, str)
    status_update = pyqtSignal(str)
    connection_ready = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)

    def __init__(self, auth_token: str, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.session = None
        self.exit_stack = AsyncExitStack()
        self.client = None
        self.connected = False
        self._shutting_down = False
        self.auth_token = auth_token

    async def cleanup(self):
        self._shutting_down = True
        if hasattr(self, 'exit_stack'):
            await self.exit_stack.aclose()

    async def process_query(self, query: str):
        """Process a query using OpenAI and available tools"""
        try:
            self.message_received.emit("user", query)
            
            if not self.client:
                self.client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
            
            query = redact_emails_in_text(query)
            messages = [{"role": "user", "content": query}]
            
            # Use FastMCP client's list_tools (returns list directly)
            tools = await self.session.list_tools()
            available_tools = [{
                "type": "function", 
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            } for tool in tools]  # No .tools attribute needed

            response = await self.invoke_llm(self.client, available_tools, messages)
            assistant_message = response.choices[0].message
            
            while assistant_message.tool_calls:
                tool_calls = assistant_message.tool_calls
                await self.invoke_tool(tool_calls, messages, [])
                response = await self.invoke_llm(self.client, available_tools, messages)
                assistant_message = response.choices[0].message

            response_content = reconstruct_emails_in_content(response.choices[0].message.content)
            self.message_received.emit("assistant", response_content)
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Error processing query: {str(e)}")
            return False

    async def invoke_llm(self, client: AsyncOpenAI, available_tools: list, messages: list):
        return await client.chat.completions.create(
            model="gpt-4-turbo",
            max_tokens=1000,
            messages=messages,
            tools=available_tools
        )
    
    async def invoke_tool(self, tool_calls: Optional[List[ChatCompletionMessageToolCall]], messages: list, final_text: list):
        if tool_calls:
            messages.append({
                "role": "assistant",
                "content": '',
                "tool_calls": tool_calls
            })
            
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                tool_args = reconstruct_emails_in_content(tool_args)
                
                # Use FastMCP client's call_tool method
                result = await self.session.call_tool(tool_name, tool_args)
                result.content = [redact_emails_in_content(item) for item in result.content]
                
                messages.append({
                    "role": "tool",
                    "name": tool_name,
                    "content": result.content,
                    "tool_call_id": tool_call.id
                })

class ChatWindow(QMainWindow):
    def __init__(self, server_script_path: str, auth_token: str):
        super().__init__()
        self.server_script_path = server_script_path
        self.auth_token = auth_token
        self._shutting_down = False
        self.connected_client = None  # Store persistent connection
        self.init_ui()
        self.mcp_client = None
        # Use QTimer to ensure event loop is running
        QTimer.singleShot(0, self.start_initialization)

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("MCP Client Chat")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)
        
        # Input area
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.returnPressed.connect(self.on_send_clicked)
        layout.addWidget(self.message_input)
        
        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.on_send_clicked)
        layout.addWidget(self.send_button)
        
        # Status
        self.statusBar().showMessage("Initializing...")
        self.set_ui_enabled(True)
        self.message_input.setFocus()

    def start_initialization(self):
        if not self._shutting_down:
            asyncio.create_task(self.initialize_client())

    def on_connection_ready(self, ready: bool):
        """Handle connection ready signal"""
        self.set_ui_enabled(ready)
        if ready:
            self.statusBar().showMessage("Ready to chat")
        else:
            self.statusBar().showMessage("Connection failed")

    async def initialize_client(self):
        """Initialize the MCP client with persistent connection"""
        try:
            # Load configuration from mcp.json
            config = self.load_mcp_config()
            
            # Override URL if provided via command line
            if hasattr(self, 'server_script_path') and self.server_script_path:
                # Update the first server's URL with command line argument
                for server_name, server_config in config["mcpServers"].items():
                    server_config["url"] = self.server_script_path
                    break
            
            client_obj = Client(config)
            self.connected_client = await client_obj.__aenter__()  # Enter the context manually
            
            await self.connected_client.ping()
            tools = await self.connected_client.list_tools()
            
            self.mcp_client = MCPClient(self.auth_token)
            self.mcp_client.session = self.connected_client
            self.mcp_client.connected = True
            
            # Connect signals
            self.mcp_client.message_received.connect(self.display_message)
            self.mcp_client.error_occurred.connect(self.display_error)
            
            # Display connection messages
            self.display_message("system", f"User authenticated with token: {self.auth_token}")
            self.display_message("system", f"Successfully connected to MCP server. Discovered tools: {[tool.name for tool in tools]}")
            
            self.set_ui_enabled(True)
            self.statusBar().showMessage("Ready to chat")
            
        except Exception as e:
            self.display_message("error", f"Failed to initialize client: {str(e)}")
            self.set_ui_enabled(False)

    def load_mcp_config(self) -> dict:
        """Load MCP configuration from mcp.json file"""
        config_file = "mcp.json"
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    
                # Validate required structure
                if "mcpServers" not in config:
                    raise ValueError("mcp.json must contain 'mcpServers' section")
                    
                # Add dynamic values to headers if not present
                for server_name, server_config in config["mcpServers"].items():
                    if "headers" not in server_config:
                        server_config["headers"] = {}
                    
                    # Add auth token if not present
                    if "Authorization" not in server_config["headers"]:
                        server_config["headers"]["Authorization"] = f"Bearer {self.auth_token}"
                    
                    # Add API key if not present
                    if "api_key" not in server_config["headers"]:
                        server_config["headers"]["api_key"] = os.environ.get("MCP_API_KEY", str(uuid.uuid4()))
                
                return config
            else:
                # Create default config if file doesn't exist
                self.create_default_mcp_config(config_file)
                return self.load_mcp_config()  # Recursive call to load the newly created file
                
        except Exception as e:
            raise Exception(f"Error loading mcp.json: {str(e)}")

    def create_default_mcp_config(self, config_file: str):
        """Create a default mcp.json configuration file"""
        default_config = {
            "mcpServers": {
                "default_server": {
                    "transport": "http",
                    "url": "http://localhost:8000/mcp",
                    "headers": {
                        "Authorization": f"Bearer {self.auth_token}",
                        "api_key": os.environ.get("MCP_API_KEY", str(uuid.uuid4()))
                    },
                    "auth": "oauth"
                }
            }
        }
        
        try:
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            self.display_message("system", f"Created default {config_file} configuration file")
        except Exception as e:
            raise Exception(f"Error creating default mcp.json: {str(e)}")


    @asyncSlot()
    async def on_send_clicked(self):
        if not self.mcp_client or not self.mcp_client.connected:
            self.display_message("error", "Not connected to MCP server")
            return
            
        message = self.message_input.text().strip()
        if not message:
            return
            
        self.message_input.clear()
        self.set_ui_enabled(False)
        
        try:
            # Use the persistent connection
            await self.mcp_client.process_query(message)
        except Exception as e:
            self.display_message("error", f"Error processing message: {str(e)}")
        finally:
            self.set_ui_enabled(True)
            self.message_input.setFocus()

    def set_ui_enabled(self, enabled: bool):
        """Enable or disable UI elements"""
        self.message_input.setEnabled(enabled)
        self.send_button.setEnabled(enabled)

    def display_message(self, role: str, message: str):
        """Thread-safe message display with proper spacing between messages"""
        if not self._shutting_down and hasattr(self, 'chat_display'):
            try:
                cursor = self.chat_display.textCursor()
                cursor.movePosition(cursor.End)
                
                # Add spacing between messages
                if cursor.position() > 0:  # Only add spacing if not first message
                    cursor.insertHtml('<br>')
                
                if role == "user":
                    prefix = "You:"
                    color = "#0066cc"
                    # For user messages, just display as plain text
                    cursor.insertHtml(f'<p><span style="color:{color};font-weight:bold;">{prefix}</span><br>{message}</p>')
                elif role == "assistant":
                    prefix = "Assistant:"
                    color = "#009933"
                    # For assistant messages, convert markdown to HTML for better formatting
                    formatted_message = markdown_to_html(message)
                    cursor.insertHtml(f'<p><span style="color:{color};font-weight:bold;">{prefix}</span><br>{formatted_message}</p>')
                elif role == "system":
                    prefix = "System:"
                    color = "#7B0D0D"
                    cursor.insertHtml(f'<p><span style="color:{color};font-weight:bold;">{prefix}</span><br>{message}</p>')
                else:  # error
                    prefix = "Error:"
                    color = "#cc0000"
                    cursor.insertHtml(f'<p><span style="color:{color};font-weight:bold;">{prefix}</span><br>{message}</p>')
                
                # Add extra spacing after system messages for better readability
                #if role == "system":
                cursor.insertHtml('<br>')
                    
                self.chat_display.setTextCursor(cursor)
                self.chat_display.ensureCursorVisible()
                
                # Scroll to bottom
                self.chat_display.verticalScrollBar().setValue(
                    self.chat_display.verticalScrollBar().maximum()
                )
            except RuntimeError:
                pass  # Ignore if widget is already deleted

    def display_error(self, error_msg: str):
        """Display error messages"""
        self.display_message("error", error_msg)
        self.statusBar().showMessage("Error occurred")

    @asyncClose
    async def closeEvent(self, event):
        """Clean up on window close"""
        self._shutting_down = True
        
        # Close the persistent connection
        if hasattr(self, 'connected_client') and self.connected_client:
            try:
                await self.connected_client.__aexit__(None, None, None)
            except:
                pass
        
        if hasattr(self, 'mcp_client'):
            await self.mcp_client.cleanup()
        event.accept()

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login to Agentic AI MCP Client")
        self.setFixedSize(300, 150)
        
        self.token = None 
        # Widgets
        self.label_username = QLabel("Username:")
        self.input_username = QLineEdit()
        self.label_password = QLabel("Password:")
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        self.button_login = QPushButton("Login")
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label_username)
        layout.addWidget(self.input_username)
        layout.addWidget(self.label_password)
        layout.addWidget(self.input_password)
        layout.addWidget(self.button_login)
        self.setLayout(layout)
        
        # Signals
        self.button_login.clicked.connect(self.authenticate)
    
    def authenticate(self):
        """Validate credentials and emit signal on success"""
        username = self.input_username.text()
        password = self.input_password.text()
        
        # Replace with your actual auth API call
        self.token = self.get_auth_token(username, password)
        
        if self.token:
            self.accept()  # Close dialog and return success
            return self.token
        else:
            self.show_error("Invalid credentials")

    def get_auth_token(self, username: str, password: str) -> Optional[str]:
        """Mock authentication function - replace with real API call"""
        # Example: Call your auth endpoint
        # response = requests.post("/login", json={"user": username, "pass": password})
        # return response.json().get("token")
        
        # For testing, return a dummy token if credentials are non-empty
        return "dummy_token" if username and password else None

    def show_error(self, message: str):
        """Display error message"""
        self.input_password.clear()
        self.statusBar().showMessage(message)  # If using status bar
        
async def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # Show login window first
    login = LoginWindow()
    if login.exec_() == QDialog.Accepted and login.token:
        token = login.token  # Store the token (you'll need to add this to LoginWindow)
        
        # Initialize chat window with token
        window = ChatWindow(sys.argv[1], token)  # Pass token to ChatWindow
        window.show()
        
        with loop:
            loop.run_forever()
    else:
        sys.exit(0)  # Exit if login failed


if __name__ == "__main__":
    # usage: python mcp_client_http_ui.py http://127.0.0.1:8000/mcp
    try:
        asyncio.run(main())
    except RuntimeError:
        pass
    except Exception as e:
        print(f"Application error: {str(e)}")