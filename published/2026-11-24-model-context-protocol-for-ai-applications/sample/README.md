## What this demonstrates

This POC demonstrates a lightweight Model Context Protocol (MCP) in Python that allows AI models to receive and manage contextual data—such as user preferences, session history, or environment variables—during inference. The protocol ensures consistent, structured context delivery across model calls.

## How it works

The MCP defines a simple JSON schema for context data. A Python class validates and formats input, then passes structured context to a mock AI model function. The model returns a response incorporating the context, simulating real-world AI behavior with contextual awareness.

## How to run

1. Save the script as `mcp_poc.py`.
2. Run with: `python mcp_poc.py`
3. The script will prompt for context input and display a model response.

## Things to try

- Add new context fields (e.g., "user_id", "location").
- Modify the model response to include dynamic logic based on context.
- Test edge cases like invalid or missing context fields.
- Extend to support multiple contexts or session persistence.
