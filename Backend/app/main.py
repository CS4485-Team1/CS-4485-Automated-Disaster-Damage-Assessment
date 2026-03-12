from fastapi import FastAPI
from datetime import datetime
import random

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models.models import ChatRequest, ChatResponse
from app.data.data import retrieve_damage_data, format_context
from .services.llm import LLMService
from app.api.endpoints import chat, query
import logging

app = FastAPI(title="Disaster Assessment Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/greet/{name}")
def greet_user(name: str):
    greetings = ["Hello", "Hi", "Hey", "Greetings", "Howdy", "Salutations"]
    greeting = random.choice(greetings)
    return {"message": f"{greeting}, {name}!"}

@app.get("/time")
def get_time():
    now = datetime.now()
    time_str = now.strftime("%I:%M:%S %p")
    return {"current_time": time_str}

app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(query.router, prefix="/api/query", tags=["query"])