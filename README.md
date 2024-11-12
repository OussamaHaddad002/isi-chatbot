------

# Project Documentation

ISIChat is a chatbot and retrieval-augmented generation (RAG) system designed to assist users with document retrieval, Q&A, and chatbot interaction, especially tailored for the Higher Institute of Computer Science environment.

## Project Overview
EZCHAT combines Pinecone for vector storage, TogetherAI API for model-based responses, and Sentence Transformers for text embeddings. Through this setup, the project provides students and university with the ability to interact with the chatbot, ask questions, and retrieve documents related to various topics available within the university's repository.

### Table of Contents
1. [Project Management Strategy](#Project-Management-Strategy)
2. [Key Features](#key-features)
3. [Technology Stack](#technology-stack)
4. [Use Cases](#use-cases)
5. [Models and Technologies Explanation](#models-and-technologies-explanation)
6. [Future Perspectives](#future-perspectives)

---

### 1. Project Management Strategy

To manage this project effectively within a strict 24-hour timeline, we used a highly focused, sprint-based approach, typical of Agile methodology. We identified core features, prioritized rapid development, and conducted continuous testing. This enabled us to deliver functional components efficiently, meeting the project's objectives within the short timeframe.

This version highlights the Agile-inspired approach adapted to the rapid development setting. 
#### Requirements

Install dependencies with:

```bash
pip install os dotenv sentence-transformers pinecone-client together numpy speechrecognition flask flask-cors tempfile langdetect pdfplumber pypdf2 unidecode
```


#### Environment Setup


Create a .env file in the root directory with your API keys:


```
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
TOGETHER_AI_API_KEY=your_together_ai_api_key
```

### 2. Key Features

- **Flask API**: Provides endpoints for chatbot interactions, including text-based and voice-based queries.
- **RAG System**: Combines Pinecone for document retrieval and Together API for generating responses, making the chatbot capable of handling extensive and context-aware information.
- **Speech Recognition**: Allows users to submit voice-based questions and converts them into text queries.
- **PDF Processing**: Enables ingestion of PDF documents, extracts relevant information, and stores it in the Pinecone index for easy retrieval.
  
#### Features Status (DONE)

- **Flask API** - Backend system is ready, enabling user interaction and retrieval through REST endpoints.
- **Pinecone Integration** - Pinecone vector storage and retrieval is complete, storing document vectors and allowing for accurate query matching.
- **Together API Response Generation** - Successfully integrated to provide natural language responses.
- **Speech Recognition** - Users can send voice queries, which are converted to text and processed and vice versa.
- **PDF Processing** - Efficient text extraction from PDF, Excel documents using `pdfplumber` and `PyPDF2`, allowing for large-scale ingestion of ISI's academic content.

### 3. Technology Stack

Each component was carefully chosen based on performance, compatibility, and ease of integration:

| Component              | Technology Used       | Reason for Choice                                                                                                                                 |
|------------------------|-----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| **Backend**            | Flask                 | Lightweight and quick to set up, suitable for small APIs and web apps.                                                                             |
| **Vector Storage**     | Pinecone              | Highly efficient for storing embeddings and fast retrieval. Pinecone also supports academic usage with a free tier.                               |
| **Embedding Model**    | Sentence Transformers (all-MiniLM-L6-v2) | Provides fast and high-quality embeddings, even with limited resources. Chose this over Ollama due to download and connectivity issues at ISI. |
| **Response Generation**| Together API          | Offers free usage for students ($5), providing a cost-effective alternative to OpenAI with similar capabilities.                                 |
| **Speech Recognition** | SpeechRecognition (Google API) | Allows transcription of voice queries with a reliable and widely used service.                                                                    |
| **PDF Processing**     | pdfplumber, PyPDF2    | Enables PDF text extraction, crucial for processing ISI's academic documents.




### 4. Use Cases

- **Document Retrieval**: Students and faculty can search for specific academic documents, and the system retrieves relevant content using Pinecone.
- **Q&A Interaction**: Users can ask questions, and the chatbot provides answers based on ISI’s documents and the Together API response generation.
- **Multilingual Support**: Supports both English and French queries, making it accessible for diverse users at ISI.

### 5. Models and Technologies Explanation

#### Why Together API Over OpenAI
The Together API offers a $5 free credit to students, making it a financially attractive option for testing and experimentation. OpenAI models are highly capable but often come with higher costs and rate limits. Together API models perform competitively in generating answers, making it a suitable alternative for this project.

#### Why all-MiniLM-L6-v2 Over Ollama 3.1
Due to ISI’s network restrictions, downloading the Ollama model would have been challenging and time-consuming. The all-MiniLM-L6-v2 model by Sentence Transformers offers fast embeddings with sufficient accuracy for retrieval tasks, allowing us to implement the RAG system without extensive setup time.

#### Retrieval-Augmented Generation (RAG) Architecture

The RAG architecture allows for efficient, context-aware Q&A. Here’s a high-level overview of how it works:
1. **Query Embedding**: User input is converted to an embedding using all-MiniLM-L6-v2.
2. **Pinecone Retrieval**: The embedding is matched against stored document embeddings in Pinecone to retrieve relevant documents.
3. **Response Generation**: Together API uses the retrieved documents as context to generate an accurate response.

#### Diagram of RAG Workflow

![drive](https://github.com/user-attachments/assets/93183259-52e0-4bb6-8b8e-01d57b6c7700)

### 6. Future Perspectives

**Enhancements**:
1. **Contextual Memory**: Enable the chatbot to remember recent interactions within a session for better conversational flow.
2. **Expanded Language Support**: Integrate additional languages to broaden accessibility.
3. **Offline Support for Embeddings**: Deploy lighter-weight models locally if network issues persist, minimizing dependency on internet speed.

---

This documentation should serve as a detailed overview of the project, explaining each component, the reasoning behind key decisions, and the potential future improvements. Let me know if you need further expansion in any specific area!
