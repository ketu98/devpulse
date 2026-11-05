def manage_context_window(messages, max_tokens=2048):
    """
    Trims a list of messages to fit within a context window by removing the oldest entries.
    Uses a simple FIFO approach to maintain coherence.
    """
    # Track total token count for messages (simplified: 10 tokens per message)
    total_tokens = sum(len(msg.get("content", "")) + len(msg.get("role", "")) for msg in messages)
    
    # If we exceed max tokens, remove from the end (oldest messages)
    while total_tokens > max_tokens:
        messages.pop(0)  # Remove oldest message
        total_tokens = sum(len(msg.get("content", "")) + len(msg.get("role", "")) for msg in messages)
    
    return messages

# Example usage
if __name__ == "__main__":
    # Sample conversation history
    conversation = [
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm fine, thanks! How can I help you today?"},
        {"role": "user", "content": "Can you explain machine learning?"},
        {"role": "assistant", "content": "Machine learning is a field of AI where systems learn from data."},
        {"role": "user", "content": "What is the difference between supervised and unsupervised learning?"}
    ]
    
    # Apply context window management
    trimmed = manage_context_window(conversation, max_tokens=100)
    
    # Output the result
    for msg in trimmed:
        print(f"{msg['role']}: {msg['content']}")
