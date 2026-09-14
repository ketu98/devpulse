import os
from pathlib import Path
from typing import List
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveTextSplitter
from langchain.schema import Document

def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text from a PDF file."""
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def split_text_into_chunks(text: str, chunk_size: int = 512) -> List[Document]:
    """Split text into manageable chunks for AI processing."""
    splitter = RecursiveTextSplitter(chunk_size=chunk_size, chunk_overlap=64)
    chunks = splitter.split_text(text)
    return [Document(page_content=chunk) for chunk in chunks]

def ingest_document(pdf_path: Path) -> List[Document]:
    """Main ingestion pipeline: extract and split document."""
    text = extract_text_from_pdf(pdf_path)
    return split_text_into_chunks(text)

# Example usage
if __name__ == "__main__":
    pdf_path = Path("example.pdf")
    if pdf_path.exists():
        documents = ingest_document(pdf_path)
        print(f"Processed {len(documents)} chunks from {pdf_path.name}")
    else:
        print("PDF file not found.")
