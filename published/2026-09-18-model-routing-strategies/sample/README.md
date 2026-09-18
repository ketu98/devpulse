## What this demonstrates

This Python script demonstrates model routing strategies for scalable AI systems, where incoming requests are dynamically routed to the most appropriate model based on task type, input complexity, or performance metrics.

## How it works

The script uses a routing function that evaluates input content and selects a model (e.g., small for simple queries, large for complex tasks). It simulates real-time decision logic with configurable thresholds and fallbacks, enabling efficient resource utilization.

## How to run

1. Save the script as `model_routing.py`.
2. Run with: `python model_routing.py`
3. Input sample prompts to see routing decisions in action.

## Things to try

- Modify thresholds to test sensitivity of routing decisions.
- Add new models or task categories to expand routing logic.
- Introduce latency or cost metrics to simulate real-world constraints.
- Test edge cases like ambiguous inputs or malformed requests.
