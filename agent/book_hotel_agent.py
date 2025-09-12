from langchain_google_genai import ChatGoogleGenerativeAI
from agent.prompts import build_create_booking_prompt
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
import os
from dotenv import load_dotenv
load_dotenv()

models = os.getenv("MODEL")
api_key = os.getenv("API_KEY")
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

llm = ChatGoogleGenerativeAI(model=models, google_api_key=api_key, temperature=0)

def check_hotel_availability_agent(user_id:str):
    prompt_template = build_create_booking_prompt()
    memory = None
    try:
        session_id = user_id or "default-session"
        history = RedisChatMessageHistory(session_id=session_id, url=redis_url)
        memory = ConversationBufferMemory(
            chat_memory=history,
            return_messages=True,
            memory_key="history",
            input_key="input",
        )
    except Exception:
        memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="history",
            input_key="input",
        )
    chain = (
        RunnablePassthrough()
        | prompt_template
        | llm
        | StrOutputParser()
    )
    
    return chain,memory