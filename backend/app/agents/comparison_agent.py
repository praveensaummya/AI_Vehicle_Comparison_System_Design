from crewai import Agent
from app.tools.search_tool import search_tool # Import the tool instance

class VehicleComparisonAgent:
    def expert_reviewer(self, llm=None) -> Agent:
        """
        Creates an agent that acts as an expert car reviewer.
        """
        agent_config = {
            "role": "Expert Car Reviewer",
            "goal": (
                "Find and summarize all relevant information about two vehicle models. "
                "Focus on technical specifications, expert reviews, reliability, and common problems."
            ),
            "backstory": (
                "You are a world-renowned automotive journalist known for your "
                "in-depth and unbiased reviews. You have a knack for digging deep into "
                "the details and presenting a clear, comprehensive comparison for consumers."
            ),
            "tools": [search_tool], # Assign the new Serper tool
            "allow_delegation": False,
            "verbose": True
        }
        
        # Add LLM if provided
        if llm is not None:
            agent_config["llm"] = llm
        
        return Agent(**agent_config)
