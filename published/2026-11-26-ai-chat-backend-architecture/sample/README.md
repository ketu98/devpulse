## What this demonstrates

This POC demonstrates a scalable AI chat backend using Python, real-time processing, and asynchronous handling. It simulates a chat system that processes user inputs with a lightweight AI model (e.g., a local LLM or mock response) and returns responses instantly via WebSocket.

## How it works

The backend uses FastAPI for routing and real-time communication. User messages are received via HTTP POST, processed asynchronously, and responses are sent back via WebSocket. A simple mock AI model simulates intelligent replies. The system scales by handling multiple concurrent connections efficiently using async event loops.

## How to run

1. Install dependencies: `pip install fastapi uvicorn python-multipart`
2. Save the code to `main.py`
3. Run: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
4. Open a browser or use `curl` to send messages to `http://localhost:8000/chat`

## Things to try

- Add a real LLM (e.g., Ollama or Hugging Face) to generate actual responses.
- Introduce rate limiting or message history to simulate real-world constraints.
- Scale by adding multiple workers or load balancing.
