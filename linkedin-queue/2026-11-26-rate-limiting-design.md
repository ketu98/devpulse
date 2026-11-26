🏗️ Building a rate limiting system from scratch taught me how fragile assumptions can be.  

I explored different approaches—token buckets, leaping counters, and sliding windows—each with trade-offs in latency and fairness.  

I built a small POC that handles burst traffic and enforces per-user limits without blocking requests.  

• Rate limiting must balance fairness and performance—overly strict limits hurt user experience.  
• Simple designs like token buckets work well for basic use cases, but scale poorly under high variance.  
• Real-time feedback loops help detect abuse early, even in small systems.  

One thing that stood out: even small systems need clear boundaries. Otherwise, they grow into unmanageable chaos. 🚀 💡

💻 Small POC

class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, int] = defaultdict(int)
        self.timestamps: Dict[str, int] = defaultdict(int)

    def allow_request(self, key: str) -> bool:
        # Get current time
        now = time.time()

        # Remove old entries outside the window

✅ Key takeaway

For me, the useful part of a small POC is seeing where the concept actually holds up once it reaches code.

📚 References

• AI gateway capabilities in Azure API Management
  https://learn.microsoft.com/en-us/azure/api-management/genai-gateway-capabilities

• Quotas and limits - Microsoft Copilot Studio
  https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-quotas

🎥 Reference video

YouTube results for Rate Limiting Design
https://www.youtube.com/results?search_query=Rate+Limiting+Design+tutorial

🔗 Full runnable POC

https://github.com/ketu98/devpulse/tree/main/published/2026-11-26-rate-limiting-design/sample

🏷️ #SystemDesign #SoftwareArchitecture #BackendEngineering #Scalability
