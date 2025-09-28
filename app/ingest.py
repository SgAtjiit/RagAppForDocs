import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Filter
from pypdf import PdfReader
from .config import QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION
from .models import get_embedder  # ✅ lazy-loaded embedder

def get_qdrant_client():
    return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=60)

def create_collection(qdrant):
    collections = [c.name for c in qdrant.get_collections().collections]
    if QDRANT_COLLECTION not in collections:
        qdrant.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=384, distance="Cosine"),
        )

def pdf_to_chunks(pdf_path, chunk_size=500, overlap=50):
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
    words = full_text.split()
    chunks, start = [], 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks

def ingest_pdf(pdf_path: str):
    qdrant = get_qdrant_client()
    create_collection(qdrant)

    # ✅ Delete all points safely
    qdrant.delete(
        collection_name=QDRANT_COLLECTION,
        points_selector=Filter(must=[])
    )

    chunks = pdf_to_chunks(pdf_path)
    if not chunks:
        raise ValueError("No text extracted from PDF.")
    
    embedder = get_embedder()
    embeddings = embedder.encode(chunks).tolist()

    points = [
        {"id": str(uuid.uuid4()), "vector": vec, "payload": {"text": chunk}}
        for chunk, vec in zip(chunks, embeddings)
    ]

    qdrant.upsert(collection_name=QDRANT_COLLECTION, points=points)
    print(f"✅ Ingested {len(chunks)} chunks into Qdrant.")