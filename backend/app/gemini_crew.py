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

    def _clean_and_store_comparison_report(self, raw_report):
        """
        Clean and store the comparison report in the database.
        """
        clean_report = self._clean_comparison_report(raw_report)
        self._store_comparison_in_database(
            self.vehicle1,
            self.vehicle2,
            clean_report,
            {}
        )

    def _clean_comparison_report(self, report):
        """
        Clean and normalize the comparison report before storing in database.
        """
        if not report or not isinstance(report, str):
            return "No comparison report available."
        
        # Remove extra whitespace and normalize line breaks
        clean_report = report.strip()
        
        # Remove markdown code blocks if present
        if clean_report.startswith('```'):
            lines = clean_report.split('\n')
            clean_report = '\n'.join(lines[1:-1]) if len(lines) > 2 else clean_report
        
        # Normalize excessive whitespace
        import re
        clean_report = re.sub(r'\n\s*\n', '\n\n', clean_report)  # Normalize paragraph breaks
        clean_report = re.sub(r' +', ' ', clean_report)  # Remove extra spaces
        
        # Ensure proper vehicle name formatting
        clean_report = clean_report.replace(self.vehicle1.lower(), self.vehicle1)
        clean_report = clean_report.replace(self.vehicle2.lower(), self.vehicle2)
        
        # Remove any emojis or special characters that might cause DB issues
        clean_report = re.sub(r'[^\w\s\n.,;:!?()\[\]{}"\'-]', '', clean_report)
        
        self.logger.info("Comparison report cleaned", 
                        original_length=len(report), 
                        cleaned_length=len(clean_report))
        
        return clean_report.strip()

    def run(self):
        try:
            self.logger.info("Starting Gemini-powered crew execution", 
                           vehicles=[self.vehicle1, self.vehicle2],
                           model=settings.GEMINI_MODEL)
            
            # 1. Create Gemini-optimized agents
            self.logger.info("Creating Gemini-optimized AI agents")
            agents = self._create_gemini_agents()
            self.logger.info("Gemini agents created successfully", agent_count=len(agents))

            # 2. Execute comparison task first and store immediately
            self.logger.info("Executing comparison task first")
            comparison_report = self._execute_comparison_task_and_store(agents)
            
            # 3. Create remaining tasks (ad finding and extraction)
            self.logger.info("Creating ad finding and extraction tasks")
            tasks = self._create_ad_tasks(agents)
            self.logger.info("Ad tasks created successfully", task_count=len(tasks))

            # 4. Assemble crew for ad processing
            self.logger.info("Assembling crew for ad processing")
            crew = self._create_gemini_crew(agents, tasks)
            self.logger.info("Ad processing crew assembled successfully")

            # 5. Execute ad finding and extraction
            self.logger.info("Executing ad finding and extraction workflow")
            result = crew.kickoff() if tasks else None
            self.logger.info("Ad processing crew execution completed")

            # 6. Process ad results and combine with stored comparison
            self.logger.info("Processing ad results")
            final_output = self._parse_crew_result_with_comparison(result, comparison_report)
            
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
    
    def _store_ads_in_database_safe(self, ads_data) -> list:
        """
        Store ads in the database with enhanced transaction management and deduplication.
        Returns list of successfully stored ads.
        """
        if not ads_data:
            return []
            
        from app.core.db import SessionLocal
        from app.crud.ad_crud import create_ad, get_existing_ad_by_link
        from sqlalchemy.exc import IntegrityError, SQLAlchemyError
        
        stored_ads = []
        failed_ads = []
        duplicate_ads = []
        
        db = SessionLocal()
        try:
            for ad in ads_data:
                if not isinstance(ad, dict) or not ad.get("URL"):
                    self.logger.warning("Skipping invalid ad data", ad_data=str(ad)[:100])
                    continue
                    
                ad_data = {
                    "title": ad.get("Ad Title", "Not Found"),
                    "price": ad.get("Price (in LKR)", "Not Found"),
                    "location": ad.get("Location", "Not Found"),
                    "mileage": ad.get("Mileage (in km)", "Not Found"),
                    "year": str(ad.get("Year of Manufacture", "Not Found")),
                    "link": ad.get("URL", "")
                }
                
                try:
                    # Check if ad already exists before attempting to create
                    existing_ad = get_existing_ad_by_link(db, ad_data["link"])
                    if existing_ad:
                        duplicate_ads.append(ad_data["link"])
                        self.logger.debug("Duplicate ad skipped", link=ad_data["link"])
                        continue
                    
                    # Create new ad
                    created_ad = create_ad(db, ad_data)
                    stored_ads.append(created_ad)
                    self.logger.info("Ad stored successfully", 
                                   title=ad_data["title"], 
                                   link=ad_data["link"])
                    
                except IntegrityError as e:
                    db.rollback()
                    duplicate_ads.append(ad_data["link"])
                    self.logger.debug("Duplicate ad detected during insert", 
                                    link=ad_data["link"], 
                                    error=str(e))
                    
                except SQLAlchemyError as e:
                    db.rollback()
                    failed_ads.append(ad_data["link"])
                    self.logger.error("Database error storing ad", 
                                    link=ad_data["link"], 
                                    error=str(e))
                    
                except Exception as e:
                    db.rollback()
                    failed_ads.append(ad_data["link"])
                    self.logger.error("Unexpected error storing ad", 
                                    link=ad_data["link"], 
                                    error=str(e))
            
            # Final commit for all successful operations
            db.commit()
            
            # Log summary
            self.logger.info("Database storage completed", 
                           stored_count=len(stored_ads),
                           duplicate_count=len(duplicate_ads),
                           failed_count=len(failed_ads),
                           total_processed=len(ads_data))
            
        except Exception as e:
            db.rollback()
            self.logger.error("Critical database error during ad storage", error=str(e))
            
        finally:
            db.close()
            
        return stored_ads
    
    def _store_ads_in_database(self, ads_data):
        """
        Legacy method - kept for backward compatibility.
        """
        return self._store_ads_in_database_safe(ads_data)
    def _store_comparison_in_database(self, vehicle1, vehicle2, comparison_report, metadata):
        """
        Store the comparison report in the database.
        """
        from app.core.db import SessionLocal
        from app.crud.comparison_crud import create_comparison
        db = SessionLocal()
        try:
            stored_comparison = create_comparison(db, vehicle1, vehicle2, comparison_report, metadata)
            self.logger.info("Comparison report stored successfully", 
                            vehicle1=vehicle1, 
                            vehicle2=vehicle2)
            return stored_comparison
        except Exception as e:
            self.logger.error("Failed to store comparison report", 
                            vehicle1=vehicle1, 
                            vehicle2=vehicle2, 
                            error=str(e))
        finally:
            db.close()

    def _execute_comparison_task_and_store(self, agents):
        """
        Execute only the comparison task and store the result immediately.
        """
        try:
            # Create comparison task
            tasks_manager = VehicleAnalysisTasks()
            comparison_task = tasks_manager.vehicle_comparison_task(
                agents['comparison'], self.vehicle1, self.vehicle2
            )
            
            # Create a minimal crew for comparison task only
            comparison_crew = Crew(
                agents=[agents['comparison']],
                tasks=[comparison_task],
                process=Process.sequential,
                verbose=True,
                memory=False,
                cache=True
            )
            
            # Execute comparison task
            self.logger.info("Executing comparison task")
            result = comparison_crew.kickoff()
            
            # Extract comparison report from result
            comparison_report = self._extract_comparison_from_result(result)
            
            # Clean and store the comparison report immediately
            self.logger.info("Cleaning and storing comparison report")
            cleaned_report = self._clean_comparison_report(comparison_report)
            
            # Store in database with metadata
            metadata = {
                "llm_provider": "google-gemini",
                "model": settings.GEMINI_MODEL,
                "task_type": "comparison_only"
            }
            
            self._store_comparison_in_database(
                self.vehicle1, self.vehicle2, cleaned_report, metadata
            )
            
            self.logger.info("Comparison report stored successfully")
            return cleaned_report
            
        except Exception as e:
            self.logger.error("Failed to execute and store comparison task", error=str(e))
            return "Error generating comparison report."
    
    def _extract_comparison_from_result(self, result):
        """
        Extract comparison report from crew result.
        """
        try:
            if hasattr(result, 'raw'):
                return result.raw if isinstance(result.raw, str) else str(result.raw)
            elif isinstance(result, str):
                return result
            elif hasattr(result, 'tasks_output') and result.tasks_output:
                task_output = result.tasks_output[0]
                return task_output.raw if hasattr(task_output, 'raw') else str(task_output)
            else:
                return str(result)
        except Exception as e:
            self.logger.warning("Failed to extract comparison from result", error=str(e))
            return "Comparison report extraction failed."
    
    def _create_ad_tasks(self, agents):
        """
        Create only ad finding and extraction tasks (excluding comparison).
        """
        tasks_manager = VehicleAnalysisTasks()
        tasks = []
        
        # Ad finding tasks
        find_ads_v1 = tasks_manager.find_ads_task(agents['ad_finder'], self.vehicle1)
        find_ads_v2 = tasks_manager.find_ads_task(agents['ad_finder'], self.vehicle2)
        tasks.extend([find_ads_v1, find_ads_v2])
        
        # Details extraction tasks
        extract_v1 = tasks_manager.extract_details_task(
            agents['details_extractor'], self.vehicle1, find_ads_v1
        )
        extract_v2 = tasks_manager.extract_details_task(
            agents['details_extractor'], self.vehicle2, find_ads_v2
        )
        tasks.extend([extract_v1, extract_v2])
        
        return tasks
    
    def _parse_crew_result_with_comparison(self, result, comparison_report):
        """
        Parse crew result and combine with pre-stored comparison report.
        """
        try:
            # Parse ad results (skip comparison parsing since it's already stored)
            parsed_results = self._extract_task_outputs(result) if result else {}
            
            # Extract ad data with intelligent parsing
            vehicle1_ads = self._parse_and_validate_ads(parsed_results.get('vehicle1_ads', []))
            vehicle2_ads = self._parse_and_validate_ads(parsed_results.get('vehicle2_ads', []))
            
            # Store ads in database with improved transaction handling
            stored_ads = self._store_ads_in_database_safe(vehicle1_ads + vehicle2_ads)
            self.logger.info(f"Successfully stored {len(stored_ads)} ads in database")
            
            # Convert to expected API format
            vehicle1_ads_formatted = self._convert_to_ad_details_format(vehicle1_ads)
            vehicle2_ads_formatted = self._convert_to_ad_details_format(vehicle2_ads)

            return {
                "comparison_report": comparison_report,  # Use pre-stored comparison
                "vehicle1_ads": vehicle1_ads_formatted,
                "vehicle2_ads": vehicle2_ads_formatted,
                "metadata": {
                    "total_ads_found": len(vehicle1_ads) + len(vehicle2_ads),
                    "ads_stored": len(stored_ads),
                    "parsing_success": True,
                    "llm_provider": "google-gemini",
                    "comparison_stored_separately": True
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to parse ad results: {str(e)}", exc_info=True)
            return {
                "comparison_report": comparison_report,  # Still return the stored comparison
                "vehicle1_ads": [],
                "vehicle2_ads": [],
                "metadata": {
                    "total_ads_found": 0,
                    "ads_stored": 0,
                    "parsing_success": False,
                    "error": str(e),
                    "llm_provider": "google-gemini"
                }
            }

    def _parse_crew_result(self, result) -> dict:
        """
        Parses the crew output and stores ads in database with improved error handling.
        """
        try:
            # Enhanced result parsing with better format detection
            parsed_results = self._extract_task_outputs(result)
            
            # Extract comparison report
            comparison_report = parsed_results.get('comparison', "Comparison report not generated.")
            
            # Extract ad data with intelligent parsing
            vehicle1_ads = self._parse_and_validate_ads(parsed_results.get('vehicle1_ads', []))
            vehicle2_ads = self._parse_and_validate_ads(parsed_results.get('vehicle2_ads', []))
            
            # Store ads in database with improved transaction handling
            stored_ads = self._store_ads_in_database_safe(vehicle1_ads + vehicle2_ads)
            self.logger.info(f"Successfully stored {len(stored_ads)} ads in database")
            
            # Store comparison report in database
            stored_comparison = self._store_comparison_in_database(
                self.vehicle1, self.vehicle2, comparison_report, {
                    "total_ads_found": len(vehicle1_ads) + len(vehicle2_ads),
                    "ads_stored": len(stored_ads),
                    "llm_provider": "google-gemini",
                    "model": settings.GEMINI_MODEL
                }
            )
            
            # Convert to expected API format
            vehicle1_ads_formatted = self._convert_to_ad_details_format(vehicle1_ads)
            vehicle2_ads_formatted = self._convert_to_ad_details_format(vehicle2_ads)

            return {
                "comparison_report": comparison_report,
                "vehicle1_ads": vehicle1_ads_formatted,
                "vehicle2_ads": vehicle2_ads_formatted,
                "metadata": {
                    "total_ads_found": len(vehicle1_ads) + len(vehicle2_ads),
                    "ads_stored": len(stored_ads),
                    "parsing_success": True,
                    "llm_provider": "google-gemini"
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to parse crew result: {str(e)}", exc_info=True)
            return {
                "comparison_report": "Error generating comparison report.",
                "vehicle1_ads": [],
                "vehicle2_ads": [],
                "metadata": {
                    "total_ads_found": 0,
                    "ads_stored": 0,
                    "parsing_success": False,
                    "error": str(e),
                    "llm_provider": "google-gemini"
                }
            }
