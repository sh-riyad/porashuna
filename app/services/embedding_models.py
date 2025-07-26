# Initialize embeddings and vector store
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.core.config import settings

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=settings.GOOGLE_API_KEY
)