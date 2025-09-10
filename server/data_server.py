from mcp.server.fastmcp import FastMCP
import pandas as pd
from agent.conversation_agent import conversation_agent
from langchain.output_parsers import PydanticOutputParser
from agent.prompts import build_common_context
from config.logging import log_exception, setup_logger
from agent.hotel_search_agent import hotel_search_agent
from agent.check_hotel_availability_agent import check_hotel_availability_agent
import json
import asyncio
import redis
import os

mcp = FastMCP("HotelList")
logger = setup_logger("data-server")

df = pd.read_excel("./data/hotels.xlsx")
data = df.to_dict(orient="records")
df1 = pd.read_excel("./data/empty_rooms_5000.xlsx")
data1 = df1.to_dict(orient="records")


@mcp.tool()
async def conversation_assistant(user_message: str):
    """this tool is used for normal conversation with user"""
    try:
        available_tools = "\n".join([
            "- search_hotels: Find hotels by city, price, amenities, room type",
            "- check_availability: Check room availability for dates and room type",
            "- get_hotel_details: Retrieve details and recent bookings for a hotel",
            "- create_booking: Create a booking and return a quote/summary",
            "- get_booking_details: Fetch details for a specific booking",
            "- update_booking_status: Update booking payment/status",
            "- get_hotel_analytics: Revenue, occupancy proxy, room popularity",
            "- get_revenue_report: Financial reporting by period/hotel",
            "- search_hotels_advanced: Natural-language filtered search",
            "- get_availability_report: City/date availability summary",
            "- analyze_booking_trends: Trends across bookings and revenue",
            "- dynamic_pricing: AI price recommendations by demand/context",
            "- predictive_availability: Forecast availability windows",
            "- guest_matching: Personalized hotel matches for a guest",
            "- sentiment_analysis: Analyze guest feedback sentiment",
            "- blockchain_verification: Verify booking integrity",
            "- iot_integration: Smart-room setup plan for preferences",
            "- multilanguage: Translate/adapt messaging for locales",
            "- carbon_tracking: Estimate footprint and reduction tips",
            "- emergency_response: Incident response checklist",
            "- ar_vr: Curate AR/VR hotel tour scenes",
            "- fraud_detection: Risk screen for booking events",
            "- loyalty_program: Personalized loyalty offer design",
        ])
        
        chain, memory = conversation_agent("ved")
        context = build_common_context()
        history = memory.load_memory_variables({}).get('history', '') if memory else ""
        logger.info("History: %s", history)
        chain_input = {
            "input": user_message,
            "context": context,
            "available_tools": available_tools,
            "history": history
        }
        
        output = await chain.ainvoke(chain_input)
        if memory:
            memory.save_context({"input": user_message}, {"output": output})
        
        return output
        
    except Exception as e:
        log_exception(logger, e, "Conversation mcp server error")
        return {"error": str(e)}

@mcp.tool()
async def hotel_search(question: str) -> dict:
    """Search hotels in the local Excel dataset by natural language."""
    try:
        chain, memory = hotel_search_agent("ved")
        history = memory.load_memory_variables({}).get('history', '') if memory else ""
        logger.info("History: %s", history)
        output = await chain.ainvoke({
            "data": json.dumps(data),
            "question": question,
            "history": history
        })
        
        if memory:
            memory.save_context({"input": question}, {"output": output})
        
        return output
    except Exception as e:
        log_exception(logger, e, "Hotel search tool error")
        return {"error": str(e)}
    

@mcp.tool()
async def hotel_availability(question:str, hotel_name: str) -> dict:
    """Search hotels in the local Excel dataset by natural language."""
    try:
        chain, memory = check_hotel_availability_agent("ved")
        history = memory.load_memory_variables({}).get('history', '') if memory else ""
        logger.info("History: %s", history)
        output = await chain.ainvoke({
            "empty_rooms": data1,
            "hotels": data,
            "hotel_name": hotel_name,
            "history": history
        })
        
        if memory:
            memory.save_context({"input": question}, {"output": output})
        
        return output
    except Exception as e:
        log_exception(logger, e, "Hotel search tool error")
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run(transport="stdio")