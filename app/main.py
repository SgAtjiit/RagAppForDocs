import os
from dotenv import load_dotenv
# ensure env loads for FastAPI also
load_dotenv()
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from .ingest import ingest_pdf
from .query import ask_gemini


app = FastAPI(title="PDF RAG App with Gemini + Qdrant")

class QuestionRequest(BaseModel):
    question: str

@app.post("/ingest")
async def ingest_endpoint(file: UploadFile = File(...)):
    """Upload a PDF and ingest it into Qdrant"""
    try:
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        file_path = f"data/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())

        ingest_pdf(file_path)
        return {"message": f"{file.filename} ingested successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.post("/ask")
async def ask_endpoint(request: QuestionRequest):
    """Ask a question based on ingested PDFs"""
    try:
        answer = ask_gemini(request.question)
        return {"question": request.question, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "PDF RAG App is running!"}