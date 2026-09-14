## What this demonstrates

This POC shows a lightweight, efficient document ingestion pipeline that extracts text from PDFs and TXT files and prepares it for AI training. It uses Python to parse common formats and outputs clean, structured text.

## How it works

The pipeline loads documents via `PyPDF2` and `pathlib`, extracts text, normalizes whitespace, and stores content in a list. It handles errors gracefully and logs progress. Output is a list of strings, ready for AI model input.

## How to run

```bash
python ingest.py
```

Ensure you have `PyPDF2` installed:  
```bash
pip install PyPDF2
```

Place sample files (`sample.pdf`, `sample.txt`) in the same directory.

## Things to try

- Add support for DOCX or JSON files.  
- Integrate with a vector database (e.g., FAISS).  
- Add metadata extraction (author, date).  
- Implement streaming for large files.  
- Add logging or progress bars for long runs.  

This pipeline is designed for speed and simplicity, ideal for early AI training workflows.
