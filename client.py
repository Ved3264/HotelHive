# client.py (updated for hotel_availability tool integration)
import asyncio
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import sys
import json
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

models = os.getenv("MODEL")
api_key = os.getenv("API_KEY")

async def process_message(user_input: str) -> str:
    """Process a single message and return the response"""
    try:
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "server.data_server"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                tools = await load_mcp_tools(session)

                google_llm = ChatGoogleGenerativeAI(
                    temperature=0,
                    model=models,
                    google_api_key=api_key
                )

                system_prompt = SystemMessage(content="""
                You have access to MCP tools exposed by the data server.
                
                Routing policy:
                (A) If the user's message is a greeting/small talk (e.g., 'hi', 'hello', 'hey', 'thanks', 'how are you'),
                    call 'conversation_assistant' with {"user_message": <message>}.
                
                (B) If the user's message is about searching for hotels with specific criteria (location, price, room_type, amenities, dates),
                    call 'hotel_search' with {"question": <message>}.
                
                (C) If the user's message is specifically about checking availability for a particular hotel by name,
                    or asks about room availability, vacancies, or booking status for a specific hotel,
                    call 'hotel_availability' with {"question": <message>, "hotel_name": <extracted_hotel_name>}.
                    Extract the hotel name from the user's message if explicitly mentioned.
                
                (D) If the user's message doesn't fit the above categories or needs clarification,
                    call 'conversation_assistant' with {"user_message": <message>}
                    to ask concise clarifying questions.
                
                Always use exactly one tool per turn and return its response.
                When in doubt about hotel availability queries, choose conversation_assistant to ask for the hotel name.
                """)

                agent = create_react_agent(model=google_llm, tools=tools)

                TURN_TIMEOUT_SEC = 30
                
                try:
                    state = await asyncio.wait_for(
                        agent.ainvoke(
                            {"messages": [system_prompt, HumanMessage(content=user_input)]},
                            config={"recursion_limit": 10}, 
                        ),
                        timeout=TURN_TIMEOUT_SEC,
                    )

                    messages = state.get("messages", [])
                    final_text = ""
                    
                    for msg in reversed(messages):
                        if hasattr(msg, 'type') and msg.type == 'ai':
                            final_text = msg.content
                            break
                        elif isinstance(msg, dict) and msg.get('type') == 'ai':
                            final_text = msg.get('content', '')
                            break
                    
                    if not final_text:
                        final_text = "I'm not sure how to respond to that. Can you try rephrasing?"
                    
                    return final_text
                    
                except asyncio.TimeoutError:
                    return "The request timed out. Please try a simpler query."
                except Exception as e:
                    logger.error(f"Agent error: {e}")
                    return f"Error processing your request: {str(e)}"
                    
    except Exception as e:
        logger.error(f"Session error: {e}")
        return f"Connection error: {str(e)}"

async def main():
    """Main function for standalone use"""
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        response = await process_message(user_input)
        print(response)
    else:
        while True:
            try:
                user_input = input("You: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in {"exit", "quit", "q"}:
                    break

                response = await process_message(user_input)
                print("Agent:", response)

            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())