from langchain_chroma import Chroma
from app.services.embedding_models import embeddings

vector_store = Chroma(
    persist_directory="./database",
    embedding_function=embeddings
)