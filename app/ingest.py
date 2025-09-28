import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams
from sentence_transformers import SentenceTransformer 
from pypdf import PdfReader
from .config import QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION

# load embedding model once
print("Loading embedding Model")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def get_qdrant_client():
    """Initialize Qdrant client lazily (when called, not on import)."""
    return QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )

def create_collection(qdrant):
    print("Checking and creating collections.....")
    collections = [c.name for c in qdrant.get_collections().collections]
    if QDRANT_COLLECTION not in collections:
        qdrant.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=384, distance="Cosine"),
        )

def pdf_to_chunks(pdf_path, chunk_size=500, overlap=50):
    print("Converting your pdf to chunks......")
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
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks

def ingest_pdf(pdf_path: str):
    print("Starting the process.......")
    qdrant = get_qdrant_client()
    create_collection(qdrant)
    chunks = pdf_to_chunks(pdf_path)
    embeddings = embedder.encode(chunks).tolist()

    points = []
    for chunk, vector in zip(chunks, embeddings):
        points.append({
            "id": str(uuid.uuid4()),
            "vector": vector,
            "payload": {"text": chunk},
        })

    qdrant.upsert(
        collection_name=QDRANT_COLLECTION,
        points=points,
    )
    print(f"✅ Ingested {len(chunks)} chunks into Qdrant.")
