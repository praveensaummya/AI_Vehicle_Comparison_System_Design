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
                    "ads_stored": len(stored_ads)
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
                    "parsing_success": True
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
                    "error": str(e)
                }
            }
    
    def _extract_task_outputs(self, result) -> dict:
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
        required_fields = ['Ad Title', 'URL']
        return all(field in ad for field in required_fields)
    
    def _normalize_ad_data(self, ad: dict) -> dict:
        """
        Normalize ad data with consistent field formatting.
        """
        normalized = {
            'Ad Title': str(ad.get('Ad Title', 'Not Found')).strip(),
            'Price (in LKR)': self._normalize_price(ad.get('Price (in LKR)', 'Not Found')),
            'Location': str(ad.get('Location', 'Not Found')).strip(),
            'Mileage (in km)': self._normalize_mileage(ad.get('Mileage (in km)', 'Not Found')),
            'Year of Manufacture': self._normalize_year(ad.get('Year of Manufacture', 'Not Found')),
            'URL': str(ad.get('URL', '')).strip()
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
        """
        converted_ads = []
        for ad in ads_data:
            if isinstance(ad, dict):
                converted_ad = {
                    "title": ad.get("Ad Title", "Not Found"),
                    "price": ad.get("Price (in LKR)", "Not Found"),
                    "location": ad.get("Location", "Not Found"),
                    "mileage": ad.get("Mileage (in km)", "Not Found"),
                    "year": str(ad.get("Year of Manufacture", "Not Found")),
                    "link": ad.get("URL", "Not Found")
                }
                converted_ads.append(converted_ad)
        return converted_ads
    
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

    def _store_comparison_in_database(self, vehicle1: str, vehicle2: str, comparison_report: str, metadata: dict):
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
