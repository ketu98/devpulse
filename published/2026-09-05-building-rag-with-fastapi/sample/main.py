from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from typing import List
import os
import json

app = FastAPI()

# Mock vector store - in real case, this would be a DB or embedding store
mock_store = [
    {"id": 1, "text": "Python is a high-level programming language."},
    {"id": 2, "text": "FastAPI is a modern Python web framework for building APIs."},
    {"id": 3, "text": "RAG systems retrieve relevant information from a knowledge base."}
]

@app.get("/query")
async def query_vector_store(query: str):
    # Simple similarity search - in real RAG, use embeddings
    results = []
    for item in mock_store:
        if query.lower() in item["text"].lower():
            results.append(item)
    return JSONResponse(content={"results": results})

@app.get("/")
async def home():
    return {"message": "RAG system running. Use /query to search."}
