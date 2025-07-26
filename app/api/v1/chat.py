from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.services.llm import llm
from app.core.config import settings
from app.core.database import get_db
from app.prompts.chat import RAG_PROMPT
from app.core.vector_store import vector_store
from app.crud.chat_history import store_chat_history, get_chat_history
from app.schemas import ChatRequest, ChatResponse, StoreChatInput, StoreChatResponse, GetChatResponse

ChatRouter = APIRouter()


@ChatRouter.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest, db: Session = Depends(get_db)):

    try:
        if not request.question.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Question cannot be empty")

        # Retrieve relevant documents
        relevant_docs = vector_store.similarity_search_with_score(
            query=request.question,
            k=request.max_results
        )

        # Extract context and metadata
        context_parts = []
        sources = []

        for doc, score in relevant_docs:
            context_parts.append(doc.page_content)
            sources.append({
                "source": doc.metadata.get("source", "Unknown"),
                "chunk_index": doc.metadata.get("chunk_index", 0),
                "similarity_score": round(float(score), 4),
                "content_preview": doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
            })

        # Combine context for RAG prompt
        combined_context = "\n\n".join(context_parts)

        # Get previous conversation
        history = get_chat_history(db)

        # Format the prompt
        prompt = RAG_PROMPT.format(
            context=combined_context,
            question=request.question,
            chat_history=history
        )

        # Call the LLM
        response = llm.invoke(request.question)
        answer = response.content if hasattr(response, 'content') else str(response)

        # Store HumanMessage
        store_chat_history(db, StoreChatInput(
            message_type="HumanMessage",
            message=request.question
        ))

        # Store AIMessage
        store_chat_history(db, StoreChatInput(
            message_type="AIMessage",
            message=answer
        ))

        return ChatResponse(
            question=request.question,
            answer=answer,
            sources=sources,
            context_used=combined_context
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process question: {str(e)}"
        )