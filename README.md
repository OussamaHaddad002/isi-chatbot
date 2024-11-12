# EZCHAT

A chatbot and retrieval system using Pinecone, Sentence Transformers, Together API, and Flask. This project enables document storage, query retrieval, and response generation using a Retrieval-Augmented Generation (RAG) system.

## 🚀 Features
- **Flask API** for chatbot interaction
- **Pinecone** for vector storage and similarity search
- **Sentence Transformers** for text embeddings
- **Together API** for generating responses
- **Speech Recognition** for transcribing audio queries
- **PDF processing** for document ingestion and vector creation

## 🛠 Requirements

Install dependencies with:

```bash
pip install os dotenv sentence-transformers pinecone-client together numpy speechrecognition flask flask-cors tempfile langdetect pdfplumber pypdf2 unidecode
```

## ⚙️ Environment Setup


Create a .env file in the root directory with your API keys:

```
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
TOGETHER_AI_API_KEY=your_together_ai_api_key
```
## 📁 Project Structure
