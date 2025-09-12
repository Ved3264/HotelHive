from mcp.server.fastmcp import FastMCP
import pandas as pd
from agent.conversation_agent import conversation_agent
from langchain.output_parsers import PydanticOutputParser
from agent.prompts import build_common_context
from config.logging import log_exception, setup_logger
from agent.hotel_search_agent import hotel_search_agent
from agent.check_hotel_availability_agent import check_hotel_availability_agent
from agent.book_hotel_agent import check_hotel_availability_agent as book_hotel_agent
import json
import asyncio
import redis
import os
import datetime

mcp = FastMCP("HotelList")
logger = setup_logger("data-server")

df = pd.read_excel("./data/hotels.xlsx")
data = df.to_dict(orient="records")
df1 = pd.read_excel("./data/empty_rooms_5000.xlsx")
data1 = df1.to_dict(orient="records")

# Path to the bookings Excel file
BOOKINGS_FILE = "./data/bookings.xlsx"

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
        
        # If no hotels found, suggest alternatives
        if not output or "error" in output:
            return {
                "message": "No hotels found matching your criteria.",
                "suggestions": "Try broadening your search (e.g., different dates, higher budget, or other locations)."
            }
        
        return output
    except Exception as e:
        log_exception(logger, e, "Hotel search tool error")
        return {"error": str(e), "suggestions": "Try broadening your search criteria."}

@mcp.tool()
async def hotel_availability(question: str, hotel_name: str) -> dict:
    """Check room availability in the local Excel dataset by natural language."""
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
        
        # If no availability, suggest checking other dates or hotels
        if not output or "error" in output:
            return {
                "message": f"No availability for {hotel_name}.",
                "suggestions": "Try different dates or another hotel."
            }
        
        return output
    except Exception as e:
        log_exception(logger, e, "Hotel availability tool error")
        return {"error": str(e), "suggestions": "Try different dates or another hotel."}

@mcp.tool()
async def create_booking(booking_request: str, hotel_name: str, room_type: str, check_in: str, check_out: str, guest_name: str) -> dict:
    """Create a hotel booking and add it to the bookings Excel file."""
    try:
        chain, memory = book_hotel_agent("ved")
        history = memory.load_memory_variables({}).get('history', '') if memory else ""
        logger.info("History: %s", history)
        
        # Validate input
        try:
            check_in_date = datetime.datetime.strptime(check_in, "%Y-%m-%d")
            check_out_date = datetime.datetime.strptime(check_out, "%Y-%m-%d")
            if check_in_date >= check_out_date:
                return {"error": "Check-out date must be after check-in date"}
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD"}
        
        # Check if the hotel and room type are valid
        hotel_data = next((item for item in data if item["name"].lower() == hotel_name.lower()), None)
        if not hotel_data:
            return {"error": f"Hotel {hotel_name} not found"}
        
        # Check availability for all dates in range
        current_date = check_in_date
        while current_date <= check_out_date:
            date_str = current_date.strftime("%Y-%m-%d")
            availability = next(
                (item for item in data1 if item["hotel_name"].lower() == hotel_name.lower() and 
                 item["room_type"].lower() == room_type.lower() and 
                 item["date"] == date_str), None
            )
            if not availability or availability["available_rooms"] <= 0:
                return {"error": f"No {room_type} rooms available at {hotel_name} on {date_str}"}
            current_date += datetime.timedelta(days=1)
        
        # Create booking entry
        booking_id = f"BK{len(data1) + 1:06d}"
        booking_entry = {
            "booking_id": booking_id,
            "hotel_name": hotel_name,
            "room_type": room_type,
            "check_in": check_in,
            "check_out": check_out,
            "guest_name": guest_name,
            "status": "confirmed",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Append to bookings Excel
        bookings_df = pd.read_excel(BOOKINGS_FILE) if os.path.exists(BOOKINGS_FILE) else pd.DataFrame()
        bookings_df = pd.concat([bookings_df, pd.DataFrame([booking_entry])], ignore_index=True)
        bookings_df.to_excel(BOOKINGS_FILE, index=False)
        
        # Update availability for all dates
        current_date = check_in_date
        while current_date <= check_out_date:
            date_str = current_date.strftime("%Y-%m-%d")
            for item in data1:
                if (item["hotel_name"].lower() == hotel_name.lower() and 
                    item["room_type"].lower() == room_type.lower() and 
                    item["date"] == date_str):
                    item["available_rooms"] -= 1
            current_date += datetime.timedelta(days=1)
        pd.DataFrame(data1).to_excel("./data/empty_rooms_5000.xlsx", index=False)
        
        # Generate confirmation
        output = await chain.ainvoke({
            "booking_request": booking_request,
            "history": history
        })
        
        if memory:
            memory.save_context({"input": booking_request}, {"output": output})
        
        return {
            "booking_confirmation": output,
            "booking_details": booking_entry
        }
    except Exception as e:
        log_exception(logger, e, "Create booking tool error")
        return {"error": str(e)}

if __name__ == "__main__":
    mcp.run(transport="stdio")