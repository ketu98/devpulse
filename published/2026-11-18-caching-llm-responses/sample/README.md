## What this demonstrates

This POC shows how caching LLM responses improves performance and reduces API costs by storing and reusing previous outputs.

## How it works

The script uses a simple in-memory cache (dictionary) to store responses based on input prompts. When a prompt is received, it checks if the response is already cached. If yes, it returns the cached result; if no, it calls an LLM (simulated via a placeholder function) and stores the result in the cache.

## How to run

1. Save the code as `cache_llm.py`.
2. Run with: `python cache_llm.py`.

The script will prompt for input and demonstrate cached vs. fresh responses.

## Things to try

- Add a file-based cache to persist results across sessions.
- Test with repeated prompts to observe performance gains.
- Modify the cache key to include context or metadata for better precision.
- Try different cache sizes or eviction strategies (e.g., LRU).
