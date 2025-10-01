# from sentence_transformers import SentenceTransformer

# print("Loading embedding model...")
# embedder = SentenceTransformer("all-MiniLM-L6-v2")
from sentence_transformers import SentenceTransformer

_embedder = None

def get_embedder():
    """Lazy load embedding model to save memory."""
    global _embedder
    if _embedder is None:
        print("Loading embedding model...")
        _embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return _embedder
