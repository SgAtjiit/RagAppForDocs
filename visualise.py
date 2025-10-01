import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("my_pdfs")

# See all IDs + metadata
results = collection.get(include=["embeddings", "documents", "metadatas"])
print(results)
