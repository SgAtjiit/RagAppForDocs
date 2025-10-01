import os
import uuid
from pypdf import PdfReader
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import chromadb
from .models import get_embedder
from .config import CHROMA_COLLECTION

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
def pdf_to_chunks(pdf_path, chunk_size=500, overlap=50):
    reader = PdfReader(pdf_path)
    full_text = ""

    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            print(f"✅ Page {page_num+1}: Extracted text with PyPDF")
            full_text += text + "\n"
        else:
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
                            full_text += ocr_text + "\n"
                            break
                except Exception as e:
                    print(f"❌ pdf2image/OCR error: {e}")

    if not full_text.strip():
        print("❌ No text could be extracted from any page")
        return []

    words = full_text.split()
    chunks, start = [], 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

# ==============================
# Ingest into Chroma
# ==============================
def ingest_pdf(pdf_path: str):
    collection = get_chroma_collection()

    # Clear collection before ingest
    ids=collection.get()["ids"]
    if ids:
        collection.delete(ids)

    chunks = pdf_to_chunks(pdf_path)
    if not chunks:
        print("❌ No text extracted from PDF, skipping ingestion")
        return

    embedder = get_embedder()
    embeddings = embedder.encode(chunks).tolist()

    collection.add(
        ids=[str(uuid.uuid4()) for _ in chunks],
        embeddings=embeddings,
        documents=chunks
    )

    print(f"✅ Ingested {len(chunks)} chunks into Chroma.")

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
