import asyncio
from typing import Any
from uuid import uuid4
import httpx
from a2a.client import A2AClient
from a2a.client import A2ACardResolver
from a2a.types import (
    MessageSendParams,
    SendMessageRequest,
    SendMessageResponse,
    
)
from a2a.types import (
    MessageSendParams,
)

def get_user_query() -> str:
    return input('\nUser Query:  ')


async def interact_with_server(client: A2AClient) -> None:
    while True:
        user_input = get_user_query()
        if user_input.lower() == 'exit':
            print('Thank You for experimenting A2A jira agent')
            break

        send_message_payload: dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [{'type': 'text', 'text': user_input}],
                'messageId': uuid4().hex,
            },
        }

        try:
            message_request = SendMessageRequest(
                id=uuid4().hex,
                params=MessageSendParams(**send_message_payload)
            )
            send_response: SendMessageResponse = await client.send_message(message_request)
            print(f"Response from jira agent : {send_response}")
        except Exception as e:
            print(f'An error occurred: {e}')


async def main() -> None:
    print('Welcome to the A2A client!')
    print("Please enter your query (type 'exit' to quit):")
    headers = {"Authorization": "Bearer satish_token_a2a_1"}
    async with httpx.AsyncClient(timeout=30, headers=headers) as httpx_client:
        card_resolver = A2ACardResolver(
                    httpx_client, 'http://localhost:10001' # connecting to jira agent server
                )  
        card = await card_resolver.get_agent_card()
        print(f"Resolved jira agent card: {card}")
        #client = httpx.AsyncClient(timeout=30)
        a2a_client =  A2AClient(
            httpx_client,card, url='http://localhost:10001'
        )
        await interact_with_server(a2a_client)


if __name__ == '__main__':
    asyncio.run(main())