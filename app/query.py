from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import google.generativeai as genai 
from .config import GEMINI_API_KEY, QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION 

print("Loading embedder.....")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def get_qdrant_client():
    return QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )

def get_gemini_model():
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel("gemini-2.5-flash")

def retrieve_context(question: str, top_k: int = 3):
    print("Retrieving context......")
    qdrant = get_qdrant_client()
    q_embedding = embedder.encode(question).tolist()

    search_results = qdrant.query_points(
        collection_name=QDRANT_COLLECTION,
        query=q_embedding,
        limit=top_k,
        with_payload=True
    ).points

    context = "\n".join([hit.payload["text"] for hit in search_results])
    return context

def ask_gemini(question: str):
    print("Asking Gemini.......")
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
