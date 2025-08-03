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
    
    def _store_ads_in_database_safe(self, ads_data, analysis_session_id=None) -> list:
        """
        Store ads in the database with enhanced transaction management and deduplication.
        Returns list of successfully stored ads.
        """
        if not ads_data:
            return []
            
        from app.core.db import SessionLocal
        from app.crud.ad_crud import create_ad, get_existing_ad_by_link
        from sqlalchemy.exc import IntegrityError, SQLAlchemyError
        from uuid import uuid4
        
        stored_ads = []
        failed_ads = []
        duplicate_ads = []
        
        # Generate session ID if not provided
        if not analysis_session_id:
            analysis_session_id = str(uuid4())
        
        db = SessionLocal()
        try:
            for ad in ads_data:
                # Check for either "URL" (old format) or "url" (new scraper format)
                ad_url = ad.get("URL") or ad.get("url") if isinstance(ad, dict) else None
                if not isinstance(ad, dict) or not ad_url:
                    self.logger.warning("Skipping invalid ad data", ad_data=str(ad)[:100])
                    continue
                    
                ad_data = {
                    "title": ad.get("ad_title", "Not Found"),
                    "price": ad.get("price_lkr", "Not Found"),
                    "location": ad.get("location", "Not Found"),
                    "mileage": ad.get("mileage_km", "Not Found"),
                    "year": str(ad.get("year", "Not Found")),
                    "link": ad_url
                }
                
                # Determine vehicle name based on ad data or context
                vehicle_name = None
                if ad.get("vehicle_name"):
                    vehicle_name = ad.get("vehicle_name")
                else:
                    # Try to determine from ad title (check both possible field names)
                    title_lower = (ad.get("Ad Title") or ad.get("ad_title", "")).lower()
                    if "aqua" in title_lower or self.vehicle1.lower() in title_lower:
                        vehicle_name = self.vehicle1
                    elif "fit" in title_lower or self.vehicle2.lower() in title_lower:
                        vehicle_name = self.vehicle2
                    else:
                        # Default to vehicle1 if we can't determine
                        vehicle_name = self.vehicle1
                
                try:
                    # Check if ad already exists before attempting to create
                    existing_ad = get_existing_ad_by_link(db, ad_data["link"])
                    if existing_ad:
                        duplicate_ads.append(ad_data["link"])
                        self.logger.debug("Duplicate ad skipped", link=ad_data["link"])
                        continue
                    
                    # Create new ad WITH session tracking data
                    created_ad = create_ad(db, ad_data, 
                                         analysis_session_id=analysis_session_id, 
                                         vehicle_name=vehicle_name)
                    stored_ads.append(created_ad)
                    self.logger.info("Ad stored successfully with session data", 
                                   title=ad_data["title"], 
                                   link=ad_data["link"],
                                   session_id=analysis_session_id,
                                   vehicle_name=vehicle_name)
                    
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
    
    def _extract_task_outputs(self, result):
        """
        Extract outputs from different crew result formats.
        """
        outputs = {}
        
        try:
            # Handle CrewOutput object
            if hasattr(result, 'tasks_output') and result.tasks_output:
                task_outputs = result.tasks_output
                self.logger.info(f"Processing {len(task_outputs)} task outputs")
                
                for i, task_output in enumerate(task_outputs):
                    output_text = task_output.raw if hasattr(task_output, 'raw') else str(task_output)
                    
                    # Identify task type based on content and order
                    if i == 0 or "#" in output_text or "comparison" in output_text.lower():
                        outputs['comparison'] = output_text
                    elif self._is_ads_json_data(output_text):
                        # Determine which vehicle these ads belong to
                        vehicle_key = f"vehicle{len([k for k in outputs.keys() if 'vehicle' in k]) + 1}_ads"
                        outputs[vehicle_key] = output_text
                        
            # Handle legacy formats
            elif hasattr(result, 'raw'):
                outputs['comparison'] = result.raw if isinstance(result.raw, str) else str(result.raw)
            elif isinstance(result, dict):
                result_values = list(result.values())
                if len(result_values) > 0:
                    outputs['comparison'] = result_values[0]
                if len(result_values) > 2:
                    outputs['vehicle1_ads'] = result_values[2]
                if len(result_values) > 4:
                    outputs['vehicle2_ads'] = result_values[4]
            elif isinstance(result, str):
                outputs['comparison'] = result
                
        except Exception as e:
            self.logger.warning(f"Error extracting task outputs: {str(e)}")
            
        return outputs
    
    def _is_ads_json_data(self, text: str) -> bool:
        """
        Check if text contains JSON ad data.
        """
        if not isinstance(text, str):
            return False
        
        text_lower = text.lower()
        return (('[' in text and ']' in text) and 
                ('ad title' in text_lower or 'price' in text_lower or 'url' in text_lower))
    
    def _parse_and_validate_ads(self, ads_data) -> list:
        """
        Parse and validate ad data with enhanced error handling.
        """
        if not ads_data:
            return []
        
        try:
            # Handle different input formats
            if isinstance(ads_data, list):
                parsed_ads = ads_data
            elif isinstance(ads_data, str):
                parsed_ads = self._safe_json_loads(ads_data, [])
            else:
                self.logger.warning(f"Unexpected ads data type: {type(ads_data)}")
                return []
            
            # Validate each ad entry
            validated_ads = []
            for ad in parsed_ads:
                if isinstance(ad, dict) and self._validate_ad_data(ad):
                    # Normalize ad data
                    normalized_ad = self._normalize_ad_data(ad)
                    validated_ads.append(normalized_ad)
                else:
                    self.logger.warning(f"Invalid ad data structure: {ad}")
            
            self.logger.info(f"Validated {len(validated_ads)} out of {len(parsed_ads)} ads")
            return validated_ads
            
        except Exception as e:
            self.logger.error(f"Failed to parse ads data: {str(e)}")
            return []
    
    def _safe_json_loads(self, data, default_val):
        """
        Enhanced JSON parsing with multiple fallback strategies.
        """
        if not data:
            return default_val
            
        try:
            if isinstance(data, str):
                # Clean up the JSON string with multiple strategies
                cleaned_data = data.strip()
                
                # Remove markdown code blocks
                if cleaned_data.startswith('```json'):
                    cleaned_data = cleaned_data[7:]
                elif cleaned_data.startswith('```'):
                    cleaned_data = cleaned_data[3:]
                    
                if cleaned_data.endswith('```'):
                    cleaned_data = cleaned_data[:-3]
                
                cleaned_data = cleaned_data.strip()
                
                # Try to extract JSON from mixed content
                if not cleaned_data.startswith('[') and '[' in cleaned_data:
                    start_idx = cleaned_data.find('[')
                    end_idx = cleaned_data.rfind(']') + 1
                    if start_idx >= 0 and end_idx > start_idx:
                        cleaned_data = cleaned_data[start_idx:end_idx]
                
                return json.loads(cleaned_data)
            elif isinstance(data, list):
                return data
            return default_val
            
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            self.logger.warning(f"JSON parsing failed: {str(e)}", data_preview=str(data)[:200])
            
            # Try alternative parsing strategies
            try:
                # Attempt to fix common JSON issues
                if isinstance(data, str):
                    # Fix common issues like trailing commas, single quotes, etc.
                    fixed_data = data.replace("'", '"').replace(',]', ']').replace(',}', '}')
                    return json.loads(fixed_data)
            except:
                pass
                
            return default_val
    
    def _validate_ad_data(self, ad: dict) -> bool:
        """
        Validate that ad data contains required fields.
        """
        required_fields = ['ad_title', 'url']
        return all(field in ad for field in required_fields)
    
    def _normalize_ad_data(self, ad: dict) -> dict:
        """
        Normalize ad data with consistent field formatting.
        """
        normalized = {
            'ad_title': str(ad.get('ad_title', 'Not Found')).strip(),
            'price_lkr': self._normalize_price(ad.get('price_lkr', 'Not Found')),
            'location': str(ad.get('location', 'Not Found')).strip(),
            'mileage_km': self._normalize_mileage(ad.get('mileage_km', 'Not Found')),
            'year': self._normalize_year(ad.get('year', 'Not Found')),
            'url': str(ad.get('url', '')).strip()
        }
        
        return normalized
    
    def _normalize_price(self, price) -> str:
        """
        Normalize price formatting.
        """
        if not price or price == 'Not Found':
            return 'Not Found'
        
        price_str = str(price).replace('Rs.', '').replace('LKR', '').replace(',', '').strip()
        
        try:
            # Try to parse as number and reformat
            price_num = float(price_str)
            return f"{price_num:,.0f}"
        except (ValueError, TypeError):
            return str(price)
    
    def _normalize_mileage(self, mileage) -> str:
        """
        Normalize mileage formatting.
        """
        if not mileage or mileage == 'Not Found':
            return 'Not Found'
        
        mileage_str = str(mileage).replace('km', '').replace(',', '').strip()
        
        try:
            # Try to parse as number
            mileage_num = float(mileage_str)
            return f"{mileage_num:,.0f} km"
        except (ValueError, TypeError):
            return str(mileage)
    
    def _normalize_year(self, year) -> str:
        """
        Normalize year formatting.
        """
        if not year or year == 'Not Found':
            return 'Not Found'
        
        try:
            year_num = int(float(str(year)))
            if 1900 <= year_num <= 2030:
                return str(year_num)
            else:
                return 'Not Found'
        except (ValueError, TypeError):
            return 'Not Found'
    
    def _convert_to_ad_details_format(self, ads_data):
        """
        Convert the agent output format to AdDetails format
        Support both old format ("Ad Title") and new scraper format ("ad_title")
        """
        converted_ads = []
        for ad in ads_data:
            if isinstance(ad, dict):
                # Handle both old and new field formats
                converted_ad = {
                    "title": (ad.get("Ad Title") or ad.get("ad_title", "Not Found")),
                    "price": (ad.get("Price (in LKR)") or ad.get("price_lkr", "Not Found")),
                    "location": (ad.get("Location") or ad.get("location", "Not Found")),
                    "mileage": (ad.get("Mileage (in km)") or ad.get("mileage_km", "Not Found")),
                    "year": str(ad.get("Year of Manufacture") or ad.get("year", "Not Found")),
                    "link": (ad.get("URL") or ad.get("url", "Not Found"))
                }
                converted_ads.append(converted_ad)
        return converted_ads
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
            
            # Generate unique analysis session ID FIRST
            from uuid import uuid4
            analysis_session_id = str(uuid4())
            
            # Extract ad data with intelligent parsing
            vehicle1_ads = self._parse_and_validate_ads(parsed_results.get('vehicle1_ads', []))
            vehicle2_ads = self._parse_and_validate_ads(parsed_results.get('vehicle2_ads', []))
            
            # Store ads in database with session ID for tracking
            stored_ads = self._store_ads_in_database_safe(vehicle1_ads + vehicle2_ads, analysis_session_id)
            self.logger.info(f"Successfully stored {len(stored_ads)} ads in database with session tracking")
            
            # Convert to expected API format
            vehicle1_ads_formatted = self._convert_to_ad_details_format(vehicle1_ads)
            vehicle2_ads_formatted = self._convert_to_ad_details_format(vehicle2_ads)
            
            # Add session ID and vehicle name to each ad
            self._add_session_data_to_ads(vehicle1_ads_formatted, analysis_session_id, self.vehicle1)
            self._add_session_data_to_ads(vehicle2_ads_formatted, analysis_session_id, self.vehicle2)

            return {
                "analysis_session_id": analysis_session_id,
                "comparison_report": comparison_report,  # Use pre-stored comparison
                "vehicle1_ads": vehicle1_ads_formatted,
                "vehicle2_ads": vehicle2_ads_formatted,
                "vehicle1_name": self.vehicle1,
                "vehicle2_name": self.vehicle2,
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
            # Generate a unique analysis session ID even for errors
            from uuid import uuid4
            analysis_session_id = str(uuid4())
            
            return {
                "analysis_session_id": analysis_session_id,
                "comparison_report": comparison_report,  # Still return the stored comparison
                "vehicle1_ads": [],
                "vehicle2_ads": [],
                "vehicle1_name": self.vehicle1,
                "vehicle2_name": self.vehicle2,
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
    
    def _add_session_data_to_ads(self, ads_list, analysis_session_id, vehicle_name):
        """Add session ID and vehicle name to each ad in the list"""
        for ad in ads_list:
            if isinstance(ad, dict):
                ad['analysis_session_id'] = analysis_session_id
                ad['vehicle_name'] = vehicle_name
