import asyncio
import json
from typing import List, Dict, Any
from collections import deque

class AIChatBackend:
    def __init__(self, max_history: int = 10):
        self.history: List[Dict[str, Any]] = []
        self.max_history = max_history
        self.buffer: deque = deque(maxlen=max_history)
    
    async def process_message(self, user_input: str) -> str:
        # Simulate AI processing delay
        await asyncio.sleep(0.1)
        
        # Simple response logic (real AI would be more complex)
        response = self.generate_response(user_input)
        
        # Store in history with timestamp
        entry = {
            "user": user_input,
            "ai": response,
            "timestamp": asyncio.get_event_loop().time()
        }
        self.buffer.append(entry)
        
        return response
    
    def generate_response(self, user_input: str) -> str:
        # Simple rule-based response
        if "hello" in user_input.lower():
            return "Hello! How can I help you today?"
        elif "how are you" in user_input.lower():
            return "I'm doing well, thanks for asking!"
        else:
            return "I'm an AI assistant. I can help with basic queries."
    
    def get_history(self) -> List[Dict[str, Any]]:
        return list(self.buffer)

# Example usage
async def main():
    backend = AIChatBackend()
    
    messages = [
        "Hello",
        "How are you?",
        "What time is it?",
        "Goodbye"
    ]
    
    for msg in messages:
        response = await backend.process_message(msg)
        print(f"User: {msg}")
        print(f"AI: {response}\n")
    
    print("History:", backend.get_history())

# Run the example
if __name__ == "__main__":
    asyncio.run(main())
