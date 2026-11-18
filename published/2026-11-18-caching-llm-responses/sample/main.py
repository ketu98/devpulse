import json
import hashlib
import time
from typing import Dict, Any, Optional

# Simple in-memory cache for LLM responses
class LLMResponseCache:
    def __init__(self):
        self.cache: Dict[str, Any] = {}
    
    def get_key(self, prompt: str) -> str:
        """Generate a unique key from prompt using hash"""
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def get(self, prompt: str) -> Optional[str]:
        """Retrieve cached response if exists"""
        key = self.get_key(prompt)
        if key in self.cache:
            return self.cache[key]
        return None
    
    def set(self, prompt: str, response: str) -> None:
        """Store response in cache"""
        key = self.get_key(prompt)
        self.cache[key] = response
    
    def is_cached(self, prompt: str) -> bool:
        """Check if prompt has been cached"""
        return self.get_key(prompt) in self.cache

# Example usage
cache = LLMResponseCache()

# Simulate LLM response generation
def generate_response(prompt: str) -> str:
    # Simulate slow LLM processing
    time.sleep(0.5)
    return f"Response to: {prompt}"

# Demonstrate caching
prompt = "Explain machine learning in simple terms"
cached = cache.get(prompt)
if cached:
    print("✅ Response retrieved from cache")
else:
    response = generate_response(prompt)
    cache.set(prompt, response)
    print("❌ No cache hit, generated new response")
    print(f"Response: {response}")
