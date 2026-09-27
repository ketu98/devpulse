## What this demonstrates

This POC shows how to build a simple AI agent in Python using reinforcement learning. The agent learns to navigate a grid world by maximizing rewards through trial and error.

## How it works

The agent uses a Q-learning algorithm to update a Q-table based on state-action pairs. It explores the environment, receives feedback (rewards), and adjusts its policy over time. The environment is a 5x5 grid where the agent moves up, down, left, or right to reach a goal.

## How to run

1. Save the code to `agent.py`.
2. Run with: `python agent.py`
3. The agent will learn and display its path after 1000 episodes.

## Things to try

- Change the grid size or reward structure.
- Test with different learning rates or exploration strategies.
- Add a visual display to see the agent’s path in real time.
- Implement a neural network instead of a Q-table for more complex environments.
