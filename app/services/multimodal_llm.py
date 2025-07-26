import google.generativeai as genai
from app.core.config import settings

genai.configure(api_key=settings.GOOGLE_API_KEY)

multimodal_llm = genai.GenerativeModel('gemini-1.5-flash')