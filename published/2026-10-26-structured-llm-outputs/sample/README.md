## What this demonstrates

This POC shows how structuring LLM outputs improves consistency, reliability, and usability by enforcing a predictable format.

## How it works

The code uses a Python function that takes a prompt and returns a JSON-structured response with fields like `answer`, `confidence`, and `sources`. It leverages OpenAI's API to generate responses, then parses them into a standardized schema using JSON schema validation.

## How to run

1. Install dependencies: `pip install openai python-jsonschema-validator`
2. Set your OpenAI API key in `your_api_key = "your_key_here"`
3. Run the script: `python structured_llm.py`

## Things to try

- Test with different prompts to see how confidence scores vary.
- Add validation rules to reject invalid outputs.
- Extend the schema to include reasoning steps or citations.
- Compare structured vs. unstructured responses for accuracy and consistency.
