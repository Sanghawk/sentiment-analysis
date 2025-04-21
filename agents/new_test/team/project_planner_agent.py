from agents import Agent
from pydantic import BaseModel
from typing import List

# Define a Task model to capture details for each individual task.
class Task(BaseModel):
    description: str
    dependencies: List[str]
    milestone: str
    assigned_agent: str

# Define a ProjectPlan model for the overall project plan.
class ProjectPlan(BaseModel):
    development_roadmap: List[str]
    system_architecture: str
    tasks: List[Task]

# Define instructions for the Project Planner Agent.
INSTRUCTIONS = (
    "You are a project planner agent that receives structured requirement data extracted from a technical requirements document. "
    "Using the provided requirements—which include functional requirements, non-functional requirements—"
    "generate a comprehensive project plan. Your output should include the following elements:\n"
    "1. A development roadmap that outlines the major steps needed to complete the project.\n"
    "2. A suggested system architecture that aligns with the project needs.\n"
    "3. A detailed list of tasks where each task includes:\n"
    "   - A description of the task,\n"
    "   - Its dependencies,\n"
    "   - The milestone it contributes to, and\n"
    "   - The appropriate agent assigned to the task.\n"
    "Make sure your plan is coherent, practical, and addresses all aspects of the provided requirements."
)

# Create the Project Planner Agent instance.
project_planner_agent = Agent(
    name="Project Planner Agent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=ProjectPlan
)