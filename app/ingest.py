
import os
import uuid
from pypdf import PdfReader
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import chromadb
from .models import get_embedder
from .config import CHROMA_COLLECTION
from typing import List  # ✅ Fixed import
# ==============================
# OCR Setup
# ==============================
possible_tesseract_paths = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\ProgramData\chocolatey\lib\tesseract\tools\tesseract.exe",
    r"C:\tesseract\tesseract.exe"
]

for tess_path in possible_tesseract_paths:
    if os.path.exists(tess_path):
        pytesseract.pytesseract.tesseract_cmd = tess_path
        print(f"✅ Tesseract found at: {tess_path}")
        break

OCR_AVAILABLE = True

# ==============================
# Chroma Setup
# ==============================
def get_chroma_client():
    return chromadb.PersistentClient(path="./chroma_db")

def get_chroma_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(CHROMA_COLLECTION)

# ==============================
# PDF → Text Chunks (OCR fallback)
# ==============================

# ...existing OCR setup code...

def pdf_to_chunks(pdf_path, chunk_size=500, overlap=50):
    reader = PdfReader(pdf_path)
    all_chunks = []
    
    for page_num, page in enumerate(reader.pages):
        page_text = ""
        
        # Try extracting text first
        text = page.extract_text()
        if text and text.strip():
            print(f"✅ Page {page_num+1}: Extracted text with PyPDF")
            page_text = text
        else:
            # OCR fallback
            if OCR_AVAILABLE:
                print(f"⚠️ Page {page_num+1}: No text found, trying OCR...")
                poppler_path = r"C:\poppler-25.07.0\Library\bin"
                try:
                    images = convert_from_path(
                        pdf_path,
                        first_page=page_num+1,
                        last_page=page_num+1,
                        poppler_path=poppler_path
                    )
                    for img in images:
                        ocr_text = pytesseract.image_to_string(img, lang='eng')
                        if ocr_text.strip():
                            print(f"✅ Page {page_num+1}: Extracted text with OCR")
                            page_text = ocr_text
                            break
                except Exception as e:
                    print(f"❌ pdf2image/OCR error: {e}")
        
        # ✅ Create chunks for this page with page number tracking
        if page_text.strip():
            words = page_text.split()
            start = 0
            page_chunk_index = 0
            
            while start < len(words):
                end = min(start + chunk_size, len(words))
                chunk = " ".join(words[start:end])
                if chunk.strip():
                    all_chunks.append({
                        "text": chunk,
                        "page_number": page_num + 1,  # ✅ 1-indexed page number
                        "chunk_index": page_chunk_index,
                        "file_name": os.path.basename(pdf_path)
                    })
                    page_chunk_index += 1
                start += chunk_size - overlap

    return all_chunks

def ingest_pdf(pdf_paths: List[str]):
    collection = get_chroma_collection()

    # Clear collection before ingest
    ids = collection.get()["ids"]
    if ids:
        collection.delete(ids)
        print("🗑️ Cleared existing documents from collection")

    embedder = get_embedder()
    all_chunks = []
    all_metadata = []
    successful_files = 0
    
    # ✅ Process each PDF with page tracking
    for pdf_path in pdf_paths:
        print(f"📄 Processing: {os.path.basename(pdf_path)}")
        chunks_with_pages = pdf_to_chunks(pdf_path)
        
        if not chunks_with_pages:
            print(f"❌ No text extracted from {pdf_path}, skipping this file")
            continue
            
        # ✅ Add detailed metadata for each chunk
        for chunk_data in chunks_with_pages:
            all_chunks.append(chunk_data["text"])
            all_metadata.append({
                "source_file": chunk_data["file_name"],
                "page_number": chunk_data["page_number"],
                "chunk_index": chunk_data["chunk_index"],
                "file_path": pdf_path,
                "chunk_id": f"{chunk_data['file_name']}_p{chunk_data['page_number']}_c{chunk_data['chunk_index']}"
            })
        
        print(f"✅ Extracted {len(chunks_with_pages)} chunks from {os.path.basename(pdf_path)}")
        successful_files += 1
    
    if not all_chunks:
        print("❌ No text extracted from any PDF files")
        return False
        
    # ✅ Generate embeddings and store with page info
    print(f"🔮 Generating embeddings for {len(all_chunks)} chunks...")
    try:
        embeddings = embedder.encode(all_chunks).tolist()
    except Exception as e:
        print(f"❌ Error generating embeddings: {e}")
        return False

    try:
        collection.add(
            ids=[str(uuid.uuid4()) for _ in all_chunks],
            embeddings=embeddings,
            documents=all_chunks,
            metadatas=all_metadata  # ✅ Rich metadata with page info
        )
        
        print(f"✅ Successfully ingested {len(all_chunks)} chunks from {successful_files}/{len(pdf_paths)} PDF(s)")
        
        # ✅ Print detailed summary with page info
        file_summary = {}
        for metadata in all_metadata:
            file = metadata["source_file"]
            if file not in file_summary:
                file_summary[file] = {"chunks": 0, "pages": set()}
            file_summary[file]["chunks"] += 1
            file_summary[file]["pages"].add(metadata["page_number"])
        
        print("📊 Ingestion Summary:")
        for file, info in file_summary.items():
            pages_range = f"{min(info['pages'])}-{max(info['pages'])}"
            print(f"   • {file}: {info['chunks']} chunks across pages {pages_range}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error adding to ChromaDB: {e}")
        return False

# ...rest of existing code...
# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    data_folder = os.path.join(os.path.dirname(__file__), "data")

    if not os.path.exists(data_folder):
        print("❌ 'data' folder not found. Please create a folder named 'data' and put PDFs inside it.")
        exit()

    pdf_files = [f for f in os.listdir(data_folder) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print("❌ No PDF files found in 'data' folder.")
        exit()

    for pdf_file in pdf_files:
        pdf_path = os.path.join(data_folder, pdf_file)
        print(f"\n📄 Processing PDF: {pdf_file}\n")
        ingest_pdf(pdf_path)
