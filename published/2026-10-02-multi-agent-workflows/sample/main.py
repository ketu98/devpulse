import asyncio
from typing import List, Dict, Any

class Agent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
    
    async def execute(self, task: str) -> str:
        # Simulate work with a delay
        await asyncio.sleep(0.1)
        return f"{self.name} completed: {task}"

async def create_workflow(agents: List[Agent], tasks: List[str]) -> Dict[str, Any]:
    results = {}
    for task in tasks:
        # Assign tasks to agents based on role
        assigned_agent = None
        for agent in agents:
            if task.startswith("analyze") and agent.role == "analyzer":
                assigned_agent = agent
                break
            elif task.startswith("validate") and agent.role == "validator":
                assigned_agent = agent
                break
        
        if assigned_agent:
            result = await assigned_agent.execute(task)
            results[task] = result
        else:
            results[task] = f"No agent found for task: {task}"
    
    return results

# Example usage
async def main():
    agents = [
        Agent("Alice", "analyzer"),
        Agent("Bob", "validator"),
    ]
    tasks = ["analyze data", "validate output", "analyze data"]
    results = await create_workflow(agents, tasks)
    print(results)

# Run the workflow
if __name__ == "__main__":
    asyncio.run(main())
