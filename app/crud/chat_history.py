from sqlalchemy.orm import Session
from typing import List
from langsmith import traceable
from app.schemas.chat_history import StoreChatInput, StoreChatResponse, GetChatResponse
from app.models.chat_history import ChatHistory

@traceable(name="store_chat_history")
def store_chat_history(db: Session, entry: StoreChatInput) -> StoreChatResponse:
    chat = ChatHistory(
        message=entry.message,
        message_type=entry.message_type,
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return StoreChatResponse.model_validate(chat)


@traceable(name="get_chat_history")
def get_chat_history(db: Session) -> List[GetChatResponse]:
    chat_entries = db.query(ChatHistory).order_by(ChatHistory.timestamp).all()
    
    return [GetChatResponse.model_validate(entry) for entry in chat_entries]
