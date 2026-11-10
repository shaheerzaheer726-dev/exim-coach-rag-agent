import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

# ---- Chat model (OpenRouter) ----
# Browse https://openrouter.ai/models, filter by "free", and paste the exact ID here.
CHAT_MODEL = "liquid/lfm-3-1.7b:free"

llm = ChatOpenAI(
    model=CHAT_MODEL,
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0.5,
    max_tokens=8000,
)

# ---- Embeddings (HuggingFace, runs locally) ----
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    encode_kwargs={"normalize_embeddings": True},
)