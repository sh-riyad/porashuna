from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter, Language
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.services.llm import llm
from app.core.config import settings

# Initialize router
ChatRouter = APIRouter()

# Initialize embeddings and vector store
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=settings.GOOGLE_API_KEY
)

# Initialize vector store
vector_store = Chroma(
    persist_directory="./vector_db",
    embedding_function=embeddings
)

# Define the RAG prompt template
RAG_PROMPT = """
You are a helpful AI assistant that answers questions based on the provided context from documents.

Context from documents:
{context}

Question: {question}

Instructions:
- Answer the question based only on the provided context
- If the context doesn't contain enough information to answer the question, say "I don't have enough information in the provided documents to answer this question."
- Be specific and cite relevant information from the context
- Keep your answer clear and concise
- If there are multiple relevant pieces of information, organize them logically

Answer:
"""

# Request/Response models
class ChatRequest(BaseModel):
    question: str
    max_results: Optional[int] = 5

class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: List[dict]
    context_used: str

@ChatRouter.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    """
    Ask a question and get an answer based on the vector database content
    """
    try:
        # Validate input
        if not request.question.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question cannot be empty"
            )

        # Search for relevant documents in vector store
        relevant_docs = vector_store.similarity_search_with_score(
            query=request.question,
            k=request.max_results
        )

        if not relevant_docs:
            return ChatResponse(
                question=request.question,
                answer="I don't have any relevant documents to answer your question. Please upload some documents first.",
                sources=[],
                context_used=""
            )

        # Extract context and sources
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

        # Combine context
        combined_context = "\n\n".join(context_parts)

        # Create the prompt
        prompt = RAG_PROMPT.format(
            context=combined_context,
            question=request.question
        )

        # Generate answer using LLM
        response = llm.invoke(prompt)
        answer = response.content if hasattr(response, 'content') else str(response)

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

@ChatRouter.get("/health")
async def health_check():
    """
    Check if the chat service and vector store are working
    """
    try:
        # Check if vector store has any documents
        sample_search = vector_store.similarity_search("test", k=1)
        doc_count = len(sample_search)
        
        return {
            "status": "healthy",
            "vector_store_connected": True,
            "documents_available": doc_count > 0,
            "estimated_document_count": doc_count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "vector_store_connected": False
        }

@ChatRouter.delete("/clear")
async def clear_vector_store():
    """
    Clear all documents from the vector store (use with caution)
    """
    try:
        # This would require implementing a clear method
        # For now, return a warning
        return {
            "message": "Clear functionality not implemented. Please manually delete the vector_db directory to clear all documents."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear vector store: {str(e)}"
        )

