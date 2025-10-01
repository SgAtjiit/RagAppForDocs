# PDF RAG App with Gemini + ChromaDB

A FastAPI-based Retrieval Augmented Generation (RAG) application that allows you to upload PDF documents and ask questions about their content using Google's Gemini AI model.

## Features

- 📄 **PDF Text Extraction**: Extract text from PDFs using PyPDF2 with OCR fallback
- 🔍 **Semantic Search**: Find relevant content using sentence transformers
- 🤖 **AI-Powered Answers**: Get intelligent responses using Google Gemini
- 🚀 **FastAPI Backend**: Modern, fast web API with automatic documentation
- 💾 **ChromaDB Storage**: Efficient vector database for document embeddings
- 🖼️ **OCR Support**: Extract text from image-based PDFs using Tesseract

## Prerequisites

- Python 3.8 or higher
- Google Gemini API key
- Tesseract OCR (for image-based PDFs)
- Poppler (for PDF to image conversion)

## Installation & Setup

### 1. Clone or Download the Project

```bash
git clone <your-repo-url>
cd RagApp
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Windows Command Prompt:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install External Dependencies

#### Install Tesseract OCR

**Windows (Chocolatey):**
```powershell
# Run as Administrator
choco install tesseract
```

**Windows (Manual):**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to `C:\Program Files\Tesseract-OCR\`
3. Add to PATH: `C:\Program Files\Tesseract-OCR\`

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

**Mac:**
```bash
brew install tesseract
```

#### Install Poppler

**Windows (Chocolatey):**
```powershell
choco install poppler
```

**Windows (Manual):**
1. Download from: https://github.com/oschwartz10612/poppler-windows/releases/
2. Extract to `C:\poppler-25.07.0\`
3. Add to PATH: `C:\poppler-25.07.0\Library\bin`

### 5. Create Required Folders

```bash
# Create data folder for PDFs
mkdir app/data

# Create environment file
touch app/.env  # Linux/Mac
# or create manually on Windows
```

### 6. Setup Environment Variables

Create `app/.env` file with your Google Gemini API key:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

**To get Gemini API key:**
1. Go to: https://makersuite.google.com/app/apikey
2. Create new API key
3. Copy and paste into `.env` file

### 7. Project Structure

Your project should look like this:

```
RagApp/
├── app/
│   ├── __init__.py
│   ├── .env                 # Your environment variables
│   ├── config.py           # Configuration settings
│   ├── main.py             # FastAPI application
│   ├── models.py           # Embedding models
│   ├── ingest.py           # PDF processing and ingestion
│   ├── query.py            # Query processing with Gemini
│   └── data/               # Put your PDF files here
│       └── your_pdfs.pdf
├── chroma_db/              # ChromaDB storage (auto-created)
├── venv/                   # Virtual environment
├── requirements.txt        # Python dependencies
├── visualise.py           # Database visualization script
└── README.md              # This file
```

## Usage

### 1. Start the Server

```bash
# Make sure virtual environment is activated
uvicorn app.main:app --reload
```

The server will start at: http://127.0.0.1:8000

### 2. Access the Interactive API Documentation

Open your browser and go to: http://127.0.0.1:8000/docs

### 3. Upload PDF Documents

1. Go to `/ingest` endpoint in the docs
2. Click "Try it out"
3. Choose a PDF file
4. Click "Execute"

### 4. Ask Questions

1. Go to `/ask` endpoint in the docs
2. Click "Try it out"
3. Enter your question in the JSON body:
   ```json
   {
     "question": "What is this document about?"
   }
   ```
4. Click "Execute"

### 5. Alternative: Using Command Line

```bash
# Health check
curl http://127.0.0.1:8000/

# Upload PDF (replace with your file path)
curl -X POST "http://127.0.0.1:8000/ingest" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/document.pdf"

# Ask question
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic of this document?"}'
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/ingest` | POST | Upload and process PDF |
| `/ask` | POST | Ask questions about uploaded PDFs |
| `/docs` | GET | Interactive API documentation |

## Configuration

### Embedding Model
The app uses `paraphrase-multilingual-MiniLM-L12-v2` for embeddings. You can change this in `app/models.py`:

```python
_embedder = SentenceTransformer("all-MiniLM-L6-v2")  # Smaller, faster model
```

### Gemini Model
Using `gemini-2.5-flash` (change in `app/query.py` if needed):

```python
return genai.GenerativeModel("gemini-1.5-flash")  # Alternative model
```

### Chunk Settings
Adjust text chunking in `app/ingest.py`:

```python
def pdf_to_chunks(pdf_path, chunk_size=500, overlap=50):
```

## Troubleshooting

### Common Issues

1. **Tesseract not found error:**
   - Ensure Tesseract is installed and in PATH
   - Check paths in `app/ingest.py`

2. **Poppler not found error:**
   - Install Poppler and add to PATH
   - Update path in `app/ingest.py` if needed

3. **Gemini API error:**
   - Check your API key in `.env`
   - Ensure you have Gemini API access

4. **Module import errors:**
   - Ensure virtual environment is activated
   - Install missing dependencies: `pip install -r requirements.txt`

### Debug Commands

```bash
# Check ChromaDB contents
python visualise.py

# Test PDF ingestion directly
python -m app.ingest

# Check if Tesseract is working
tesseract --version

# Check if Poppler is working
pdftoppm -h
```

## Development

### Adding New Features

1. **New endpoints**: Add to `app/main.py`
2. **New processing**: Modify `app/ingest.py`
3. **New AI models**: Update `app/query.py`

### Testing

```bash
# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Deployment

### Local Production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Cloud Deployment (Render, Heroku, etc.)

The app includes auto-configuration for cloud deployment. Set these environment variables:

- `GEMINI_API_KEY`: Your Google Gemini API key
- `PORT`: Will be automatically set by cloud providers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

If you encounter any issues:

1. Check the troubleshooting section
2. Review the error logs
3. Ensure all dependencies are properly installed
4. Create an issue with detailed error information

---

**Happy RAG-ing! 🚀📄🤖**