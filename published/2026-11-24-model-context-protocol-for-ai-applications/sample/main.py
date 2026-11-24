import json
from typing import Dict, Any

class ModelContextProtocol:
    def __init__(self, context: Dict[str, Any]):
        self.context = context
        self._validate()

    def _validate(self):
        """Ensure required fields are present"""
        required = ['user_id', 'session_id', 'timestamp']
        for field in required:
            if field not in self.context:
                raise ValueError(f"Missing required field: {field}")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize context to a dictionary"""
        return self.context.copy()

    def to_json(self) -> str:
        """Serialize context to JSON string"""
        return json.dumps(self.context, indent=2)

# Example usage
if __name__ == "__main__":
    sample_context = {
        "user_id": "u12345",
        "session_id": "s67890",
        "timestamp": "2023-10-05T12:00:00Z",
        "ip_address": "192.168.1.1",
        "device": "mobile"
    }
    
    ctx = ModelContextProtocol(sample_context)
    print("Context as dict:")
    print(ctx.to_dict())
    print("\nContext as JSON:")
    print(ctx.to_json())
