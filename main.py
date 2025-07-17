#!/usr/bin/env python3
"""
FastAPI main application
"""

from fastapi import FastAPI, Request
import uvicorn
import logging
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from utils import load_messages, save_message, get_call_history

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Create FastAPI app
app = FastAPI(
    title="CallFlow Test API",
    description="A simple FastAPI server with POST endpoints",
    version="1.0.0"
)

# Allow all origins, methods, and headers for development/testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/callflow")
async def callflow(request: Request):
    """
    Handle callflow requests with conversation history
    """
    body = await request.body()
    call_id = request.headers.get("call-id")
    body_text = body.decode('utf-8')

    # Get conversation history for this call_id (handle None case)
    call_messages = get_call_history(call_id) if call_id else []

    # Build LangChain message history for this call_id
    langchain_messages = []
    
    for json_message in call_messages:
        langchain_messages.extend([
            HumanMessage(content=json_message["request"]),
            AIMessage(content=json_message["response"])
        ])
    
    # Add current message
    langchain_messages.append(HumanMessage(content=body_text))

    # Add system message at the beginning
    langchain_messages.insert(0, SystemMessage(content="""
    You are Instant Alfred, a helpful insurance agent working for insurancemarket.ae
    You are given a conversation history and a new message.
    You need to respond to the new message based on the conversation history.
    You are given the following information:
    - The conversation history
    - The new message

    Try to keep the response short and concise and human like with a touch of humor.
    dont indulge in any other conversation except the one related to the insurance.
    """))	

    logger.info(f"Callflow request received - Call ID: {call_id}, Data: {body_text}")
    
    response = llm.invoke(langchain_messages).content
    
    # Save the message data
    message_data = {
        "call_id": call_id,
        "request": body_text,
        "response": response,
        "timestamp": datetime.now().isoformat()
    }
    save_message(message_data)
    
    return response

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    logger.info("Starting FastAPI server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 