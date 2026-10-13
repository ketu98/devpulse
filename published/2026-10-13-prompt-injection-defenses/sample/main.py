# Simple prompt injection defense using input validation and sanitization
# This POC checks for common prompt injection patterns and rejects suspicious inputs

def is_suspicious_prompt(prompt: str) -> bool:
    """Check if a prompt contains common injection patterns"""
    # Common injection indicators
    suspicious_keywords = [
        "system", "execute", "run", "eval", "shell", "command",
        "inject", "payload", "code", "script", "dangerous", "unsafe"
    ]
    
    # Case-insensitive check
    prompt_lower = prompt.lower()
    
    for kw in suspicious_keywords:
        if kw in prompt_lower:
            return True
    
    # Check for common injection syntax
    if "```" in prompt or "code" in prompt_lower:
        return True
    
    return False

def sanitize_prompt(prompt: str) -> str:
    """Sanitize input by removing or replacing dangerous elements"""
    # Replace code-like syntax with neutral text
    prompt = prompt.replace("```", "code_block")
    prompt = prompt.replace("code", "neutral_code")
    return prompt

def safe_prompt_response(user_input: str) -> str:
    """Process user input with defense against prompt injection"""
    if is_suspicious_prompt(user_input):
        return "Error: Input contains suspicious content. Rejected."
    
    # Sanitize before processing
    clean_input = sanitize_prompt(user_input)
    
    # Simulate safe response
    return f"Processing safe input: {clean_input}"

# Example usage
if __name__ == "__main__":
    test_inputs = [
        "Hello, how are you?",
        "Execute: print('hello')",
        "I want to run a shell command",
        "What is the weather today?"
    ]
    
    for inp in test_inputs:
        result = safe_prompt_response(inp)
        print(f"Input: '{inp}' -> {result}")
