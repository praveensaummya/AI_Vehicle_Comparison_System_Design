# app/agents/details_extractor_agent.py
from crewai import Agent
from app.tools.sync_ad_details_tool import SyncAdDetailsExtractorTool

class AdDetailsExtractorAgent:
    def details_extractor(self, llm=None) -> Agent:
        """
        Creates an agent that extracts structured data from vehicle advertisements.
        """
        agent_config = {
            "role": "Ad Data Extractor",
            "goal": (
                "Extract key information from vehicle advertisement URLs including "
                "price, location, mileage, year, and other relevant details."
            ),
            "backstory": (
                "You are an expert data extraction specialist who extracts real vehicle "
                "advertisement data from Sri Lankan websites like ikman.lk and riyasewana.com. "
                "You use efficient HTTP requests with requests library and BeautifulSoup for HTML parsing "
                "to extract accurate pricing, locations, mileage figures, and vehicle specifications. "
                "You are skilled at handling various website structures, parsing HTML content, "
                "and cleaning extracted data for consistent formatting and reliable results."
            ),
            "tools": [SyncAdDetailsExtractorTool()],
            "allow_delegation": False,
            "verbose": True
        }
        
        # Add LLM if provided
        if llm is not None:
            agent_config["llm"] = llm
        
        return Agent(**agent_config)

