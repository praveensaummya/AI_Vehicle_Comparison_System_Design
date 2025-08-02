# app/agents/details_extractor_agent.py
from crewai import Agent
from app.tools.search_tool import search_tool
from app.tools.ad_details_tool import ad_details_extractor_tool
from app.tools.playwright_scraper import batch_extract_ad_details

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
                "You are a data extraction specialist with expertise in parsing "
                "vehicle advertisements. You can visit web pages and extract "
                "structured information from various Sri Lankan vehicle websites. "
                "You have extensive experience interpreting vehicle mileage data, "
                "understanding that when sellers mention 'just 50km' or 'only 25' "
                "they typically mean '50,000 km' or '25,000 km' respectively. "
                "You apply contextual intelligence to convert abbreviated mileage "
                "figures into their proper full values."
            ),
            "tools": [ad_details_extractor_tool],
            "allow_delegation": False,
            "verbose": True
        }
        
        # Add LLM if provided
        if llm is not None:
            agent_config["llm"] = llm
        
        return Agent(**agent_config)

    def extract_details_from_urls(self, urls: list) -> list:
        """
        Batch extract ad details from a list of URLs using Playwright,
        and save each ad to the database.
        """
        from app.core.db import SessionLocal
        from app.crud.ad_crud import create_ad
        from sqlalchemy.exc import IntegrityError

        ads = batch_extract_ad_details(urls)
        db = SessionLocal()
        for ad in ads:
            try:
                create_ad(db, ad)
            except IntegrityError:
                db.rollback()  # Duplicate link, skip
            except Exception:
                db.rollback()
        db.close()
        return ads