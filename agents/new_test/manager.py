from __future__ import annotations

import asyncio
import time

from rich.console import Console

from agents import Runner, custom_span, gen_trace_id, trace

from team.requirements_analyzer_agent import requirements_analyzer_agent, TechnicalRequirements
from team.project_planner_agent import project_planner_agent, ProjectPlan
from printer import Printer

class GeneralManager:
    def __init__(self):
        self.console = Console()
        self.printer = Printer(self.console)

    async def run(self, tech_req_txt: str) -> None:
        trace_id = gen_trace_id()
        with trace("Project trace", trace_id=trace_id):
            self.printer.update_item(
                "trace_id",
                f"View trace: https://platform.openai.com/traces/{trace_id}",
                is_done=True,
                hide_checkmark=True,
            )

            self.printer.update_item(
                "starting",
                "Starting project...",
                is_done=True,
                hide_checkmark=True,
            )
            technical_requirements = await self._analyze_technical_requirements(tech_req_txt)
            # project_plan = await self._plan_project(technical_requirements)


            self.printer.end()

        # print("\n\n=====Technical Requirements=====\n\n")
        # func_r = "\n".join(technical_requirements.functional_requirements)
        # nonfunc_r = "\n".join(technical_requirements.non_functional_requirements)
        # constraints = "\n".join(technical_requirements.constraints)
        # ambig_r = "\n".join(technical_requirements.ambiguities)
        # missing_r = "\n".join(technical_requirements.missing_details)
        # print(f"func_r: {func_r}")
        # print(f"nonfunc_r: {nonfunc_r}")
        # print(f"constraints: {constraints}")
        # print(f"ambig_r: {ambig_r}")
        # print(f"missing_r: {missing_r}")
        

    async def _analyze_technical_requirements(self, tech_req_txt: str) -> TechnicalRequirements:
        self.printer.update_item("analyze_technical_requirements", "Starting ... ")
        result = await Runner.run(
            requirements_analyzer_agent,
            tech_req_txt,
        )
        print(result.to_input_list())

        self.printer.mark_item_done("analyze_technical_requirements")
        return result.final_output_as(TechnicalRequirements)

    async def _plan_project(self, technical_requirements: TechnicalRequirements) -> ProjectPlan:
        self.printer.update_item("plan_project", "Starting ... ")

        func_r = technical_requirements.functional_requirements
        nonfunc_r = technical_requirements.non_functional_requirements
        r_list = ["Functional requirements: "]
        for f_req in func_r:
            r_list.append(f"\n - {f_req}")
        r_list.append("\n\nNon-functional requirements: ")
        for nf_req in nonfunc_r:
            r_list.append(f"\n - {nf_req}")
        requirement_str = "".join(r_list)
        result = await Runner.run(
            project_planner_agent,
            requirement_str
        )
        self.printer.mark_item_done("plan_project")
        return result.final_output_as(ProjectPlan)



