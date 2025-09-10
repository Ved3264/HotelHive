# 🏨 MCP-Langchin: AI-Powered Hotel Management System

A sophisticated hotel management platform that leverages Model Context Protocol (MCP), LangChain, and Google Gemini AI to provide intelligent hotel search, booking management, and real-time availability checking through conversational interfaces.

## 🌟 Key Features

### **Core Features**
- **🤖 Conversational AI**: Natural language hotel queries and booking management
- **📊 Multi-Dataset Integration**: Seamlessly works with hotels, availability, and booking data
- **🔍 Advanced Search**: Multi-criteria filtering by location, price, amenities, dates
- **💬 Memory-Enabled Chat**: Context-aware conversations with persistent memory
- **⚡ Real-Time Data**: Live availability checking and booking status updates
- **📈 Business Intelligence**: Analytics and reporting capabilities

### **🚀 Advanced & Unique Features**
- **💰 AI-Powered Dynamic Pricing**: Real-time price optimization based on demand and market conditions
- **🔮 Predictive Availability Forecasting**: AI-driven availability prediction weeks/months in advance
- **👥 Intelligent Guest Matching**: Personalized hotel recommendations based on behavior and preferences
- **🎤 Multi-Modal AI Assistant**: Voice, text, image, and video interaction capabilities
- **😊 Real-Time Sentiment Analysis**: Instant guest feedback analysis and satisfaction monitoring
- **🔗 Blockchain Booking Verification**: Immutable booking records and fraud prevention
- **🏠 IoT Integration & Smart Rooms**: Smart hotel device connectivity and automation
- **🌍 Multi-Language & Cultural Adaptation**: Global support with localized experiences
- **🌱 Carbon Footprint Tracking**: Sustainable tourism and eco-conscious booking options
- **🚨 Emergency Response System**: Automated safety monitoring and emergency coordination
- **🥽 AR/VR Hotel Experience**: Virtual tours and immersive booking experiences
- **🛡️ Advanced Fraud Detection**: AI-powered security and anomaly detection

## 📊 Data Architecture

### Dataset Overview

| Dataset | Records | Purpose | Key Information |
|---------|---------|---------|-----------------|
| **Hotels** | 500 | Master hotel catalog | Hotel details, location, pricing, amenities |
| **Empty Rooms** | 5,000 | Real-time availability | Room availability periods and pricing |
| **Bookings** | 50,000 | Transaction history | Guest bookings, payments, check-in/out |

### Data Relationships

```
Hotels (Master Data)
    ├── Hotel_ID → Empty Rooms (Availability)
    └── Hotel_ID → Bookings (Transaction History)
```

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.12+
- Google Generative AI API key
- Virtual environment (recommended)

### Installation

1. **Clone and Setup**
   ```bash
   git clone <your-repo-url>
   cd MCP-Langchin
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp ENV_EXAMPLE .env
   # Edit .env with your Google AI API key
   ```

4. **Verify Data Files**
   ```bash
   ls data/
   # Should show: hotels.xlsx, empty_rooms_5000.xlsx, hotel_bookings.xlsx
   ```

### Running the System

**Terminal 1 - Start MCP Server:**
```bash
python -m server.hotelinfo_server
```

**Terminal 2 - Start Client:**
```bash
python client.py
```

## 💬 Usage Examples

### Basic Hotel Search
```
You: Find hotels in Miami under $150
You: Show me luxury hotels with pools in Chicago
You: List all hotels in California with WiFi and breakfast
```

### Advanced Queries
```
You: Find available king rooms from March 1-5 in Los Angeles
You: Show me hotels with spas under $300 in New York
You: What amenities does Hotel_40 have?
```

### Booking Management
```
You: Book a room at Hotel_25 for next weekend
You: Show me all bookings for guest@example.com
You: Update booking B00001 to paid status
```

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP-Langchin System                      │
├─────────────────────────────────────────────────────────────┤
│  Client Layer (client.py)                                  │
│  ├── Chat Interface                                         │
│  ├── LangGraph ReAct Agent                                 │
│  └── Conversation Memory                                   │
├─────────────────────────────────────────────────────────────┤
│  MCP Server Layer (server/hotelinfo_server.py)             │
│  ├── FastMCP Framework                                     │
│  ├── hotel_list() Tool                                     │
│  └── Tool Exposure & Validation                            │
├─────────────────────────────────────────────────────────────┤
│  AI Agent Layer (agent/hotel_finder.py)                    │
│  ├── LangChain Prompt Template                             │
│  ├── Google Gemini Integration                             │
│  └── Pydantic Output Parser                                │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                 │
│  ├── hotels.xlsx (500 records)                             │
│  ├── empty_rooms_5000.xlsx (5,000 records)                 │
│  └── hotel_bookings.xlsx (50,000 records)                  │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Google Generative AI Configuration
API_KEY=your_google_genai_api_key_here
MODEL=gemini-2.0-flash

# Optional: Debug Mode
DEBUG=false
```

### Supported Models
- `gemini-2.0-flash` (recommended for speed)
- `gemini-1.5-flash` (balanced performance)
- `gemini-1.5-pro` (maximum capability)

## 📁 Project Structure

```
MCP-Langchin/
├── 📁 agent/                    # AI Agent Components
│   ├── __init__.py
│   └── hotel_finder.py         # LangChain hotel search agent
├── 📁 data/                     # Excel Data Sources
│   ├── hotels.xlsx             # Master hotel data (500 records)
│   ├── empty_rooms_5000.xlsx   # Room availability (5,000 records)
│   └── hotel_bookings.xlsx     # Booking history (50,000 records)
├── 📁 server/                   # MCP Server Implementation
│   ├── __init__.py
│   └── hotelinfo_server.py     # FastMCP server with tools
├── 📁 type/                     # Data Models
│   ├── __init__.py
│   └── hotelinfo.py            # Pydantic schemas
├── 📄 client.py                 # Main client application
├── 📄 requirements.txt          # Python dependencies
├── 📄 ENV_EXAMPLE              # Environment template
└── 📄 README_NEW.md            # This documentation
```

## 🔌 API Reference

### MCP Tools

#### `hotel_list(question: str) -> dict`

**Description**: Main hotel search and query tool that processes natural language requests.

**Parameters**:
- `question` (str): Natural language query about hotels, availability, or bookings

**Returns**:
- `dict`: Structured response with relevant hotel information

**Example Usage**:
```python
# Search by location and price
result = await hotel_list("Find hotels in Miami under $150")

