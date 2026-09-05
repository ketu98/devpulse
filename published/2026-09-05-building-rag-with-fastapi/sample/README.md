## What this demonstrates  
This POC builds a simple Retrieval-Augmented Generation (RAG) system using FastAPI, demonstrating how to retrieve relevant documents and generate responses using a local LLM. It shows integration of document retrieval, prompt engineering, and real-time API responses.

## How it works  
The system loads a sample text corpus, indexes it with a vector database (e.g., FAISS), and uses a text embedding model to find relevant passages. A FastAPI endpoint accepts user queries, retrieves matching documents, and generates responses via a local LLM (e.g., Ollama or Hugging Face).

## How to run  
1. Install dependencies: `pip install fastapi uvicorn langchain faiss-cpu sentence-transformers`  
2. Clone this repo and run: `uvicorn main:app --reload`  
3. Access the API at `http://localhost:8000/` and send queries via POST.

## Things to try  
- Add more documents to the corpus  
- Swap the embedding model (e.g., all-MiniLM-L6-v2)  
- Integrate a different LLM (e.g., Llama 3)  
- Add query refinement or RAG pipeline optimization  
- Implement authentication or rate limiting for production use
