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

def retrieve_context(question: str, top_k: int = 5):  # ✅ Increased to get more sources
    collection = get_chroma_collection()
    embedder = get_embedder()
    q_embedding = embedder.encode(question).tolist()

    results = collection.query(
        query_embeddings=[q_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    context_parts  = []
    sources = []
# Don't filter by dist, just take top_k
    for i, (docs, metadata_list, distance) in enumerate(zip(
        results["documents"], results["metadatas"], results["distances"]
    )):
        for doc, metadata, dist in zip(docs, metadata_list, distance):
            source_info = {
                "file": metadata["source_file"],
                "page": metadata["page_number"],
                "chunk_id": metadata.get("chunk_id", f"chunk_{i}"),
                "relevance": round((1 - dist) * 100, 1)
            }
            context_parts.append(f"[Source: {source_info['file']}, Page {source_info['page']}]\n{doc}")
            sources.append(source_info)

        
    context = "\n\n".join(context_parts)
    return context, sources

def ask_gemini(question: str):
    context, sources = retrieve_context(question)
    
    # ✅ Enhanced prompt with source instruction
    prompt = f"""
You are an assistant answering based on document context with SOURCE CITATION.

Context (with sources):
{context}

Question: {question}

Instructions:
- Answer using the provided context
- ALWAYS cite your sources like: "According to [filename, page X]..."
- If multiple sources support the answer, mention all relevant sources
- If you can't find the answer in context, say "This information is not available in the provided documents"
- Be specific about which page contains which information

Answer format:
[Your answer here]

Sources: [List the specific pages you referenced]
"""

    model = get_gemini_model()
    response = model.generate_content(prompt)
    
    # ✅ Return both answer and source metadata
    return {
        "answer": response.text,
        "sources": sources,
        "total_chunks_used": len(sources)
    }