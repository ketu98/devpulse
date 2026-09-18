🤖 I’ve been tinkering with how to route requests to different AI models in a system—without overloading any one model.  

I built a small POC that routes incoming queries based on task type, model size, and latency thresholds.  

• Use lightweight models for simple tasks like sentiment analysis  
• Route complex queries to larger models with confidence scoring  
• Prioritize low-latency paths when user experience is critical  

One thing that stood out: even small routing decisions can shift performance noticeably.  

It’s not about choosing the “best” model—just the right one for the moment. 🚀💡

💻 Small POC

class ModelRouter:
    def __init__(self, models: Dict[str, Callable]):
        self.models = models
        self.weights = {k: 1.0 / len(models) for k in models}

    def route(self, input_text: str) -> str:
        # Route based on input length: short inputs to lightweight model, long to heavy
        if len(input_text) < 50:
            # Use lightweight model for short inputs
            return self._select_model("light", 0.7)
        else:
            # Use heavy model for long inputs

✅ Key takeaway

For me, the useful part of a small POC is seeing where the concept actually holds up once it reaches code.

📚 References

• Model router for Microsoft Foundry concepts - Microsoft Foundry
  https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-router

• Microsoft Certified: Azure Network Engineer Associate - Certifications
  https://learn.microsoft.com/en-us/credentials/certifications/azure-network-engineer-associate/

🎥 Reference video

YouTube results for Model Routing Strategies
https://www.youtube.com/results?search_query=Model+Routing+Strategies+tutorial

🔗 Full runnable POC

https://github.com/ketu98/devpulse/tree/main/published/2026-09-18-model-routing-strategies/sample

🏷️ #GenerativeAI #AIEngineering #LLM #SoftwareEngineering
