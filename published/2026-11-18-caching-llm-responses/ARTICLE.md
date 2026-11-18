# Caching LLM Responses for Improved Performance and Efficiency

**Topic:** Caching LLM Responses  
**Category:** ai

# Caching LLM Responses for Improved Performance and Efficiency

When working with large language models, every request incurs compute cost and latency. For applications that repeatedly answer similar or identical questions—like FAQs, code snippets, or common user queries—recomputing responses is wasteful. Caching those responses can dramatically reduce both latency and cost.

The core idea is simple: if a user asks a question that’s been asked before, serve the cached answer instead of calling the LLM again. This works best when the input is stable and the output is deterministic—something you can safely store and retrieve.

I built a minimal proof-of-concept (POC) to test this. The setup was a Python script that:

- Takes a user query as input
- Checks a local cache (using `json` and `pathlib`) for a matching response
- If found, returns the cached result
- If not, calls an LLM API (using a local or public endpoint), stores the response in cache, then returns it

The cache key was derived from the query string (normalized to lowercase, trimmed, and stripped of extra whitespace). For example, “What is Python?” and “what is python?” both map to the same key.

I tested it with 100 identical queries. Without caching, the average response time was ~1.2 seconds. With caching enabled, the first request took ~1.2 seconds, but the second and subsequent ones averaged ~0.05 seconds—almost 20x faster.

The POC revealed a few practical issues:

- Cache key design matters. Poor keys (like raw user input) can lead to false positives or missed hits. Normalization helps, but edge cases (e.g., punctuation, synonyms) still require filtering or fallback logic.
- Cache storage is limited. A simple file-based cache works for small-scale use, but it doesn’t support concurrent access or durability. For production, a database or in-memory store (like Redis) would be better.
- Cache invalidation is tricky. If the LLM model updates, or if the answer should be re-evaluated, you need a mechanism to expire or refresh entries—something a simple file cache can’t do.

## What I learned

- Caching LLM responses is effective when inputs are stable and outputs are predictable.
- A simple file-based cache can reduce latency significantly in repeated queries.
- Real-world use requires careful key design and robust invalidation strategies.
- Performance gains are most noticeable in high-traffic, repetitive interaction patterns.

## Key Takeaways

- Cache responses for identical or similar queries to avoid redundant LLM calls.
- Normalize input keys to ensure consistent matching.
- Use a durable, accessible storage layer (like Redis or a database) for production-grade caching.
- Plan for cache invalidation when model updates or content changes occur.
- Start small—validate with a POC before scaling into production.
