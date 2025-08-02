# RAG-Lawyer 🤖⚖️

A powerful **Retrieval-Augmented Generation (RAG)** system designed for legal document analysis and question-answering. Built with FastAPI, Pinecone, and cutting-edge AI technologies to provide accurate, contextual responses to legal queries.

## 🌟 Features

- **📄 Text PDF Processing**: Upload and process text-based legal documents with automatic text extraction
- **🧠 Intelligent Q&A**: Ask questions and get accurate answers from your legal documents
- **⚡ Vector Search**: Fast and efficient document retrieval using Pinecone vector database
- **🌐 RESTful API**: Clean, well-documented API endpoints for easy integration
- **🔄 Real-time Processing**: Instant document processing and query responses
- **📊 Source Citations**: Track and cite sources for transparency and verification

## 🛠️ Technology Stack

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework for building APIs
- **Vector Database**: [Pinecone](https://www.pinecone.io/) - Managed vector database for similarity search
- **Embeddings**: [Google Generative AI](https://cloud.google.com/ai/generative-ai) - High-quality text embeddings
- **Deepseek R1**: [Groq](https://groq.com/) - Fast inference for language models
- **Document Processing**: [LangChain](https://langchain.com/) - Framework for building LLM applications
- **PDF Processing**: [PyPDF2](https://pypdf2.readthedocs.io/) - Text extraction from PDF documents

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   PDF Upload    │───▶│  Text Extraction │───▶│   Embedding     │
│                 │    │   & Chunking     │    │   Generation    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  User Question  │───▶│   Query Vector   │───▶│   Pinecone      │
│                 │    │    Generation    │    │   Search        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Final Answer  │◀───│   LLM Response   │◀───│   Context       │
│  with Sources   │    │   Generation     │    │  Retrieval      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google API key (for embeddings)
- Pinecone API key (for vector storage)
- Groq API key (for LLM responses)
- Text-based PDF documents (scanned PDFs are not supported)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/M-Haris7/RAG-Lawyer.git
   cd RAG-Lawyer
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Configure your `.env` file**
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   PINECONE_API_KEY=your_pinecone_api_key_here
   GROQ_API_KEY=your_groq_api_key_here
   PINECONE_INDEX_NAME=rag-ai-lawyer
   ```

6. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`

## 📖 API Documentation

### Upload Documents

**POST** `/upload_pdfs/`

Upload PDF documents to the system for processing.

```bash
curl -X POST "http://localhost:8000/upload_pdfs/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@legal_document.pdf"
```

**Response:**
```json
{
  "message": "Files processed and vectorstore updated successfully",
  "processed_files": 1,
  "file_names": ["legal_document.pdf"]
}
```

### Ask Questions

The system supports multiple ways to ask questions:

#### 1. GET Request (Query Parameter)
```bash
curl "http://localhost:8000/ask/?question=What are the main provisions of this contract?"
```

#### 2. POST Request (Form Data)
```bash
curl -X POST "http://localhost:8000/ask/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "question=What are the main provisions of this contract?"
```

#### 3. POST Request (JSON)
```bash
curl -X POST "http://localhost:8000/ask/json/" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the main provisions of this contract?"}'
```

**Response:**
```json
{
  "response": "Based on the uploaded contract, the main provisions include...",
  "sources": [
    "legal_document.pdf (Page 1) [Score: 0.892]",
    "legal_document.pdf (Page 3) [Score: 0.845]"
  ],
  "query": "What are the main provisions of this contract?",
  "documents_used": 2
}
```


## 📁 Project Structure

```
RAG-Lawyer/
├── main.py                 # FastAPI application entry point
├── server/
│   ├── routes/
│   │   ├── upload_pdfs.py  # PDF upload endpoints
│   │   └── ask_question.py # Question answering endpoints
│   ├── modules/
│   │   ├── load_vectorstore.py    # Document processing & vector storage
│   │   ├── query_handlers.py      # Query processing logic
│   │   └── llm.py                 # LLM configuration
│   └── middlewares/
│       └── exception_handlers.py  # Error handling
├── uploaded_docs/          # Temporary storage for uploaded files
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # Project documentation
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google Generative AI API key for embeddings | ✅ |
| `PINECONE_API_KEY` | Pinecone API key for vector database | ✅ |
| `GROQ_API_KEY` | Groq API key for LLM responses | ✅ |
| `PINECONE_INDEX_NAME` | Name of the Pinecone index (default: `rag-ai-lawyer`) | ❌ |

### Getting API Keys

1. **Google API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Pinecone API Key**: Sign up at [Pinecone](https://app.pinecone.io/)
3. **Groq API Key**: Get yours from [Groq Console](https://console.groq.com/)

## 🧪 Testing

### Test PDF Upload
```bash
# Test with a sample PDF
curl -X POST "http://localhost:8000/upload_pdfs/" \
  -F "files=@sample_legal_document.pdf"
```

### Test Question Answering
```bash
# Ask a question about uploaded documents
curl "http://localhost:8000/ask/?question=What are the key terms mentioned in the document?"
```

### Run Tests
```bash
python -m pytest tests/
```

## 🔍 Advanced Features

### Custom Chunking Strategies

Modify text chunking parameters in `load_vectorstore.py`:

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # Adjust based on your needs
    chunk_overlap=100    # Overlap between chunks
)
```

## 🐛 Troubleshooting

### Common Issues

1. **"No chunks created from PDF"**
   - The PDF might not contain extractable text
   - Ensure the PDF is a text-based document (not scanned images)
   - Check if the PDF is password-protected or corrupted

2. **"Invalid header value b'Bearer '"**
   - Check that your `GROQ_API_KEY` is properly set in `.env`
   - Ensure the API key is valid and not empty

3. **"Knowledge base is empty"**
   - Upload some PDF documents first using `/upload_pdfs/`
   - Check that the upload was successful

4. **Connection errors**
   - Verify your API keys are valid
   - Check your internet connection
   - Ensure API quotas aren't exceeded


*Disclaimer: This tool is for informational purposes only and does not constitute legal advice. Always consult with qualified legal professionals for legal matters.*
