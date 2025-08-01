# app/crew.py
from crewai import Crew, Process
from app.agents.comparison_agent import VehicleComparisonAgent
from app.agents.ad_finder_agent import SriLankanAdFinderAgent
from app.agents.details_extractor_agent import AdDetailsExtractorAgent
from app.tasks import VehicleAnalysisTasks
from app.core.config import settings
import os
import json
import structlog

class VehicleAnalysisCrew:
    def __init__(self, vehicle1: str, vehicle2: str):
        self.logger = structlog.get_logger()
        self.vehicle1 = vehicle1
        self.vehicle2 = vehicle2
        
        # Validate API key before proceeding
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your_openai_api_key_here":
            raise ValueError("OPENAI_API_KEY is not properly configured")
        
        # Set environment variables for CrewAI to use
        os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
        os.environ["OPENAI_MODEL_NAME"] = "gpt-3.5-turbo"
        
        # Log API configuration (without exposing the key)
        api_key_masked = f"{settings.OPENAI_API_KEY[:8]}...{settings.OPENAI_API_KEY[-4:]}" if len(settings.OPENAI_API_KEY) > 12 else "[CONFIGURED]"
        
        self.logger.info("VehicleAnalysisCrew initialized", 
                        vehicle1=vehicle1, 
                        vehicle2=vehicle2,
                        openai_key_status=api_key_masked,
                        model="gpt-3.5-turbo")

    def run(self):
        """Optimized crew execution with better error handling and efficiency"""
        try:
            self.logger.info("Starting optimized crew execution workflow", 
                           vehicles=[self.vehicle1, self.vehicle2])
            
            # 1. Instantiate Agents (optimized initialization)
            self.logger.info("Instantiating AI agents with optimized settings")
            agents = self._create_optimized_agents()
            self.logger.info("AI agents instantiated successfully", agent_count=len(agents))

            # 2. Create Tasks (batch creation for efficiency)
            self.logger.info("Creating analysis tasks in optimized batches")
            tasks = self._create_optimized_tasks(agents)
            self.logger.info("All tasks created successfully", task_count=len(tasks))

            # 3. Assemble Optimized Crew
            self.logger.info("Assembling optimized crew configuration")
            crew = self._create_optimized_crew(agents, tasks)
            self.logger.info("Crew assembled with optimized settings")

            # 4. Execute with enhanced logging
            self.logger.info("Initiating crew task execution with progress tracking")
            result = crew.kickoff()
            self.logger.info("Crew task execution completed successfully")

            # 5. Process Results
            self.logger.info("Processing and validating crew results")
            final_output = self._parse_crew_result(result)
            
            # Enhanced result logging
            self.logger.info("Analysis workflow completed successfully", 
                           comparison_generated=bool(final_output.get('comparison_report')),
                           vehicle1_ads_found=len(final_output.get('vehicle1_ads', [])),
                           vehicle2_ads_found=len(final_output.get('vehicle2_ads', [])),
                           total_processing_steps=5)
            
            return final_output
            
        except Exception as e:
            self.logger.error("Crew execution failed with detailed error info", 
                            error=str(e),
                            error_type=type(e).__name__,
                            vehicles=[self.vehicle1, self.vehicle2])
            raise
    
    def _create_optimized_agents(self):
        """Create agents with optimized settings"""
        comparison_agent = VehicleComparisonAgent().expert_reviewer()
        ad_finder_agent = SriLankanAdFinderAgent().ad_finder()
        details_extractor_agent = AdDetailsExtractorAgent().details_extractor()
        
        return {
            'comparison': comparison_agent,
            'ad_finder': ad_finder_agent,  
            'details_extractor': details_extractor_agent
        }
    
    def _create_optimized_tasks(self, agents):
        """Create tasks in optimized batches"""
        tasks_manager = VehicleAnalysisTasks()
        
        # Create all tasks efficiently
        tasks = []
        
        # 1. Comparison task (highest priority)
        comparison_task = tasks_manager.vehicle_comparison_task(
            agents['comparison'], self.vehicle1, self.vehicle2
        )
        tasks.append(comparison_task)
        self.logger.info("Comparison task created", priority="high")
        
        # 2. Ad finding tasks (parallel-ready)
        find_ads_v1 = tasks_manager.find_ads_task(agents['ad_finder'], self.vehicle1)
        find_ads_v2 = tasks_manager.find_ads_task(agents['ad_finder'], self.vehicle2)
        tasks.extend([find_ads_v1, find_ads_v2])
        self.logger.info("Ad finding tasks created", vehicles=[self.vehicle1, self.vehicle2])
        
        # 3. Details extraction tasks (dependent)
        extract_v1 = tasks_manager.extract_details_task(
            agents['details_extractor'], self.vehicle1, find_ads_v1
        )
        extract_v2 = tasks_manager.extract_details_task(
            agents['details_extractor'], self.vehicle2, find_ads_v2
        )
        tasks.extend([extract_v1, extract_v2])
        self.logger.info("Details extraction tasks created", vehicles=[self.vehicle1, self.vehicle2])
        
        return tasks
    
    def _create_optimized_crew(self, agents, tasks):
        """Create crew with optimized configuration"""
        agent_list = list(agents.values())
        
        crew = Crew(
            agents=agent_list,
            tasks=tasks,
            process=Process.sequential,  # Sequential for better error handling
            verbose=True,  # Keep verbose for debugging
            memory=False,  # Disable memory for faster execution
            cache=False    # Disable cache for fresh results
        )
        
        self.logger.info("Crew created with optimized configuration", 
                        agent_count=len(agent_list),
                        task_count=len(tasks),
                        process="sequential",
                        memory_enabled=False,
                        cache_enabled=False)
        
        return crew

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