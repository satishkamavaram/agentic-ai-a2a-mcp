import asyncio
from typing import Optional,Any, Dict, List, Union
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

load_dotenv()  # load environment variables from .env

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

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
    
    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        env_vars = {
            "API_KEY": "your_api_key_1234",
            "CONFIG_PATH": "/path/to/config",
        }
        
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=env_vars
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Process a query using OpenAI and available tools"""
        
        api_key = os.environ["OPENAI_API_KEY"] 
        # Initialize OpenAI client with your API key
        client = AsyncOpenAI(api_key=api_key)
        print("\n\n")
        print(f"\033[1m**user query:**\033[0m {query}\n\n")
        query = redact_emails_in_text(query)
        print(f"\033[1m**user query redacted:**\033[0m {query}\n\n")
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]
        final_text = []
        response = await self.session.list_tools()
        available_tools = [{
            "type": "function", 
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        } for tool in response.tools]

        
        print(f"\033[1m**sending user query to openapi llm to find if any mcp tool to use:**\033[0m {messages}\n\n")
        response = await self.invoke_llm(client, available_tools, messages)
        assistant_message = response.choices[0].message
        
        while assistant_message.tool_calls:
            tool_calls = assistant_message.tool_calls
            await self.invoke_tool(tool_calls, messages, final_text)
            print(f"\033[1m**sending tools response to openapi llm:**\033[0m {messages}\n\n")
            response = await self.invoke_llm(client, available_tools, messages)
            print(f"\033[1m**openai llm response:**\033[0m {response}\n\n")
            assistant_message = response.choices[0].message

        response_content = reconstruct_emails_in_content(response.choices[0].message.content)
        final_text.append(response_content)

        return "\n".join(final_text)

    async def invoke_llm(self,  client: AsyncOpenAI,available_tools: list,messages: list) -> str:
         return await client.chat.completions.create(
                    model="gpt-4-turbo",
                    max_tokens=1000,
                    messages=messages,
                    tools=available_tools
                )
    
    async def invoke_tool(self, tool_calls: Optional[List[ChatCompletionMessageToolCall]] ,messages: list,final_text:list) -> None:
        if tool_calls:
            print(f"\033[1m**Going to call these mcp tool:**\033[0m {tool_calls} \n\n")
            messages.append({
                    "role": "assistant",
                    "content": '',
                    "tool_calls": tool_calls
            })
            for tool_call in tool_calls:
                print(f"\033[1m**Processing tool call:**\033[0m {tool_call}\n\n")
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                print(f"\033[1m**redacted input args:**\033[0m {tool_args}\n\n")
                tool_args = reconstruct_emails_in_content(tool_args)
                print(f"\033[1m**reconstructed input args for sendint to mcp tool:**\033[0m {tool_args}\n\n")
                # Execute tool call
                result = await self.session.call_tool(tool_name, tool_args)
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")
                print(f"\033[1m**mcp tool response:**\033[0m {result}\n\n")
                #result.content = redact_emails(result.content)  # Redact emails in the tool response
                result.content = [redact_emails_in_content(item) for item in result.content]
                print(f"\033[1m**mcp tool response redacted:**\033[0m {result}\n\n")
                
                messages.append({
                    "role": "tool",
                    "name": tool_name,
                    "content": result.content,
                    "tool_call_id": tool_call.id
                })

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\n\033[1m**Query:**\033[0m ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\033[1m**Final Response:**\033[0m \n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python mcp_client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())