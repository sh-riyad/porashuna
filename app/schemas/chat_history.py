from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class StoreChatInput(BaseModel):
    message: str = Field(..., min_length=1, description="The message content")
    message_type: str = Field(..., description="Type of message (e.g., 'user', 'assistant')")

class StoreChatResponse(BaseModel):
    message: str
    message_type: str
    timestamp: datetime

    class Config:
        from_attributes = True

class GetChatResponse(BaseModel):
    message: str
    message_type: str
    timestamp: datetime

    class Config:
        from_attributes = True
