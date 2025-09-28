import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams
from pypdf import PdfReader
from .config import QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION
from .models import embedder   # ✅ import shared embedder
from qdrant_client.models import Filter
def get_qdrant_client():
    """Initialize Qdrant client lazily."""
    return QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        timeout=60
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

# def ingest_pdf(pdf_path: str):
#     print("Starting the process.......")
#     qdrant = get_qdrant_client()
#     create_collection(qdrant)
#     chunks = pdf_to_chunks(pdf_path)
#     embeddings = embedder.encode(chunks).tolist()   # ✅ using shared embedder

#     points = []
#     for chunk, vector in zip(chunks, embeddings):
#         points.append({
#             "id": str(uuid.uuid4()),
#             "vector": vector,
#             "payload": {"text": chunk},
#         })

#     qdrant.upsert(
#         collection_name=QDRANT_COLLECTION,
#         points=points,
#     )
#     print(f"✅ Ingested {len(chunks)} chunks into Qdrant.")


def ingest_pdf(pdf_path: str):
    qdrant = get_qdrant_client()
    create_collection(qdrant)

    # ✅ Delete all points safely
    qdrant.delete(
        collection_name=QDRANT_COLLECTION,
        points_selector=Filter(must=[]) # ✅ Correct way to select all points
    )

    chunks = pdf_to_chunks(pdf_path)
    if not chunks:
        raise ValueError("No text could be extracted from PDF. Make sure the PDF contains selectable text.")
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

    
    
