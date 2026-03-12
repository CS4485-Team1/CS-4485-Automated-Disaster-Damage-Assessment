from fastapi import FastAPI, HTTPException, APIRouter
from app.models.models import ChatResponse, ChatRequest
from app.services.llm import LLMService
from app.data.data import retrieve_damage_data, format_context, format_relevant_data
from app.services.query_parser import QueryParser
from colorama import Fore, Style, init
from pydantic import BaseModel
import logging
import time
import json

router = APIRouter()

@router.get("/")
def test():
    return {"Bot": "Greetings"}

@router.post("/temp")
def chat():
    return "Yo"


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        print(f"Request: {request}")

        llm = LLMService()

        records = retrieve_damage_data(request.query)
        print(f"Records: {records}")

        context = format_context(records)
        print(f"Context: {context}")

        answer = await llm.call_with_context(request.query, context)

        map_focus = None
        if records:
            first = records[0]
            regions = first.get("critical_regions", [])

            if regions:
                center = regions[0].get("center")

                if center:
                    map_focus = {
                        "x": center[0],
                        "y": center[1],
                        "zoom": 4
                    }

        return ChatResponse(
            answer=answer,
            relevant_data=format_relevant_data(records),
            map_focus=map_focus,
            suggested_followups=[
                "Show destroyed buildings",
                "What's the damage in Springfield?",
                "Compare Springfield and Shelbyville"
            ]
        )

    except Exception as e:
        logging.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
    
