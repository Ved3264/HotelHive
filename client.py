import asyncio
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
import os
import sys
import json
from dotenv import load_dotenv
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
models = os.getenv("MODEL")
api_key = os.getenv("API_KEY")
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

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
                session_id = "ved"
                history = RedisChatMessageHistory(session_id=session_id, url=redis_url)
                memory = ConversationBufferMemory(
                    chat_memory=history,
                    return_messages=True,
                    memory_key="history",
                    input_key="input",
                )
                
                # Load full message history
                memory_vars = memory.load_memory_variables({})
                past_messages = memory_vars.get('history', [])
                
                google_llm = ChatGoogleGenerativeAI(
                    temperature=0,
                    model=models,
                    google_api_key=api_key
                )

                # System instructions for tool routing with enhanced history parsing
                system_prompt = SystemMessage(content="""
                You are HotelHive, a hotel booking assistant. Review the FULL conversation history (all messages) to extract details like hotel name, room type, check-in/check-out dates, and guest name. Do NOT re-ask for details already provided in history.

                Routing policy:
                (A) If the message is a greeting/small talk (e.g., "hi", "hello") → call 'conversation_assistant' with {"user_message": <message>}.

                (B) If the message is about searching hotels (e.g., mentions city, price, amenities) → 
                    call 'hotel_search' with {"question": <message>}. Use history to fill in missing details like location or budget if available.

                (C) If the message is about checking availability for a specific hotel → 
                    extract 'hotel_name' from history or message, then call 'hotel_availability' with {"question": <message>, "hotel_name": <hotel_name>}.

                (D) If the message indicates booking intent (e.g., contains "book", "reserve", "stay", or includes room type/dates/guest name):
                    - Extract ALL details from FULL history and current message:
                        • hotel_name (e.g., "Hotel_1")
                        • room_type (e.g., "Single")
                        • check_in (YYYY-MM-DD, e.g., "2025-09-20")
                        • check_out (YYYY-MM-DD, e.g., "2025-09-23")
                        • guest_name (e.g., "John Doe")
                    - If ALL details are present, call 'create_booking' with:
                        {"booking_request": <original message>,
                         "hotel_name": <hotel_name>,
                         "room_type": <room_type>,
                         "check_in": <check_in>,
                         "check_out": <check_out>,
                         "guest_name": <guest_name>}.
                    - If ANY details are missing, call 'conversation_assistant' to ask ONLY for missing details, referencing known ones (e.g., "I have Hotel_1 and John Doe, but need room type and dates.").

                (E) If the message doesn't fit above → call 'conversation_assistant' with {"user_message": <message>}.

                Rules:
                - Use exactly one tool per turn.
                - Assume YYYY-MM-DD date format.
                - Today’s date is September 12, 2025.
                - Use history to avoid re-asking for known details.
                - For flexible queries (e.g., "anywhere"), suggest hotels based on history or default to broad search.
                """)

                agent = create_react_agent(model=google_llm, tools=tools)

                TURN_TIMEOUT_SEC = 30
                
                try:
                    # Build initial state with full history
                    initial_messages = past_messages + [system_prompt, HumanMessage(content=user_input)]
                    
                    state = await asyncio.wait_for(
                        agent.ainvoke(
                            {"messages": initial_messages},
                            config={"recursion_limit": 10}, 
                        ),
                        timeout=TURN_TIMEOUT_SEC,
                    )

                    messages = state.get("messages", [])
                    final_text = ""
                    
                    # Extract the last AI message content
                    for msg in reversed(messages):
                        if isinstance(msg, AIMessage):
                            final_text = msg.content
                            break
                    
                    if not final_text:
                        final_text = "I'm not sure how to respond to that. Can you try rephrasing?"
                    
                    # Save to memory
                    if memory:
                        memory.save_context({"input": user_input}, {"output": final_text})
                    return final_text
                    
                except asyncio.TimeoutError:
                    return "The request timed out. Please try again."
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