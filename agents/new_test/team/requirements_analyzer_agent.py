from agents import Agent

from pydantic import BaseModel
INSTRUCTIONS = (
"You are a technical requirements document analyzer."
"Identify functional requirements, non-functional requirements, and any constraints from the technical requirements document." 
"You should also detect ambiguities and missing information, then output a structured data representation"
"(e.g., functional_requirements, non_functional_requirements, constraints, ambiguities, and missing_details) for use by subsequent agents."
"Additionally, the agent should note any inconsistencies or unclear areas and flag them for further clarification,"
"ensuring its output is comprehensive, consistent, and readily consumable by the rest of the system."
)    

class TechnicalRequirements(BaseModel):
    functional_requirements: list[str]

    non_functional_requirements: list[str]
 
    constraints: list[str]

    ambiguities: list[str]

    missing_details: list[str]

requirements_analyzer_agent = Agent(
    name="Requirements analyzer agent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=TechnicalRequirements
)