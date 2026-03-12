from pydantic import BaseModel
from typing import Optional, List, Any

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    dashboard_context: Optional[Any]

class ChatResponse(BaseModel):
    answer: str
    relevant_data: List[Any] 
    map_focus: Optional[dict] = None
    suggested_followups: Optional[List[str]] = None