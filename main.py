from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from app.api.v1.document import DocumentRouter
from app.core.config import settings
from app.core.database import engine, Base
import uvicorn
from app.api.v1.chat import ChatRouter

app = FastAPI(
        title="Porashuna",
        description="Porashun AI Backend API",
        version="1.0.0"
    )

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    from app.models.chat_history import ChatHistory
    Base.metadata.create_all(bind=engine)

app.include_router(DocumentRouter, prefix="/document", tags=["Document"])
app.include_router(ChatRouter, prefix="/chat", tags=["Chat"])


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")