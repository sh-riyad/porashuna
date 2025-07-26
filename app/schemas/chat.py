from pydantic import BaseModel
from typing import List

class ChatRequest(BaseModel):
    question: str
    max_results: int = 5

class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: List[dict]
    context_used: str