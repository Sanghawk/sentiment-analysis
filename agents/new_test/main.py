import asyncio
from team.requirements_analyzer_agent import requirements_analyzer_agent
from agents import Agent, Runner, set_default_openai_key, trace, TResponseInputItem, ItemHelpers
# from manager import GeneralManager
from dataclasses import dataclass
from typing import Literal


from team.requirements_analyzer_agent import requirements_analyzer_agent
@dataclass
class EvaluationFeedback:
    score: Literal["pass", "provides_details"]
    clarifications: str


evaluator = Agent[None](
    name="evaluator",
    instructions=(
        "You provide answers to the missing and ambiguous technical requirements for a project."
        "If there are ambiguities or missing details, provide the answers so that they are no longer missing or ambiguous."
        "Never give it a pass on the first try."
        "If there are no more ambiguities or missing details, you can pass."
    ),
    output_type=EvaluationFeedback,
    model="gpt-4o-mini"
)


async def main() -> None:
    # hello_world_dir = "./input/technical_requirements_doc-helloworld.txt" 
    # todo_app_dir = "./input/todo_app.txt" 
    # with open(todo_app_dir, "r", encoding="utf-8") as file:
    #     content = file.read()

    # tech_req_txt = content
    # await GeneralManager().run(tech_req_txt)
    msg = input("What do you want to make? ")
    input_items: list[TResponseInputItem] = [{"content": msg, "role": "user"}]

    latest_requirements: str | None = None

    # We'll run the entire workflow in a single trace
    with trace("LLM as a judge"):
        while True:
            requirements = await Runner.run(
                requirements_analyzer_agent,
                input_items,
            )

            input_items = requirements.to_input_list()
            latest_requirements = ItemHelpers.text_message_outputs(requirements.new_items)
            print("Story outline generated")

            evaluator_result = await Runner.run(evaluator, input_items)
            result: EvaluationFeedback = evaluator_result.final_output

            print(f"Evaluator score: {result.score}")

            if result.score == "pass":
                print("Story outline is good enough, exiting.")
                break

            print("Re-running with feedback")

            input_items.append({"content": f"Clarifications: {result.clarifications}", "role": "user"})

    print(f"Final requirements list: {latest_requirements}")



if __name__ == "__main__":
    asyncio.run(main())