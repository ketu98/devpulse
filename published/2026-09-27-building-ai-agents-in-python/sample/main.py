import random
from typing import List, Dict, Any

class SimpleAIAgent:
    def __init__(self, memory: List[str] = None):
        self.memory = memory or []
        self.knowledge = {"greeting": "Hello!", "response": "I'm fine, thanks."}
    
    def think(self, input_text: str) -> str:
        # Simple rule-based reasoning
        if input_text.lower().startswith("hi") or input_text.lower().startswith("hello"):
            return self.knowledge["greeting"]
        elif input_text.lower().startswith("how are you"):
            return self.knowledge["response"]
        else:
            # Default response with memory context
            self.memory.append(input_text)
            return f"Interesting. I remember: {self.memory[-1]}."
    
    def learn(self, experience: Dict[str, Any]):
        # Update knowledge based on experience
        self.knowledge.update(experience)
        return f"Learned: {experience}"

# Example usage
agent = SimpleAIAgent()
print(agent.think("Hi there!"))
print(agent.think("How are you?"))
print(agent.think("What's your favorite color?"))
print(agent.learn({"favorite_color": "blue"}))
