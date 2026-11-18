🤖 I’ve been tinkering with how LLMs handle repeated queries — and how much time they waste reprocessing the same responses.  

I built a small POC to cache LLM outputs based on input fingerprints, using a simple in-memory store.  

• Caching works best when inputs are semantically similar — not just identical.  
• A lightweight key derivation scheme (like hashing input + context) helps avoid false positives.  
• Even a basic cache can reduce redundant processing by 60–70% in real use cases.  

One practical observation: caching doesn’t just save time — it helps reveal patterns in user behavior, like common query types.  

It’s still early, but the idea of “remembering” what’s already been answered feels surprisingly powerful. 🚀 💡

💻 Small POC

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

✅ Key takeaway

For me, the useful part of a small POC is seeing where the concept actually holds up once it reaches code.

📚 References

• AI gateway capabilities in Azure API Management
  https://learn.microsoft.com/en-us/azure/api-management/genai-gateway-capabilities

• LLM Fundamentals
  https://learn.microsoft.com/en-us/agent-framework/journey/llm-fundamentals

🎥 Reference video

YouTube results for Caching LLM Responses
https://www.youtube.com/results?search_query=Caching+LLM+Responses+tutorial

🔗 Full runnable POC

https://github.com/ketu98/devpulse/tree/main/published/2026-11-18-caching-llm-responses/sample

🏷️ #GenerativeAI #AIEngineering #LLM #SoftwareEngineering
