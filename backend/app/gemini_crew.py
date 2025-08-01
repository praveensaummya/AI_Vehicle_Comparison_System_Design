# app/gemini_crew.py
from crewai import Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from app.agents.comparison_agent import VehicleComparisonAgent
from app.agents.ad_finder_agent import SriLankanAdFinderAgent
from app.agents.details_extractor_agent import AdDetailsExtractorAgent
from app.tasks import VehicleAnalysisTasks
from app.core.config import settings
import os
import json
import structlog

class GeminiVehicleAnalysisCrew:
    """
    Vehicle Analysis Crew powered by Google Gemini API
    Uses the free Gemini 1.5 Flash model with generous quotas
    """
    
    def __init__(self, vehicle1: str, vehicle2: str):
        self.logger = structlog.get_logger()
        self.vehicle1 = vehicle1
        self.vehicle2 = vehicle2
        
        # Validate Gemini API key with detailed error information
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set. Please add GEMINI_API_KEY to your .env file. Get your key from: https://makersuite.google.com/app/apikey")
        
        if settings.GEMINI_API_KEY == "your_gemini_api_key_here":
            raise ValueError("GEMINI_API_KEY is set to placeholder value. Please replace with your actual Gemini API key from: https://makersuite.google.com/app/apikey")
        
        if len(settings.GEMINI_API_KEY) < 20:  # Basic sanity check
            raise ValueError("GEMINI_API_KEY appears to be invalid (too short). Please check your API key from: https://makersuite.google.com/app/apikey")
        
        # Set environment variables for CrewAI to use Google AI Studio directly (not Vertex AI)
        os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY
        
        # Clear OpenAI environment variables to prevent conflicts
        os.environ.pop("OPENAI_API_KEY", None)
        os.environ.pop("OPENAI_MODEL_NAME", None)
        os.environ.pop("OPENAI_API_BASE", None)
        
        # Explicitly prevent Vertex AI usage by clearing ALL Google Cloud credentials
        os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
        os.environ.pop("GOOGLE_CLOUD_PROJECT", None)
        os.environ.pop("GCLOUD_PROJECT", None)
        os.environ.pop("GOOGLE_CLOUD_QUOTA_PROJECT", None)
        
        # Force empty string to prevent any file-based auth
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""
        
        # Set LiteLLM to use Google AI Studio API explicitly
        os.environ["LITELLM_LOG"] = "INFO"  
        
        # Force CrewAI to use the Google AI Studio provider format
        # Use the correct LiteLLM format for Google AI Studio (not Vertex AI)
        # Format: gemini/model-name for Google AI Studio
        model_name = f"gemini/{settings.GEMINI_MODEL}"
        os.environ["OPENAI_MODEL_NAME"] = model_name
        
        # Also try setting it as the default model
        os.environ["LITELLM_MODEL"] = model_name
        
        # Additional environment variables to force Google AI Studio
        os.environ["GEMINI_API_KEY"] = settings.GEMINI_API_KEY  # Explicit Gemini key
        os.environ["GOOGLE_AI_STUDIO_API_KEY"] = settings.GEMINI_API_KEY  # Alternative name
        
        # Use environment variables approach - explicit LLM still routes through LiteLLM with issues
        # The direct LangChain integration works fine, but CrewAI needs specific model naming
        self.llm = None  # Let CrewAI handle LLM via environment variables for now
        
        # Test direct connection to ensure API key works
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            test_llm = ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                google_api_key=settings.GEMINI_API_KEY,
            )
            # Quick test to verify connectivity
            test_result = test_llm.invoke("Test")
            self.logger.info("Google AI Studio connection verified", 
                           model=settings.GEMINI_MODEL,
                           response_length=len(test_result.content) if hasattr(test_result, 'content') else 0)
        except Exception as e:
            self.logger.error("Google AI Studio connection test failed", 
                            error=str(e), model=settings.GEMINI_MODEL)
            raise ValueError(f"Cannot connect to Google AI Studio: {str(e)}")
        
        self.logger.info("Environment configured for Google AI Studio", model=settings.GEMINI_MODEL)
        
        # Log configuration (mask API key)
        api_key_masked = f"{settings.GEMINI_API_KEY[:8]}...{settings.GEMINI_API_KEY[-4:]}" if len(settings.GEMINI_API_KEY) > 12 else "[CONFIGURED]"
        
        self.logger.info("GeminiVehicleAnalysisCrew initialized", 
                        vehicle1=vehicle1, 
                        vehicle2=vehicle2,
                        gemini_key_status=api_key_masked,
                        model=settings.GEMINI_MODEL,
                        provider="google-gemini")

    def run(self):
        """Optimized Gemini crew execution"""
        try:
            self.logger.info("Starting Gemini-powered crew execution", 
                           vehicles=[self.vehicle1, self.vehicle2],
                           model=settings.GEMINI_MODEL)
            
            # 1. Create Gemini-optimized agents
            self.logger.info("Creating Gemini-optimized AI agents")
            agents = self._create_gemini_agents()
            self.logger.info("Gemini agents created successfully", agent_count=len(agents))

            # 2. Create tasks optimized for Gemini
            self.logger.info("Creating Gemini-optimized tasks")
            tasks = self._create_gemini_tasks(agents)
            self.logger.info("Gemini tasks created successfully", task_count=len(tasks))

            # 3. Assemble Gemini crew
            self.logger.info("Assembling Gemini crew")
            crew = self._create_gemini_crew(agents, tasks)
            self.logger.info("Gemini crew assembled successfully")

            # 4. Execute with Gemini
            self.logger.info("Executing Gemini crew workflow")
            result = crew.kickoff()
            self.logger.info("Gemini crew execution completed")

            # 5. Process results
            self.logger.info("Processing Gemini crew results")
            final_output = self._parse_crew_result(result)
            
            self.logger.info("Gemini analysis completed successfully", 
                           comparison_generated=bool(final_output.get('comparison_report')),
                           vehicle1_ads_found=len(final_output.get('vehicle1_ads', [])),
                           vehicle2_ads_found=len(final_output.get('vehicle2_ads', [])),
                           llm_provider="google-gemini")
            
            return final_output
            
        except Exception as e:
            self.logger.error("Gemini crew execution failed", 
                            error=str(e),
                            error_type=type(e).__name__,
                            vehicles=[self.vehicle1, self.vehicle2],
                            model=settings.GEMINI_MODEL)
            raise
    
    def _create_gemini_agents(self):
        """Create agents optimized for Gemini with explicit LLM"""
        # Pass explicit LLM if available, otherwise let CrewAI handle it
        if self.llm:
            self.logger.info("Using explicit Gemini LLM for agents")
            comparison_agent = VehicleComparisonAgent().expert_reviewer(llm=self.llm)
            ad_finder_agent = SriLankanAdFinderAgent().ad_finder(llm=self.llm)
            details_extractor_agent = AdDetailsExtractorAgent().details_extractor(llm=self.llm)
        else:
            self.logger.info("Using environment-based LLM for agents")
            comparison_agent = VehicleComparisonAgent().expert_reviewer()
            ad_finder_agent = SriLankanAdFinderAgent().ad_finder()
            details_extractor_agent = AdDetailsExtractorAgent().details_extractor()
        
        return {
            'comparison': comparison_agent,
            'ad_finder': ad_finder_agent,  
            'details_extractor': details_extractor_agent
        }
    
    def _create_gemini_tasks(self, agents):
        """Create tasks optimized for Gemini's capabilities"""
        tasks_manager = VehicleAnalysisTasks()
        tasks = []
        
        # 1. Vehicle comparison (Gemini excels at detailed analysis)
        comparison_task = tasks_manager.vehicle_comparison_task(
            agents['comparison'], self.vehicle1, self.vehicle2
        )
        tasks.append(comparison_task)
        self.logger.info("Gemini comparison task created")
        
        # 2. Ad finding tasks
        find_ads_v1 = tasks_manager.find_ads_task(agents['ad_finder'], self.vehicle1)
        find_ads_v2 = tasks_manager.find_ads_task(agents['ad_finder'], self.vehicle2)
        tasks.extend([find_ads_v1, find_ads_v2])
        self.logger.info("Gemini ad finding tasks created")
        
        # 3. Details extraction tasks
        extract_v1 = tasks_manager.extract_details_task(
            agents['details_extractor'], self.vehicle1, find_ads_v1
        )
        extract_v2 = tasks_manager.extract_details_task(
            agents['details_extractor'], self.vehicle2, find_ads_v2
        )
        tasks.extend([extract_v1, extract_v2])
        self.logger.info("Gemini extraction tasks created")
        
        return tasks
    
    def _create_gemini_crew(self, agents, tasks):
        """Create crew optimized for Gemini performance"""
        agent_list = list(agents.values())
        
        crew = Crew(
            agents=agent_list,
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,  # Disable for better performance
            cache=True     # Enable cache for Gemini (it's faster)
        )
        
        self.logger.info("Gemini crew configured", 
                        agent_count=len(agent_list),
                        task_count=len(tasks),
                        model=settings.GEMINI_MODEL,
                        cache_enabled=True)
        
        return crew

    def _parse_crew_result(self, result):
        """Parse crew results into structured format"""
        # Handle different result formats from Gemini
        if hasattr(result, 'raw'):
            outputs = [result.raw] if isinstance(result.raw, str) else list(result.raw) if result.raw else []
        elif isinstance(result, dict):
            outputs = list(result.values())
        elif isinstance(result, str):
            outputs = [result]
        else:
            outputs = []
        
        comparison_report = outputs[0] if len(outputs) > 0 else "Comparison report not generated."
        
        def safe_json_loads(data, default_val):
            if not data:
                return default_val
            try:
                if isinstance(data, str):
                    return json.loads(data)
                return data if isinstance(data, list) else default_val
            except (json.JSONDecodeError, TypeError):
                return default_val

        vehicle1_ads = safe_json_loads(outputs[2] if len(outputs) > 2 else '[]', [])
        vehicle2_ads = safe_json_loads(outputs[4] if len(outputs) > 4 else '[]', [])

        return {
            "comparison_report": comparison_report,
            "vehicle1_ads": vehicle1_ads,
            "vehicle2_ads": vehicle2_ads
        }
