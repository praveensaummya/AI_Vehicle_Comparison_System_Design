# app/crew.py
from crewai import Crew, Process
from app.agents.comparison_agent import VehicleComparisonAgent
from app.agents.ad_finder_agent import SriLankanAdFinderAgent
from app.agents.details_extractor_agent import AdDetailsExtractorAgent
from app.tasks import VehicleAnalysisTasks
from app.core.config import settings
from langchain_openai import ChatOpenAI
import json

class VehicleAnalysisCrew:
    def __init__(self, vehicle1: str, vehicle2: str):
        self.vehicle1 = vehicle1
        self.vehicle2 = vehicle2
        self.llm = ChatOpenAI(
            model_name="gpt-4o",
            api_key=settings.OPENAI_API_KEY
        )

    def run(self):
        # 1. Instantiate Agents
        comparison_agent = VehicleComparisonAgent().expert_reviewer()
        ad_finder_agent = SriLankanAdFinderAgent().ad_finder()
        details_extractor_agent = AdDetailsExtractorAgent().details_extractor()

        # 2. Instantiate Tasks
        tasks = VehicleAnalysisTasks()

        # Task for comparing the two vehicles
        comparison_task = tasks.vehicle_comparison_task(comparison_agent, self.vehicle1, self.vehicle2)

        # Tasks for finding and extracting ads for Vehicle 1
        find_ads_task_v1 = tasks.find_ads_task(ad_finder_agent, self.vehicle1)
        extract_details_task_v1 = tasks.extract_details_task(details_extractor_agent, self.vehicle1, find_ads_task_v1)

        # Tasks for finding and extracting ads for Vehicle 2
        find_ads_task_v2 = tasks.find_ads_task(ad_finder_agent, self.vehicle2)
        extract_details_task_v2 = tasks.extract_details_task(details_extractor_agent, self.vehicle2, find_ads_task_v2)

        # 3. Assemble the Crew
        # This crew will execute tasks sequentially
        crew = Crew(
            agents=[comparison_agent, ad_finder_agent, details_extractor_agent],
            tasks=[
                comparison_task,
                find_ads_task_v1,
                extract_details_task_v1,
                find_ads_task_v2,
                extract_details_task_v2
            ],
            process=Process.sequential,
            verbose=2,
            manager_llm=self.llm
        )

        # 4. Kick off the work
        result = crew.kickoff()

        # 5. Process and Structure the Final Output
        # The raw output is a dictionary where keys are task outputs. We need to parse them.
        final_output = self._parse_crew_result(result)
        return final_output

    def _parse_crew_result(self, result: dict) -> dict:
        """
        Parses the complex dictionary output from the crew into our simple target JSON structure.
        """
        # The raw outputs from the tasks are usually the last items in the result dictionary
        outputs = list(result.values())
        
        comparison_report = outputs[0] if len(outputs) > 0 else "Comparison report not generated."
        
        # The ad details are expected to be JSON strings, so we parse them safely
        def safe_json_loads(data, default_val):
            try:
                return json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return default_val

        vehicle1_ads = safe_json_loads(outputs[2] if len(outputs) > 2 else '[]', [])
        vehicle2_ads = safe_json_loads(outputs[4] if len(outputs) > 4 else '[]', [])

        return {
            "comparison_report": comparison_report,
            "vehicle1_ads": vehicle1_ads,
            "vehicle2_ads": vehicle2_ads
        }