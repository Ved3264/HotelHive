# api_server.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
import json
import logging
import subprocess
import sys
from pathlib import Path
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="HotelHive Chat API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.client_process = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New connection. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Connection closed. Total connections: {len(self.active_connections)}")

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

async def run_client_with_input(user_input: str) -> str:
    """Run the client.py with the given input and capture the output"""
    try:
        input_file = "temp_input.txt"
        with open(input_file, "w") as f:
            f.write(user_input + "\nexit\n")
        
        result = subprocess.run([
            sys.executable, "client.py"
        ], 
        input=f"{user_input}\nexit\n", 
        text=True, 
        capture_output=True,
        timeout=30)
        
        output_lines = result.stdout.split('\n')
        agent_response = ""
        capture = False
        
        for line in output_lines:
            if "Agent:" in line:
                capture = True
                response_part = line.replace("Agent:", "").replace("Agent:\n", "").strip()
                if response_part:
                    agent_response += response_part + " "
            elif capture and line.strip() and not line.startswith("You:"):
                agent_response += line.strip() + " "
        
        agent_response = agent_response.strip()
        if not agent_response:
            agent_response = "I'm sorry, I didn't get a response. Please try again."
        
        return agent_response
        
    except subprocess.TimeoutExpired:
        return "The request timed out. Please try a simpler query."
    except Exception as e:
        logger.error(f"Error running client: {e}")
        return f"Error processing your request: {str(e)}"

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data["type"] == "message":
                user_message = message_data["content"]
                
                await websocket.send_json({
                    "type": "typing",
                    "isTyping": True
                })
                
                
                try:
                    response = await run_client_with_input(user_message)
                    
                    
                    await websocket.send_json({
                        "type": "message",
                        "content": response,
                        "sender": "bot"
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    await websocket.send_json({
                        "type": "message",
                        "content": "Sorry, I encountered an error processing your request.",
                        "sender": "bot"
                    })
                
                await websocket.send_json({
                    "type": "typing",
                    "isTyping": False
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/message")
async def send_message(message: dict):
    """REST endpoint for sending messages"""
    try:
        user_input = message.get("content", "")
        if not user_input:
            return {"error": "No message content provided"}
        
        response = await run_client_with_input(user_input)
        return {"response": response}
        
    except Exception as e:
        logger.error(f"Error in REST API: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)