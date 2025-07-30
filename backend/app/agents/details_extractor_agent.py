# app/agents/details_extractor_agent.py
from crewai import Agent
from app.tools.search_tool import search_tool
from app.tools.playwright_scraper import batch_extract_ad_details

class AdDetailsExtractorAgent:
    def details_extractor(self) -> Agent:
        """
        Creates an agent that extracts structured data from vehicle advertisements.
        """
        return Agent(
            role="Ad Data Extractor",
            goal=(
                "Extract key information from vehicle advertisement URLs including "
                "price, location, mileage, year, and other relevant details."
            ),
            backstory=(
                "You are a data extraction specialist with expertise in parsing "
                "vehicle advertisements. You can visit web pages and extract "
                "structured information from various Sri Lankan vehicle websites."
            ),
            tools=[search_tool],
            allow_delegation=False,
            verbose=True
        )

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