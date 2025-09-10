# 🚀 Complete MCP Server & Client Development Guide

A comprehensive guide to building different types of Model Context Protocol (MCP) servers and their corresponding clients using your hotel management data.

## 📋 Table of Contents

1. [MCP Server Types Overview](#mcp-server-types-overview)
2. [Basic Data Server](#basic-data-server)
3. [Tool-Based Server](#tool-based-server)
4. [Resource Server](#resource-server)
5. [Hybrid Server](#hybrid-server)
6. [Client Implementations](#client-implementations)
7. [Advanced Patterns](#advanced-patterns)
8. [Testing & Debugging](#testing--debugging)

## 🏗️ MCP Server Types Overview

### Server Categories
- **Data Server**: Exposes data resources (files, databases)
- **Tool Server**: Provides executable functions/tools
- **Resource Server**: Manages external resources (APIs, services)
- **Hybrid Server**: Combines multiple server types

## 1. 📊 Basic Data Server

### Server Implementation

```python
# server/data_server.py
from mcp.server.fastmcp import FastMCP
import pandas as pd
import json
from typing import Dict, Any

mcp = FastMCP("HotelDataServer")

# Load data once at startup
hotels_df = pd.read_excel("./data/hotels.xlsx")
empty_rooms_df = pd.read_excel("./data/empty_rooms_5000.xlsx")
bookings_df = pd.read_excel("./data/hotel_bookings.xlsx")

@mcp.resource("hotels://data")
async def get_hotels_data() -> str:
    """Get all hotels data as JSON"""
    return hotels_df.to_json(orient="records")

@mcp.resource("hotels://empty-rooms")
async def get_empty_rooms_data() -> str:
    """Get all empty rooms data as JSON"""
    return empty_rooms_df.to_json(orient="records")

@mcp.resource("hotels://bookings")
async def get_bookings_data() -> str:
    """Get all bookings data as JSON"""
    return bookings_df.to_json(orient="records")

@mcp.resource("hotels://summary")
async def get_data_summary() -> str:
    """Get summary statistics of all datasets"""
    summary = {
        "hotels": {
            "count": len(hotels_df),
            "columns": list(hotels_df.columns),
            "sample": hotels_df.head(3).to_dict(orient="records")
        },
        "empty_rooms": {
            "count": len(empty_rooms_df),
            "columns": list(empty_rooms_df.columns),
            "sample": empty_rooms_df.head(3).to_dict(orient="records")
        },
        "bookings": {
            "count": len(bookings_df),
            "columns": list(bookings_df.columns),
            "sample": bookings_df.head(3).to_dict(orient="records")
        }
    }
    return json.dumps(summary, indent=2)

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### Client Implementation

```python
# client/data_client.py
import asyncio
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
import json

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "server.data_server"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List available resources
            resources = await session.list_resources()
            print("Available Resources:")
            for resource in resources.resources:
                print(f"- {resource.uri}")
            
            # Get hotels data
            hotels_data = await session.read_resource("hotels://data")
            hotels = json.loads(hotels_data.contents)
            print(f"\nLoaded {len(hotels)} hotels")
            
            # Get data summary
            summary_data = await session.read_resource("hotels://summary")
            summary = json.loads(summary_data.contents)
            print(f"\nData Summary:")
            print(f"Hotels: {summary['hotels']['count']} records")
            print(f"Empty Rooms: {summary['empty_rooms']['count']} records")
            print(f"Bookings: {summary['bookings']['count']} records")

if __name__ == "__main__":
    asyncio.run(main())
```

## 2. 🔧 Tool-Based Server

### Server Implementation

```python
# server/tool_server.py
from mcp.server.fastmcp import FastMCP
import pandas as pd
from typing import List, Optional, Dict, Any
from datetime import datetime, date

mcp = FastMCP("HotelToolServer")

# Load data
hotels_df = pd.read_excel("./data/hotels.xlsx")
empty_rooms_df = pd.read_excel("./data/empty_rooms_5000.xlsx")
bookings_df = pd.read_excel("./data/hotel_bookings.xlsx")

@mcp.tool()
async def search_hotels(
    city: Optional[str] = None,
    state: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    amenities: Optional[str] = None
) -> Dict[str, Any]:
    """Search hotels by various criteria"""
    result_df = hotels_df.copy()
    
    if city:
        result_df = result_df[result_df['City'].str.contains(city, case=False, na=False)]
    if state:
        result_df = result_df[result_df['State'].str.contains(state, case=False, na=False)]
    if min_price:
        result_df = result_df[result_df['Price'] >= min_price]
    if max_price:
        result_df = result_df[result_df['Price'] <= max_price]
    if amenities:
        result_df = result_df[result_df['Amenities'].str.contains(amenities, case=False, na=False)]
    
    return {
        "count": len(result_df),
        "hotels": result_df.to_dict(orient="records")
    }

@mcp.tool()
async def check_availability(
    hotel_id: str,
    check_in: str,
    check_out: str,
    room_type: Optional[str] = None
) -> Dict[str, Any]:
    """Check room availability for specific dates"""
    # Convert date strings to datetime
    check_in_date = pd.to_datetime(check_in)
    check_out_date = pd.to_datetime(check_out)
    
    # Filter empty rooms for the hotel
    available_rooms = empty_rooms_df[
        (empty_rooms_df['Hotel_ID'] == hotel_id) &
        (empty_rooms_df['Status'] == 'Available')
    ]
    
    if room_type:
        available_rooms = available_rooms[available_rooms['Room_Type'] == room_type]
    
    # Check date overlap
    available_rooms['Available_From'] = pd.to_datetime(available_rooms['Available_From'])
    available_rooms['Available_To'] = pd.to_datetime(available_rooms['Available_To'])
    
    overlapping_rooms = available_rooms[
        (available_rooms['Available_From'] <= check_in_date) &
        (available_rooms['Available_To'] >= check_out_date)
    ]
    
    return {
        "hotel_id": hotel_id,
        "check_in": check_in,
        "check_out": check_out,
        "available_rooms": len(overlapping_rooms),
        "rooms": overlapping_rooms.to_dict(orient="records")
    }

@mcp.tool()
async def get_hotel_details(hotel_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific hotel"""
    hotel_info = hotels_df[hotels_df['Hotel_ID'] == hotel_id]
    
    if hotel_info.empty:
        return {"error": f"Hotel {hotel_id} not found"}
    
    hotel = hotel_info.iloc[0].to_dict()
    
    # Get room types for this hotel
    room_types = hotels_df[hotels_df['Hotel_ID'] == hotel_id]['Room_Type'].unique().tolist()
    
    # Get recent bookings
    recent_bookings = bookings_df[bookings_df['Hotel_ID'] == hotel_id].tail(5)
    
    return {
        "hotel_info": hotel,
        "room_types": room_types,
        "recent_bookings": recent_bookings.to_dict(orient="records")
    }

@mcp.tool()
async def create_booking(
    hotel_id: str,
    room_type: str,
    guest_name: str,
    contact_email: str,
    check_in: str,
    check_out: str,
    guests_count: int
) -> Dict[str, Any]:
    """Create a new hotel booking"""
    # Check if hotel exists
    hotel_exists = hotels_df[hotels_df['Hotel_ID'] == hotel_id]
    if hotel_exists.empty:
        return {"error": f"Hotel {hotel_id} not found"}
    
    # Check availability
    availability = await check_availability(hotel_id, check_in, check_out, room_type)
    if availability['available_rooms'] == 0:
        return {"error": "No rooms available for the selected dates"}
    
    # Generate booking ID
    booking_id = f"B{len(bookings_df) + 1:05d}"
    
    # Calculate total price
    room_price = hotels_df[
        (hotels_df['Hotel_ID'] == hotel_id) & 
        (hotels_df['Room_Type'] == room_type)
    ]['Price'].iloc[0]
    
    check_in_date = pd.to_datetime(check_in)
    check_out_date = pd.to_datetime(check_out)
    nights = (check_out_date - check_in_date).days
    total_price = room_price * nights * guests_count
    
    # Create booking record
    new_booking = {
        "Booking_ID": booking_id,
        "Hotel_ID": hotel_id,
        "Hotel_Name": hotel_exists.iloc[0]['Hotel_Name'],
        "Room_Type": room_type,
        "Guest_Name": guest_name,
        "Contact_Email": contact_email,
        "Check_In_Date": check_in,
        "Check_Out_Date": check_out,
        "Guests_Count": guests_count,
        "Total_Price": total_price,
        "Payment_Status": "Pending"
    }
    
    return {
        "success": True,
        "booking": new_booking,
        "message": f"Booking {booking_id} created successfully"
    }

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### Client Implementation

```python
# client/tool_client.py
import asyncio
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "server.tool_server"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Load MCP tools
            tools = await load_mcp_tools(session)
            
            # Initialize LLM
            google_llm = ChatGoogleGenerativeAI(
                temperature=0,
                model=os.getenv("MODEL", "gemini-2.0-flash"),
                google_api_key=os.getenv("API_KEY")
            )
            
            # Create agent
            system_prompt = SystemMessage(content="""
            You are a hotel management assistant with access to hotel search, 
            availability checking, and booking tools. Help users find and book hotels.
            """)
            
            agent = create_react_agent(model=google_llm, tools=tools)
            
            # Interactive chat loop
            conversation = [system_prompt]
            print("🏨 Hotel Management Assistant")
            print("Type 'exit' to quit\n")
            
            while True:
                try:
                    user_input = input("You: ").strip()
                    if user_input.lower() in {"exit", "quit", "q"}:
                        break
                    if not user_input:
                        continue
                    
                    conversation.append(HumanMessage(content=user_input))
                    state = await agent.ainvoke({"messages": conversation})
                    messages = state.get("messages", [])
                    response = messages[-1].content if messages else "Sorry, I couldn't process that request."
                    
                    print(f"Assistant: {response}\n")
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 3. 📁 Resource Server

### Server Implementation

```python
# server/resource_server.py
from mcp.server.fastmcp import FastMCP
import pandas as pd
import json
from typing import Dict, Any
from datetime import datetime

mcp = FastMCP("HotelResourceServer")

# Load data
hotels_df = pd.read_excel("./data/hotels.xlsx")
empty_rooms_df = pd.read_excel("./data/empty_rooms_5000.xlsx")
bookings_df = pd.read_excel("./data/hotel_bookings.xlsx")

@mcp.resource("hotels://cities")
async def get_cities() -> str:
    """Get list of all cities with hotels"""
    cities = hotels_df['City'].unique().tolist()
    return json.dumps(sorted(cities))

@mcp.resource("hotels://states")
async def get_states() -> str:
    """Get list of all states with hotels"""
    states = hotels_df['State'].unique().tolist()
    return json.dumps(sorted(states))

@mcp.resource("hotels://room-types")
async def get_room_types() -> str:
    """Get list of all available room types"""
    room_types = hotels_df['Room_Type'].unique().tolist()
    return json.dumps(sorted(room_types))

@mcp.resource("hotels://amenities")
async def get_amenities() -> str:
    """Get list of all available amenities"""
    all_amenities = set()
    for amenities_str in hotels_df['Amenities'].dropna():
        amenities = [a.strip() for a in amenities_str.split(',')]
        all_amenities.update(amenities)
    return json.dumps(sorted(list(all_amenities)))

@mcp.resource("hotels://price-ranges")
async def get_price_ranges() -> str:
    """Get price range statistics"""
    price_stats = {
        "min_price": int(hotels_df['Price'].min()),
        "max_price": int(hotels_df['Price'].max()),
        "avg_price": float(hotels_df['Price'].mean()),
        "median_price": float(hotels_df['Price'].median())
    }
    return json.dumps(price_stats)

@mcp.resource("hotels://hotel/{hotel_id}")
async def get_hotel_resource(hotel_id: str) -> str:
    """Get specific hotel information"""
    hotel_info = hotels_df[hotels_df['Hotel_ID'] == hotel_id]
    if hotel_info.empty:
        return json.dumps({"error": f"Hotel {hotel_id} not found"})
    
    hotel = hotel_info.iloc[0].to_dict()
    return json.dumps(hotel)

@mcp.resource("hotels://availability/{hotel_id}")
async def get_hotel_availability(hotel_id: str) -> str:
    """Get availability for a specific hotel"""
    available_rooms = empty_rooms_df[
        (empty_rooms_df['Hotel_ID'] == hotel_id) &
        (empty_rooms_df['Status'] == 'Available')
    ]
    return available_rooms.to_json(orient="records")

@mcp.resource("hotels://bookings/{hotel_id}")
async def get_hotel_bookings(hotel_id: str) -> str:
    """Get bookings for a specific hotel"""
    hotel_bookings = bookings_df[bookings_df['Hotel_ID'] == hotel_id]
    return hotel_bookings.to_json(orient="records")

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### Client Implementation

```python
# client/resource_client.py
import asyncio
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
import json

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "server.resource_server"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("🏨 Hotel Resource Explorer\n")
            
            # List all resources
            resources = await session.list_resources()
            print("Available Resources:")
            for resource in resources.resources:
                print(f"- {resource.uri}")
            
            print("\n" + "="*50 + "\n")
            
            # Get cities
            cities_data = await session.read_resource("hotels://cities")
            cities = json.loads(cities_data.contents)
            print(f"Cities with hotels: {len(cities)}")
            print(f"Sample cities: {cities[:10]}")
            
            # Get room types
            room_types_data = await session.read_resource("hotels://room-types")
            room_types = json.loads(room_types_data.contents)
            print(f"\nAvailable room types: {room_types}")
            
            # Get price ranges
            price_data = await session.read_resource("hotels://price-ranges")
            price_ranges = json.loads(price_data.contents)
            print(f"\nPrice ranges:")
            print(f"Min: ${price_ranges['min_price']}")
            print(f"Max: ${price_ranges['max_price']}")
            print(f"Average: ${price_ranges['avg_price']:.2f}")
            
            # Get specific hotel info
            hotel_data = await session.read_resource("hotels://hotel/H001")
            hotel_info = json.loads(hotel_data.contents)
            print(f"\nHotel H001 details:")
            print(f"Name: {hotel_info['Hotel_Name']}")
            print(f"City: {hotel_info['City']}, {hotel_info['State']}")
            print(f"Price: ${hotel_info['Price']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 4. 🔄 Hybrid Server

### Server Implementation

```python
# server/hybrid_server.py
from mcp.server.fastmcp import FastMCP
import pandas as pd
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

mcp = FastMCP("HotelHybridServer")

# Load data
hotels_df = pd.read_excel("./data/hotels.xlsx")
empty_rooms_df = pd.read_excel("./data/empty_rooms_5000.xlsx")
bookings_df = pd.read_excel("./data/hotel_bookings.xlsx")

# Resources
@mcp.resource("hotels://data")
async def get_hotels_data() -> str:
    """Get all hotels data"""
    return hotels_df.to_json(orient="records")

@mcp.resource("hotels://stats")
async def get_hotel_stats() -> str:
    """Get hotel statistics"""
    stats = {
        "total_hotels": len(hotels_df),
        "total_rooms": len(empty_rooms_df),
        "total_bookings": len(bookings_df),
        "cities": hotels_df['City'].nunique(),
        "states": hotels_df['State'].nunique(),
        "avg_price": float(hotels_df['Price'].mean()),
        "most_common_amenity": hotels_df['Amenities'].mode().iloc[0] if not hotels_df['Amenities'].mode().empty else "N/A"
    }
    return json.dumps(stats, indent=2)

# Tools
@mcp.tool()
async def search_hotels_advanced(
    query: str,
    city: Optional[str] = None,
    state: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    amenities: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Advanced hotel search with natural language query support"""
    result_df = hotels_df.copy()
    
    # Apply filters
    if city:
        result_df = result_df[result_df['City'].str.contains(city, case=False, na=False)]
    if state:
        result_df = result_df[result_df['State'].str.contains(state, case=False, na=False)]
    if min_price:
        result_df = result_df[result_df['Price'] >= min_price]
    if max_price:
        result_df = result_df[result_df['Price'] <= max_price]
    if amenities:
        for amenity in amenities:
            result_df = result_df[result_df['Amenities'].str.contains(amenity, case=False, na=False)]
    
    # Natural language query processing
    query_lower = query.lower()
    if "luxury" in query_lower or "expensive" in query_lower:
        result_df = result_df[result_df['Price'] > result_df['Price'].quantile(0.7)]
    elif "budget" in query_lower or "cheap" in query_lower:
        result_df = result_df[result_df['Price'] < result_df['Price'].quantile(0.3)]
    
    if "pool" in query_lower:
        result_df = result_df[result_df['Amenities'].str.contains("Pool", case=False, na=False)]
    if "spa" in query_lower:
        result_df = result_df[result_df['Amenities'].str.contains("Spa", case=False, na=False)]
    
    return {
        "query": query,
        "results_count": len(result_df),
        "hotels": result_df.to_dict(orient="records")
    }

@mcp.tool()
async def get_availability_report(
    city: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """Generate availability report for hotels"""
    if start_date and end_date:
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        
        # Filter empty rooms by date range
        empty_rooms_df['Available_From'] = pd.to_datetime(empty_rooms_df['Available_From'])
        empty_rooms_df['Available_To'] = pd.to_datetime(empty_rooms_df['Available_To'])
        
        available_rooms = empty_rooms_df[
            (empty_rooms_df['Available_From'] <= start_dt) &
            (empty_rooms_df['Available_To'] >= end_dt) &
            (empty_rooms_df['Status'] == 'Available')
        ]
    else:
        available_rooms = empty_rooms_df[empty_rooms_df['Status'] == 'Available']
    
    if city:
        # Filter by city through hotel data
        city_hotels = hotels_df[hotels_df['City'].str.contains(city, case=False, na=False)]['Hotel_ID'].tolist()
        available_rooms = available_rooms[available_rooms['Hotel_ID'].isin(city_hotels)]
    
    # Generate report
    report = {
        "total_available_rooms": len(available_rooms),
        "hotels_with_availability": available_rooms['Hotel_ID'].nunique(),
        "room_types_available": available_rooms['Room_Type'].value_counts().to_dict(),
        "price_range": {
            "min": int(available_rooms['Price'].min()) if len(available_rooms) > 0 else 0,
            "max": int(available_rooms['Price'].max()) if len(available_rooms) > 0 else 0
        },
        "rooms": available_rooms.to_dict(orient="records")
    }
    
    return report

@mcp.tool()
async def analyze_booking_trends(
    hotel_id: Optional[str] = None,
    days_back: int = 30
) -> Dict[str, Any]:
    """Analyze booking trends and patterns"""
    analysis_df = bookings_df.copy()
    
    if hotel_id:
        analysis_df = analysis_df[analysis_df['Hotel_ID'] == hotel_id]
    
    # Convert dates
    analysis_df['Check_In_Date'] = pd.to_datetime(analysis_df['Check_In_Date'])
    analysis_df['Check_Out_Date'] = pd.to_datetime(analysis_df['Check_Out_Date'])
    
    # Calculate booking metrics
    total_revenue = analysis_df['Total_Price'].sum()
    avg_booking_value = analysis_df['Total_Price'].mean()
    total_bookings = len(analysis_df)
    
    # Room type popularity
    room_type_popularity = analysis_df['Room_Type'].value_counts().to_dict()
    
    # Payment status distribution
    payment_status = analysis_df['Payment_Status'].value_counts().to_dict()
    
    # Guest count distribution
    guest_count_dist = analysis_df['Guests_Count'].value_counts().to_dict()
    
    return {
        "period_days": days_back,
        "hotel_id": hotel_id or "All Hotels",
        "total_revenue": float(total_revenue),
        "avg_booking_value": float(avg_booking_value),
        "total_bookings": total_bookings,
        "room_type_popularity": room_type_popularity,
        "payment_status_distribution": payment_status,
        "guest_count_distribution": guest_count_dist
    }

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### Client Implementation

```python
# client/hybrid_client.py
import asyncio
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
import json

load_dotenv()

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "server.hybrid_server"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Load tools and resources
            tools = await load_mcp_tools(session)
            resources = await session.list_resources()
            
            print("🏨 Hotel Management System - Hybrid Mode")
            print("=" * 50)
            
            # Show available resources
            print("\n📁 Available Resources:")
            for resource in resources.resources:
                print(f"  - {resource.uri}")
            
            # Show available tools
            print(f"\n🔧 Available Tools: {len(tools)}")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Get hotel statistics
            print("\n📊 Hotel Statistics:")
            stats_data = await session.read_resource("hotels://stats")
            stats = json.loads(stats_data.contents)
            print(f"  Total Hotels: {stats['total_hotels']}")
            print(f"  Total Rooms: {stats['total_rooms']}")
            print(f"  Total Bookings: {stats['total_bookings']}")
            print(f"  Cities: {stats['cities']}")
            print(f"  Average Price: ${stats['avg_price']:.2f}")
            
            # Initialize AI agent
            google_llm = ChatGoogleGenerativeAI(
                temperature=0,
                model=os.getenv("MODEL", "gemini-2.0-flash"),
                google_api_key=os.getenv("API_KEY")
            )
            
            system_prompt = SystemMessage(content="""
            You are a comprehensive hotel management assistant with access to both 
            data resources and powerful tools. You can:
            - Search hotels with advanced filtering
            - Generate availability reports
            - Analyze booking trends and patterns
            - Provide business insights and recommendations
            
            Always use the appropriate tool for the user's request.
            """)
            
            agent = create_react_agent(model=google_llm, tools=tools)
            
            # Interactive chat
            conversation = [system_prompt]
            print("\n💬 Interactive Chat (type 'exit' to quit):")
            print("-" * 50)
            
            while True:
                try:
                    user_input = input("\nYou: ").strip()
                    if user_input.lower() in {"exit", "quit", "q"}:
                        break
                    if not user_input:
                        continue
                    
                    conversation.append(HumanMessage(content=user_input))
                    state = await agent.ainvoke({"messages": conversation})
                    messages = state.get("messages", [])
                    response = messages[-1].content if messages else "Sorry, I couldn't process that request."
                    
                    print(f"\nAssistant: {response}")
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"\nError: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 5. 🧪 Testing & Debugging

### Test Script

```python
# test/test_servers.py
import asyncio
import pytest
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters

async def test_data_server():
    """Test data server functionality"""
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "server.data_server"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Test resource listing
            resources = await session.list_resources()
            assert len(resources.resources) > 0
            
            # Test data retrieval
            hotels_data = await session.read_resource("hotels://data")
            assert hotels_data.contents is not None
            
            print("✅ Data server test passed")

async def test_tool_server():
    """Test tool server functionality"""
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "server.tool_server"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Test tool listing
            tools = await session.list_tools()
            assert len(tools.tools) > 0
            
            # Test tool execution
            result = await session.call_tool("search_hotels", {"city": "Miami"})
            assert result.content is not None
            
            print("✅ Tool server test passed")

async def test_hybrid_server():
    """Test hybrid server functionality"""
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "server.hybrid_server"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Test both resources and tools
            resources = await session.list_resources()
            tools = await session.list_tools()
            
            assert len(resources.resources) > 0
            assert len(tools.tools) > 0
            
            print("✅ Hybrid server test passed")

async def run_all_tests():
    """Run all server tests"""
    print("🧪 Running MCP Server Tests")
    print("=" * 40)
    
    try:
        await test_data_server()
        await test_tool_server()
        await test_hybrid_server()
        print("\n🎉 All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
```

### Debug Script

```python
# debug/debug_server.py
import asyncio
import logging
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

async def debug_server(server_module: str):
    """Debug a specific server"""
    print(f"🐛 Debugging {server_module}")
    print("=" * 50)
    
    server_params = StdioServerParameters(
        command="python",
        args=["-m", server_module]
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                print("✅ Server initialized successfully")
                
                # List capabilities
                resources = await session.list_resources()
                tools = await session.list_tools()
                
                print(f"📁 Resources: {len(resources.resources)}")
                for resource in resources.resources:
                    print(f"  - {resource.uri}")
                
                print(f"🔧 Tools: {len(tools.tools)}")
                for tool in tools.tools:
                    print(f"  - {tool.name}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import sys
    server_module = sys.argv[1] if len(sys.argv) > 1 else "server.hybrid_server"
    asyncio.run(debug_server(server_module))
```

## 🚀 Running the Examples

### 1. Data Server
```bash
# Terminal 1: Start server
python -m server.data_server

# Terminal 2: Run client
python client/data_client.py
```

### 2. Tool Server
```bash
# Terminal 1: Start server
python -m server.tool_server

# Terminal 2: Run client
python client/tool_client.py
```

### 3. Resource Server
```bash
# Terminal 1: Start server
python -m server.resource_server

# Terminal 2: Run client
python client/resource_client.py
```

### 4. Hybrid Server
```bash
# Terminal 1: Start server
python -m server.hybrid_server

# Terminal 2: Run client
python client/hybrid_client.py
```

### 5. Run Tests
```bash
python test/test_servers.py
```

### 6. Debug Server
```bash
python debug/debug_server.py server.hybrid_server
```

## 📋 Summary

This guide provides you with:

1. **4 Different Server Types**: Data, Tool, Resource, and Hybrid servers
2. **Complete Client Implementations**: For each server type
3. **Testing Framework**: Automated testing and debugging tools
4. **Real Examples**: Using your hotel management data
5. **Production Ready**: Error handling, logging, and best practices

Each server type serves different purposes:
- **Data Server**: Simple data exposure
- **Tool Server**: Function-based interactions
- **Resource Server**: Resource management
- **Hybrid Server**: Best of all worlds

Choose the server type that best fits your use case and build your client accordingly!
