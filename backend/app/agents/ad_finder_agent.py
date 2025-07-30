# app/agents/ad_finder_agent.py
from crewai import Agent
from app.tools.search_tool import search_tool # Import the tool instance

class SriLankanAdFinderAgent:
    def ad_finder(self) -> Agent:
        """
        Creates an agent that finds vehicle sale listings in the Sri Lankan market.
        """
        return Agent(
            role="Local Vehicle Market Analyst",
            goal=(
                "Find URLs of active sale listings for specific vehicle models on "
                "popular Sri Lankan websites like ikman.lk and riyasewana.com."
            ),
            backstory=(
                "You are a savvy car dealer based in Colombo with an encyclopedic knowledge "
                "of the local online vehicle market. You know exactly how to phrase search "
                "queries to find the best deals and active listings on websites like "
                "ikman.lk and riyasewana.com."
            ),
            tools=[search_tool], # Assign the new Serper tool
            allow_delegation=False,
            verbose=True
        )