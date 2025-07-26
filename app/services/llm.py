from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings



llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, api_key=settings.GOOGLE_API_KEY)

