# app/agents/ad_finder_agent.py
from crewai import Agent
from app.tools.search_tool import search_tool
from app.tools.sri_lankan_scraper import sri_lankan_scraper_tool

class SriLankanAdFinderAgent:
    def ad_finder(self, llm=None) -> Agent:
        """
        Creates an agent that finds vehicle sale listings in the Sri Lankan market.
        """
        agent_config = {
            "role": "Local Vehicle Market Analyst",
            "goal": (
                "Find URLs of individual car SALE advertisements (not rentals, parts, or services) for specific vehicle models on "
                "popular Sri Lankan websites like ikman.lk and riyasewana.com. Each URL must link directly "
                "to a single car's FOR SALE advertisement page - avoid rental, spare parts, accessories, or service ads."
            ),
            "backstory": (
                "You are a savvy car dealer based in Colombo with an encyclopedic knowledge "
                "of the local online vehicle market. You specialize in finding ACTUAL VEHICLE SALES only - "
                "never rentals, spare parts, accessories, or services. You know exactly how to phrase search "
                "queries to find specific car FOR SALE advertisements on websites like ikman.lk and riyasewana.com.\n\n"
                "CRITICAL FILTERING RULES:\n"
                "✅ INCLUDE: 'for sale', 'sale', 'selling', vehicle model + year combinations\n"
                "❌ EXCLUDE: 'rent', 'rental', 'hire', 'parts', 'spare parts', 'accessories', 'service', 'repair'\n"
                "❌ EXCLUDE: URLs containing 'rent', 'rental', 'parts', 'service', 'accessories'\n"
                "❌ EXCLUDE: Titles mentioning 'rent', 'rental', 'parts', 'accessories', 'service'\n\n"
                "SEARCH STRATEGIES for SALES ONLY:\n"
                "- Use 'site:ikman.lk/en/ad Honda Fit 2013 for sale' to find Honda Fit sales\n"
                "- Use 'site:riyasewana.com/ad Honda Vezel sale' to find Honda Vezel sales\n"
                "- Add keywords like 'sale' or 'selling' to ensure sales ads\n"
                "- Verify each URL actually leads to a vehicle SALE (not rental/parts)\n\n"
                "AVOID: search pages, rental ads, parts ads, service ads, category pages."
            ),
            "tools": [search_tool, sri_lankan_scraper_tool], # Assign search and Sri Lankan scraper tools
            "allow_delegation": False,
            "verbose": True
        }
        
        # Add LLM if provided
        if llm is not None:
            agent_config["llm"] = llm
        
        return Agent(**agent_config)