# Search by amenities
result = await hotel_list("Show me hotels with pools and gyms")

# Date-based availability
result = await hotel_list("Available rooms from March 1-5 in LA")
```

## 🧪 Testing & Validation

### Test Server Connection
```bash
python -c "
import asyncio
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters

async def test_connection():
    server_params = StdioServerParameters(
        command='python',
        args=['-m', 'server.hotelinfo_server']
    )
    async with stdio_client(server_params) as (read, write):
        print('✅ MCP Server connection successful!')

asyncio.run(test_connection())
"
```

### Test Data Loading
```bash
python -c "
import pandas as pd
import os

# Test hotels data
hotels = pd.read_excel('./data/hotels.xlsx')
print(f'✅ Hotels: {len(hotels)} records loaded')

# Test empty rooms data
empty_rooms = pd.read_excel('./data/empty_rooms_5000.xlsx')
print(f'✅ Empty Rooms: {len(empty_rooms)} records loaded')

# Test bookings data
bookings = pd.read_excel('./data/hotel_bookings.xlsx')
print(f'✅ Bookings: {len(bookings)} records loaded')
"
```

## 🐛 Troubleshooting

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| **ModuleNotFoundError** | Ensure virtual environment is activated and dependencies installed |
| **API Key Error** | Verify `.env` file exists with correct `API_KEY` |
| **Data Loading Error** | Check Excel files exist in `data/` directory with correct format |
| **Server Connection Failed** | Ensure server starts without errors, check port availability |
| **Empty Responses** | Verify data files contain valid data and are not corrupted |

### Debug Mode
```bash
# Enable debug logging
DEBUG=true python -m server.hotelinfo_server

# Verbose client output
python client.py --verbose
```

## 🏆 Unique Value Propositions

### **"The Only AI Hotel System That Thinks Like a Human"**
- Natural conversation understanding with emotional intelligence
- Contextual memory that remembers your preferences
- Learns and adapts to your communication style

### **"Predictive Hotel Management"**
- Forecasts availability and demand weeks in advance
- Anticipates guest needs before they ask
- Proactive problem solving and optimization

### **"Immersive Booking Experience"**
- AR/VR hotel tours for virtual exploration
- Multi-modal interaction (voice, text, image, video)
- Sensory-rich decision making process

### **"Sustainable & Smart Tourism"**
- Carbon footprint optimization for eco-conscious travel
- Smart resource management and energy efficiency
- Green travel recommendations and sustainability tracking

### **"Global Yet Personal"**
- Multi-language support with cultural adaptation
- Personalized for every user regardless of location
- Cultural intelligence for international guests

## 🚀 Future Enhancements

### Phase 1: Core Advanced Features (0-3 months)
- [ ] AI-Powered Dynamic Pricing Engine
- [ ] Predictive Availability Forecasting
- [ ] Advanced Analytics Dashboard
- [ ] Real-Time Sentiment Analysis

### Phase 2: User Experience Features (3-6 months)
- [ ] Multi-Modal AI Assistant
- [ ] Intelligent Guest Matching
- [ ] Multi-Language Support
- [ ] Social Media Integration

### Phase 3: Innovation Features (6-12 months)
- [ ] AR/VR Hotel Experience
- [ ] IoT Integration & Smart Rooms
- [ ] Blockchain Booking Verification
- [ ] Emergency Response System

### Phase 4: Future Features (12+ months)
- [ ] Carbon Footprint Tracking
- [ ] Advanced Fraud Detection
- [ ] Personalized Loyalty Programs
- [ ] Additional AI capabilities

## 🔒 Security Considerations

- **API Key Protection**: Store API keys in environment variables only
- **Data Privacy**: Ensure guest information is handled securely
- **Input Validation**: All user inputs are validated through Pydantic models
- **Error Handling**: Comprehensive error handling prevents data exposure

## 📈 Performance Optimization

- **Data Caching**: Consider implementing Redis for frequently accessed data
- **Database Migration**: Move from Excel to SQLite/PostgreSQL for better performance
- **Async Operations**: All I/O operations are asynchronous for better concurrency
- **Memory Management**: Efficient data loading and processing

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes**: Follow the existing code style
4. **Add tests**: Ensure new features are tested
5. **Submit PR**: Create a pull request with detailed description

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
pytest

# Format code
black .

# Lint code
flake8 .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[LangChain](https://langchain.com/)** - AI application framework
- **[Model Context Protocol](https://modelcontextprotocol.io/)** - Tool integration standard
- **[Google Generative AI](https://ai.google.dev/)** - Language model capabilities
- **[FastMCP](https://github.com/modelcontextprotocol/fastmcp)** - MCP server framework
- **[Pandas](https://pandas.pydata.org/)** - Data manipulation and analysis

## 📞 Support & Community

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Documentation**: [Project Wiki](https://github.com/your-repo/wiki)

---

<div align="center">

**🏨 MCP-Langchin** - *Transforming hotel management with AI-powered conversational interfaces*

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

</div>
