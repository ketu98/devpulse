import json
from typing import Dict, Any

def structure_llm_response(prompt: str, response: str) -> Dict[str, Any]:
    """
    Takes a prompt and raw response, and structures the output into a consistent JSON format.
    Returns a dictionary with metadata and content.
    """
    # Extract key information from response
    extracted = {
        "prompt": prompt,
        "response": response,
        "confidence": 0.8,  # default confidence level
        "metadata": {
            "source": "structured_llm_output",
            "timestamp": "2024-04-05T12:00:00Z",
            "version": "1.0"
        }
    }
    
    # Validate response has content
    if not response.strip():
        extracted["error"] = "No response content provided"
        return extracted
    
    # Add a simple analysis field
    if "help" in response.lower():
        extracted["analysis"] = "User likely seeking assistance"
    elif "example" in response.lower():
        extracted["analysis"] = "User likely asking for an example"
    else:
        extracted["analysis"] = "General response"
    
    return extracted

# Example usage
if __name__ == "__main__":
    prompt = "Explain how a neural network works in simple terms."
    raw_response = "A neural network is like a network of neurons in the brain. It learns by adjusting connections between nodes based on input data."
    
    result = structure_llm_response(prompt, raw_response)
    print(json.dumps(result, indent=2))
