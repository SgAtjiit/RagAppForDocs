import os
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from .ingest import ingest_pdf
from .query import ask_gemini
from typing import List

# ensure env loads
load_dotenv()

app = FastAPI(title="PDF RAG App with Gemini + Qdrant")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str

@app.post("/ingest")
async def ingest_endpoint(files: List[UploadFile] = File(...)):
    """Upload a PDF and ingest it into Qdrant"""
    try:
        os.makedirs("data", exist_ok=True)
        file_paths = []
        uploaded_files = []
        for file in files:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(
                    status_code=400,
                    detail={"status": "error", "message": f"File {file.filename} is not a PDF"}
                )
                
            file_path = f"data/{file.filename}"
            with open(file_path, "wb") as f:
                f.write(await file.read())
            
            file_paths.append(file_path)
            uploaded_files.append(file.filename)

        ingest_pdf(file_paths)
        return {
            "status": "success",
            "message": f"✅ {len(uploaded_files)} PDF(s) ingested successfully",
            "data": {
                "filenames": uploaded_files,
                "paths": file_paths,
                "count": len(uploaded_files)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": f"Ingestion failed: {str(e)}"}
        )

# @app.post("/ask")
# async def ask_endpoint(request: QuestionRequest):
#     """Ask a question based on ingested PDFs"""
#     try:
#         answer = ask_gemini(request.question)
#         return {
#             "status": "success",
#             "question": request.question,
#             "answer": answer,
#             "source": ["📄 extracted chunks from PDFs"]  # optional: add page info later
#         }
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail={"status": "error", "message": f"Query failed: {str(e)}"}
#         )

@app.post("/ask")
async def ask_endpoint(request: QuestionRequest):
    """Ask a question based on ingested PDFs with source attribution"""
    try:
        result = ask_gemini(request.question)
        
        # ✅ Enhanced response with detailed source info
        return {
            "status": "success",
            "question": request.question,
            "answer": result["answer"],
            "sources": {
                "total_chunks_used": result["total_chunks_used"],
                "source_details": result["sources"],
                "files_referenced": list(set([s["file"] for s in result["sources"]])),
                "pages_referenced": [f"{s['file']} (Page {s['page']})" for s in result["sources"]]
            },
            "metadata": {
                "retrieval_method": "semantic_search",
                "chunks_analyzed": result["total_chunks_used"]
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": f"Query failed: {str(e)}"}
        )


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "🚀 PDF RAG App is running!",
        "endpoints": {
            "upload_pdf": "/ingest",
            "ask_question": "/ask"
        }
    }

# ✅ Auto-run when deployed on Render
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Render injects PORT
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
