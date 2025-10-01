import google.generativeai as genai
import chromadb
from .config import GEMINI_API_KEY, CHROMA_COLLECTION
from .models import get_embedder  # lazy-loaded embedder

# ==============================
# Chroma Setup
# ==============================
def get_chroma_client():
    return chromadb.PersistentClient(path="./chroma_db")

def get_chroma_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(CHROMA_COLLECTION)

def get_gemini_model():
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel("gemini-2.5-flash")

def retrieve_context(question: str, top_k: int = 3):
    collection = get_chroma_collection()
    embedder = get_embedder()
    q_embedding = embedder.encode(question).tolist()

    results = collection.query(
        query_embeddings=[q_embedding],
        n_results=top_k
    )

    # results["documents"] is a list of list
    context = "\n".join([doc for docs in results["documents"] for doc in docs])
    return context

def ask_gemini(question: str):
    context = retrieve_context(question)
    prompt = f"""
You are an assistant answering based on the following document context.

Context:
{context}

Question:
{question}

Answer clearly and only using the provided context. 
If not in provided context just say this is out of the context
"""
    model = get_gemini_model()
    response = model.generate_content(prompt)
    return response.text
