## What this demonstrates

This POC shows how text embeddings work in Python, using a simple model to convert text into numerical vectors. Backend engineers can see how natural language becomes vectors for similarity searches, enabling features like search, recommendations, or content grouping.

## How it works

It uses `sentence-transformers` to generate embeddings for sentences. Each sentence is transformed into a fixed-size vector. The cosine similarity between vectors measures how similar two sentences are. The model is lightweight and runs entirely in memory.

## How to run

```bash
pip install sentence-transformers
python embedding_demo.py
```

The script runs a simple test with two sentences and computes their similarity score.

## Things to try

- Change the input sentences to explore different topics.
- Try adding more sentences and compare their embeddings.
- Modify the model (e.g., use `all-MiniLM-L6-v2`) to see performance differences.
- Add a search feature to find similar sentences from a list.
