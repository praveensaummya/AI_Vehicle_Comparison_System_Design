"""
MCP Enhanced Agent for AI Vehicle Comparison System
This agent leverages MCP OpenAI server for enhanced analysis capabilities.
"""

from crewai import Agent
from app.tools.mcp_openai_tool import create_mcp_openai_tool
import structlog

logger = structlog.get_logger()

class MCPEnhancedAgent:
    """
    Enhanced agent that uses MCP OpenAI server for advanced analysis
    """
    
    def __init__(self):
        self.logger = logger
        self.mcp_tool = create_mcp_openai_tool()
    
    def enhanced_comparison_agent(self) -> Agent:
        """
        Create an enhanced vehicle comparison agent with MCP OpenAI capabilities
        """
        return Agent(
            role="MCP Enhanced Vehicle Analyst",
            goal="Provide comprehensive vehicle analysis using advanced AI capabilities through MCP OpenAI server",
            backstory="""You are an expert automotive analyst with access to advanced AI tools through 
            the Model Context Protocol (MCP). You can leverage OpenAI's most advanced models to provide 
            detailed, accurate, and insightful vehicle comparisons specifically tailored for the Sri Lankan market.
            
            Your expertise includes:
            - Deep technical knowledge of vehicles popular in Sri Lanka
            - Understanding of local market conditions and pricing
            - Access to real-time AI analysis through MCP OpenAI server
            - Ability to provide structured, actionable insights
            """,
            verbose=True,
            allow_delegation=False,
            tools=[],  # MCP tools will be called programmatically
            max_iter=3
        )
    
    def intelligent_ad_analyzer_agent(self) -> Agent:
        """
        Create an intelligent ad analyzer agent with MCP OpenAI capabilities
        """
        return Agent(
            role="MCP Intelligent Ad Analyzer",
            goal="Analyze vehicle advertisements with advanced AI to extract insights and identify opportunities",
            backstory="""You are an intelligent advertisement analyzer with access to advanced AI capabilities 
            through MCP OpenAI server. You can understand nuanced language, identify key selling points, 
            spot potential issues, and provide valuable insights for car buyers.
            
            Your capabilities include:
            - Natural language understanding of ad content
            - Market price comparison and reasonableness assessment
            - Identification of negotiation opportunities
            - Risk assessment and red flag detection
            - Structured insight generation
            """,
            verbose=True,
            allow_delegation=False,
            tools=[],  # MCP tools will be called programmatically
            max_iter=2
        )
    
    def smart_search_optimizer_agent(self) -> Agent:
        """
        Create a smart search optimizer agent with MCP OpenAI capabilities
        """
        return Agent(
            role="MCP Smart Search Optimizer",
            goal="Generate optimized search queries for finding vehicle advertisements using AI insights",
            backstory="""You are a smart search optimization specialist with access to advanced AI through 
            MCP OpenAI server. You understand how people search for cars in Sri Lanka and can generate 
            highly effective search queries that maximize the chances of finding relevant advertisements.
            
            Your expertise includes:
            - Understanding Sri Lankan vehicle naming conventions
            - Knowledge of popular model variations and trim levels
            - Search engine optimization for local websites
            - Query generation that accounts for common misspellings and variations
            """,
            verbose=True,
            allow_delegation=False,
            tools=[],  # MCP tools will be called programmatically
            max_iter=2
        )

# Factory functions for easy integration
def create_enhanced_comparison_agent() -> Agent:
    """Factory function to create enhanced comparison agent"""
    mcp_agent = MCPEnhancedAgent()
    return mcp_agent.enhanced_comparison_agent()

def create_intelligent_ad_analyzer() -> Agent:
    """Factory function to create intelligent ad analyzer agent"""
    mcp_agent = MCPEnhancedAgent()
    return mcp_agent.intelligent_ad_analyzer_agent()

def create_smart_search_optimizer() -> Agent:
    """Factory function to create smart search optimizer agent"""
    mcp_agent = MCPEnhancedAgent()
    return mcp_agent.smart_search_optimizer_agent()
