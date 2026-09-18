import random
from typing import Dict, Any, Callable

# Simple model routing strategy: route based on input length
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
            return self._select_model("heavy", 0.3)
    
    def _select_model(self, model_name: str, prob: float) -> str:
        if random.random() < prob:
            return model_name
        return random.choice(list(self.models.keys()))

# Example models (dummy functions)
def light_model(input_text: str) -> str:
    return f"Processed short input: {input_text[:10]}..."

def heavy_model(input_text: str) -> str:
    return f"Processed long input: {input_text[:20]}..."

# Usage
router = ModelRouter({
    "light": light_model,
    "heavy": heavy_model
})

# Test with different inputs
test_inputs = ["hello", "this is a longer input that will trigger the heavy model"]
for inp in test_inputs:
    result = router.route(inp)
    print(result)
