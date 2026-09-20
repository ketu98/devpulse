import numpy as np
from typing import List

def create_embedding(text: str, dim: int = 128) -> np.ndarray:
    """
    Simple embedding function using hash-based vector representation.
    Demonstrates how text can be converted into a dense vector.
    """
    # Basic hash-based vector: use first 128 characters of text
    # This is not a real embedding model, but illustrates the concept
    vec = np.zeros(dim)
    for i, char in enumerate(text[:dim]):
        # Map character to a value in range [0, 1]
        val = ord(char) / 256.0
        # Distribute across vector dimensions
        idx = i % dim
        vec[idx] += val
    return vec

def similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return dot_product / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0.0

# Example usage
if __name__ == "__main__":
    text1 = "machine learning models"
    text2 = "deep learning algorithms"
    
    emb1 = create_embedding(text1)
    emb2 = create_embedding(text2)
    
    sim = similarity(emb1, emb2)
    print(f"Similarity between '{text1}' and '{text2}': {sim:.3f}")
