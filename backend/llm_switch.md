# AI Vehicle Comparison System - LLM Provider Switching Guide

This comprehensive guide explains the intelligent LLM (Large Language Model) switching system implemented in the AI Vehicle Comparison platform. The system automatically selects the best available LLM provider based on configuration, API availability, and cost optimization.

## System Overview

The AI Vehicle Comparison System implements an intelligent, production-ready LLM switching architecture that provides:

- **Multi-Provider Support**: Google Gemini (primary), OpenAI (fallback), Mock agents (development/testing)
- **Automatic Failover**: Seamless switching between providers based on availability
- **Cost Optimization**: Prioritizes free-tier models (Gemini) over paid services (OpenAI)
- **Environment-Driven Configuration**: Zero-code provider switching via environment variables
- **Production Resilience**: Graceful fallback to mock agents if all APIs fail

## Current Architecture

### Provider Priority (Intelligent Selection)

1. **Google Gemini 1.5 Flash** (Primary - Free Tier)
   - **Cost**: Free with generous quotas (15 requests/minute, 1500 requests/day)
   - **Performance**: Fast response times, optimized for real-time applications
   - **Context**: 1M token context window
   - **Best For**: Production workloads, high-frequency requests, cost-sensitive deployments

2. **OpenAI GPT-3.5-Turbo** (Secondary - Paid)
   - **Cost**: Pay-per-use ($0.0015/1K input tokens, $0.002/1K output tokens)
   - **Performance**: Excellent quality and reliability
   - **Context**: 16K token context window
   - **Best For**: Enterprise deployments, guaranteed availability, premium features

3. **Mock Agents** (Fallback - Local)
   - **Cost**: Free (no API calls)
   - **Performance**: Instant responses with realistic data
   - **Context**: Pre-generated comprehensive responses
   - **Best For**: Development, testing, API outages, demonstration purposes

### Implementation Components

```
Backend Architecture:
├── app/main.py                 # Intelligent crew selection logic
├── app/core/config.py          # Environment-driven configuration
├── app/crew.py                 # OpenAI-powered crew (legacy/fallback)
├── app/gemini_crew.py          # Gemini-powered crew (primary)
├── app/mock_crew.py            # Mock crew (development/fallback)
└── app/agents/                 # Flexible agent implementations
    ├── comparison_agent.py     # Vehicle comparison specialist
    ├── ad_finder_agent.py      # Sri Lankan marketplace ad finder
    └── details_extractor_agent.py  # Ad details extraction agent
```

## Intelligent Crew Selection Logic

The system uses a sophisticated selection algorithm in `app/main.py` that automatically chooses the optimal LLM provider:

```python
# app/main.py - Intelligent crew selection function
async def _select_optimal_crew(vehicle1: str, vehicle2: str):
    """
    Intelligently select the best available crew based on configuration and API availability
    Priority: Gemini (free + generous) > OpenAI (paid) > Mock (fallback)
    """
    
    # Force mock mode if enabled
    if settings.USE_MOCK_CREW:
        logger.info("Using mock crew (forced by configuration)")
        return MockVehicleAnalysisCrew(vehicle1, vehicle2)
    
    # Try Gemini first (preferred - free and generous quotas)
    if settings.LLM_PROVIDER in ["gemini", "google-gemini"] or settings.LLM_PROVIDER == "auto":
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key_here":
            try:
                logger.info("Selecting Gemini crew (free tier with generous quotas)")
                return GeminiVehicleAnalysisCrew(vehicle1, vehicle2)
            except Exception as e:
                logger.warning("Gemini crew initialization failed, trying alternatives")
    
    # Try OpenAI if Gemini not available or specified
    if settings.LLM_PROVIDER == "openai" or settings.LLM_PROVIDER == "auto":
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your_openai_api_key_here":
            try:
                logger.info("Selecting OpenAI crew (paid service)")
                return VehicleAnalysisCrew(vehicle1, vehicle2)
            except Exception as e:
                logger.warning("OpenAI crew initialization failed, falling back to mock")
    
    # Fallback to mock if no APIs available
    logger.info("Using mock crew (no valid API keys found)")
    return MockVehicleAnalysisCrew(vehicle1, vehicle2)
```

### Error Handling and Resilience

The system includes comprehensive error handling with automatic fallback:

```python
# Automatic API error detection and fallback
is_api_error = (
    "quota" in error_msg.lower() or 
    "rate limit" in error_msg.lower() or 
    "RateLimitError" in str(type(e).__name__) or
    "supports_stop_words" in error_msg or  # CrewAI compatibility issue
    "DefaultCredentialsError" in error_msg or  # Vertex AI auth issue
    "APIConnectionError" in str(type(e).__name__)  # General API connection error
)

if is_api_error:
    logger.warning("API error detected, falling back to mock crew")
    # Automatic fallback to mock crew
    mock_crew = MockVehicleAnalysisCrew(request.vehicle1, request.vehicle2)
    result = mock_crew.run()
```

## Switching to Google Gemini Models

### Prerequisites

1. **Get Google AI API Key**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add it to your `.env` file as `GOOGLE_API_KEY`

2. **Install Required Dependencies**:
   Add to your `requirements.txt`:
   ```
   langchain-google-genai
   google-generativeai
   ```

   Install using:
   ```bash
   pip install langchain-google-genai google-generativeai
   ```

## Current Production Configuration

### Active Configuration (`app/core/config.py`)

The current production system uses the following configuration:

```python
# app/core/config.py - Current Production Implementation
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # LLM Provider Configuration
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()  # gemini, openai, or mock
    
    # OpenAI Configuration (legacy support)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Gemini Configuration (primary)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")  # Free tier model
    
    # Mock Mode Configuration (for testing without API calls)
    USE_MOCK_CREW = os.getenv("USE_MOCK_CREW", "false").lower() == "true"

    # Tool Configuration
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")

settings = Settings()

# Set environment variables for CrewAI tools
os.environ["SERPER_API_KEY"] = settings.SERPER_API_KEY
```

### Current Environment Variables

**Production-Ready `.env` Configuration**:
```env
# Primary LLM Provider (Default: Gemini for cost optimization)
LLM_PROVIDER=gemini  # Options: gemini, openai, auto, mock

# Google Gemini Configuration (Primary - Free Tier)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash  # Options: gemini-1.5-flash, gemini-1.5-pro

# OpenAI Configuration (Fallback - Paid)
OPENAI_API_KEY=your_openai_api_key_here

# Mock Mode (Development/Testing)
USE_MOCK_CREW=false  # Set to "true" for development without API calls

# Search Tool Configuration
SERPER_API_KEY=your_serper_api_key_here
```

**Update your `.env` file**:
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Google Gemini Configuration
GOOGLE_API_KEY=your_google_api_key_here

# LLM Provider Selection (openai, gemini-flash, gemini-pro)
LLM_PROVIDER=gemini-flash

# Other API Keys
SERPER_API_KEY=your_serper_api_key_here
```

### Code Implementation

**Create LLM Factory (`app/core/llm_factory.py`)**:
```python
# app/core/llm_factory.py
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
import structlog

logger = structlog.get_logger()

class LLMFactory:
    @staticmethod
    def create_llm():
        """Create LLM instance based on configuration"""
        provider = settings.LLM_PROVIDER.lower()
        
        if provider == "openai":
            logger.info("Initializing OpenAI GPT-4o model")
            return ChatOpenAI(
                model_name="gpt-4o",
                api_key=settings.OPENAI_API_KEY,
                temperature=0.1
            )
        
        elif provider == "gemini-flash":
            logger.info("Initializing Google Gemini Flash model")
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=0.1,
                convert_system_message_to_human=True
            )
        
        elif provider == "gemini-pro":
            logger.info("Initializing Google Gemini Pro model")
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=0.1,
                convert_system_message_to_human=True
            )
        
        else:
            logger.warning(f"Unknown LLM provider: {provider}, falling back to OpenAI")
            return ChatOpenAI(
                model_name="gpt-4o",
                api_key=settings.OPENAI_API_KEY,
                temperature=0.1
            )
```

**Update `app/crew.py`**:
```python
# app/crew.py
from crewai import Crew, Process
from app.agents.comparison_agent import VehicleComparisonAgent
from app.agents.ad_finder_agent import SriLankanAdFinderAgent
from app.agents.details_extractor_agent import AdDetailsExtractorAgent
from app.tasks import VehicleAnalysisTasks
from app.core.config import settings
from app.core.llm_factory import LLMFactory  # Import the factory
import json
import structlog

class VehicleAnalysisCrew:
    def __init__(self, vehicle1: str, vehicle2: str):
        self.logger = structlog.get_logger()
        self.vehicle1 = vehicle1
        self.vehicle2 = vehicle2
        self.llm = LLMFactory.create_llm()  # Use factory instead of direct instantiation
        self.logger.info("VehicleAnalysisCrew initialized", 
                        vehicle1=vehicle1, 
                        vehicle2=vehicle2,
                        llm_provider=settings.LLM_PROVIDER)
    
    # Rest of the class remains the same...
```

**Update Agent Classes (Optional - for individual agent LLM control)**:

If you want individual agents to use specific LLMs, update each agent:

```python
# app/agents/comparison_agent.py
from crewai import Agent
from app.tools.search_tool import search_tool
from app.core.llm_factory import LLMFactory

class VehicleComparisonAgent:
    def expert_reviewer(self) -> Agent:
        """
        Creates an agent that acts as an expert car reviewer.
        """
        return Agent(
            role="Expert Car Reviewer",
            goal=(
                "Find and summarize all relevant information about two vehicle models. "
                "Focus on technical specifications, expert reviews, reliability, and common problems."
            ),
            backstory=(
                "You are a world-renowned automotive journalist known for your "
                "in-depth and unbiased reviews. You have a knack for digging deep into "
                "the details and presenting a clear, comprehensive comparison for consumers."
            ),
            tools=[search_tool],
            allow_delegation=False,
            verbose=True,
            llm=LLMFactory.create_llm()  # Add this line for agent-specific LLM
        )
```

### Model Characteristics

**Gemini Flash 1.5**:
- **Speed**: Fastest Google model, optimized for low-latency use cases
- **Cost**: Most cost-effective Google option
- **Context**: 1M token context window
- **Best for**: Real-time applications, high-frequency requests
- **Use case**: Quick vehicle comparisons, ad extraction

**Gemini Pro 1.5**:
- **Speed**: Slower than Flash but more capable
- **Quality**: Higher quality outputs, better reasoning
- **Context**: 2M token context window
- **Best for**: Complex analysis, detailed comparisons
- **Use case**: In-depth vehicle analysis, comprehensive reports

### Environment Variables Setup

**For Development**:
```env
# Use Gemini Flash for faster development
LLM_PROVIDER=gemini-flash
GOOGLE_API_KEY=your_google_api_key_here
```

**For Production**:
```env
# Use Gemini Pro for better quality
LLM_PROVIDER=gemini-pro
GOOGLE_API_KEY=your_google_api_key_here
```

### Testing the Integration

**Create a test script (`test_gemini.py`)**:
```python
# test_gemini.py
from app.core.llm_factory import LLMFactory
from app.core.config import settings

def test_gemini_integration():
    """Test Gemini model integration"""
    llm = LLMFactory.create_llm()
    
    test_prompt = "Compare Toyota Aqua and Honda Fit in 3 sentences."
    response = llm.invoke(test_prompt)
    
    print(f"LLM Provider: {settings.LLM_PROVIDER}")
    print(f"Response: {response.content}")
    
if __name__ == "__main__":
    test_gemini_integration()
```

Run the test:
```bash
python test_gemini.py
```

### Performance Considerations

1. **Rate Limits**:
   - Gemini Flash: Higher rate limits, suitable for production
   - Gemini Pro: Lower rate limits, use for quality-critical tasks

2. **Cost Optimization**:
   - Use Gemini Flash for preliminary analysis
   - Switch to Gemini Pro for final detailed reports

3. **Fallback Strategy**:
   ```python
   # In llm_factory.py, add error handling
   try:
       return ChatGoogleGenerativeAI(...)
   except Exception as e:
       logger.error(f"Failed to initialize Gemini: {e}")
       logger.info("Falling back to OpenAI")
       return ChatOpenAI(...)
   ```

## Current Gemini Implementation Details

### Gemini Crew Implementation (`app/gemini_crew.py`)

The current production system uses an optimized Gemini crew with enhanced error handling:

```python
# Key features of the current Gemini implementation:

1. **Environment Variable Routing**: 
   - Uses LiteLLM format: "gemini/gemini-1.5-flash"
   - Forces Google AI Studio (prevents Vertex AI routing)
   - Clears conflicting environment variables

2. **API Key Validation**:
   - Comprehensive validation with detailed error messages
   - Direct connection test to verify API key works
   - Clear guidance for obtaining API keys

3. **CrewAI Integration**:
   - Environment-driven LLM configuration (no explicit LLM objects)
   - Avoids compatibility issues with CrewAI's internal LLM handling
   - Optimized crew settings (cache enabled, memory disabled)

4. **Error Resilience**:
   - Automatic fallback to OpenAI/Mock crews on failure
   - Comprehensive error detection and logging
   - Production-ready error handling
```

### Provider-Specific Optimizations

**Gemini Crew Optimizations**:
- **Cache**: Enabled (Gemini benefits from caching)
- **Memory**: Disabled (better performance)
- **Model**: gemini-1.5-flash (free tier, fast)
- **Environment**: Google AI Studio (not Vertex AI)

**OpenAI Crew Optimizations**:
- **Cache**: Disabled (fresh results preferred)
- **Memory**: Disabled (faster execution)
- **Model**: gpt-3.5-turbo (cost-effective)
- **Environment**: Direct OpenAI API

**Mock Crew Features**:
- **Instant responses**: No API delays
- **Realistic data**: Comprehensive mock comparisons
- **Consistent output**: Predictable for testing
- **Full feature parity**: Complete vehicle analysis simulation

### Usage Patterns and Best Practices

#### Development Workflow

1. **Local Development**:
   ```env
   USE_MOCK_CREW=true  # Fast development without API costs
   LLM_PROVIDER=mock
   ```

2. **Testing with Real APIs**:
   ```env
   USE_MOCK_CREW=false
   LLM_PROVIDER=gemini  # Free tier for testing
   GEMINI_API_KEY=your_key_here
   ```

3. **Production Deployment**:
   ```env
   LLM_PROVIDER=auto  # Intelligent selection
   GEMINI_API_KEY=your_gemini_key
   OPENAI_API_KEY=your_openai_key  # Fallback
   USE_MOCK_CREW=false
   ```

#### API Health Monitoring

The system includes built-in health checks:

```python
# Available endpoints for monitoring:

GET /api/v1/health  # Overall system health
# Returns:
{
    "status": "healthy",
    "services": {
        "api": "operational",
        "openai_configured": true,
        "serper_configured": true,
        "mock_mode": false
    }
}

POST /api/v1/test-openai  # Test OpenAI connectivity
# Returns API status, quota information, and suggestions
```

### Switching Providers at Runtime

#### Quick Provider Switch

**Switch to Gemini (Free)**:
```bash
# Update .env file
echo "LLM_PROVIDER=gemini" >> .env
echo "GEMINI_API_KEY=your_key_here" >> .env

# Restart backend
uvicorn app.main:app --reload
```

**Switch to OpenAI (Paid)**:
```bash
# Update .env file
echo "LLM_PROVIDER=openai" >> .env
echo "OPENAI_API_KEY=your_key_here" >> .env

# Restart backend
uvicorn app.main:app --reload
```

**Enable Mock Mode (Development)**:
```bash
# Update .env file
echo "USE_MOCK_CREW=true" >> .env

# Restart backend (no API keys needed)
uvicorn app.main:app --reload
```

### Cost Optimization Strategies

1. **Development Phase**:
   - Use `USE_MOCK_CREW=true` for UI development
   - Switch to Gemini for integration testing
   - Minimize API calls during development

2. **Production Phase**:
   - Primary: Gemini (free tier, 1500 requests/day)
   - Fallback: OpenAI (paid, guaranteed availability)
   - Emergency: Mock crew (system always available)

3. **Scaling Considerations**:
   - Monitor Gemini quota usage
   - Implement request caching for repeated queries
   - Consider Gemini Pro for high-quality requirements
   - Load balance between multiple API keys if needed

### Troubleshooting Common Issues

#### Gemini API Issues

```bash
# Issue: "supports_stop_words" error
# Solution: Use environment-driven configuration (current implementation)

# Issue: Vertex AI authentication error
# Solution: Clear Google Cloud credentials (implemented in gemini_crew.py)

# Issue: Rate limiting
# Solution: Automatic fallback to OpenAI/Mock crews
```

#### OpenAI API Issues

```bash
# Issue: Quota exceeded
# Solution: System automatically falls back to mock crew

# Issue: Invalid API key
# Solution: Check /api/v1/test-openai endpoint for diagnosis

# Issue: Network connectivity
# Solution: Automatic fallback to mock crew maintains service
```

### Migration Checklist

**Current System (Already Implemented)**:
- [x] Multi-provider architecture
- [x] Intelligent crew selection
- [x] Environment-driven configuration
- [x] Automatic error handling and fallback
- [x] Production-ready Gemini integration
- [x] Comprehensive logging and monitoring
- [x] Mock crew for development/testing
- [x] API health check endpoints

**For Adding New Providers**:
- [ ] Create new crew class (follow gemini_crew.py pattern)
- [ ] Add provider configuration to config.py
- [ ] Update intelligent selection logic in main.py
- [ ] Add provider-specific optimizations
- [ ] Implement error handling and fallback
- [ ] Add health check endpoints
- [ ] Update documentation
- [ ] Test thoroughly with real API calls

## Advanced Configuration

### Custom LLM Factory (Alternative Approach)

If you prefer explicit LLM instantiation over environment-driven configuration:

```python
# app/core/llm_factory.py - Alternative implementation
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from app.core.config import settings
import structlog

class LLMFactory:
    @staticmethod
    def create_llm(provider: str = None):
        """Create LLM with explicit provider override"""
        provider = provider or settings.LLM_PROVIDER
        logger = structlog.get_logger()
        
        try:
            if provider == "gemini":
                return ChatGoogleGenerativeAI(
                    model=settings.GEMINI_MODEL,
                    google_api_key=settings.GEMINI_API_KEY,
                    temperature=0.1
                )
            elif provider == "openai":
                return ChatOpenAI(
                    model="gpt-3.5-turbo",
                    api_key=settings.OPENAI_API_KEY,
                    temperature=0.1
                )
            else:
                logger.warning(f"Unknown provider {provider}, using OpenAI")
                return ChatOpenAI(
                    model="gpt-3.5-turbo",
                    api_key=settings.OPENAI_API_KEY,
                    temperature=0.1
                )
        except Exception as e:
            logger.error(f"Failed to create {provider} LLM: {e}")
            raise
```

### Enterprise Deployment Considerations

1. **Load Balancing**:
   - Multiple API keys for higher quotas
   - Round-robin selection between keys
   - Health checking of individual keys

2. **Monitoring and Alerting**:
   - API usage tracking
   - Cost monitoring and alerts
   - Performance metrics and dashboards

3. **Security**:
   - API key rotation policies
   - Environment variable encryption
   - Access logging and audit trails

4. **Scaling**:
   - Horizontal scaling with consistent provider selection
   - Database-driven configuration for multi-instance deployments
   - Centralized logging and monitoring

---

## Summary

The AI Vehicle Comparison System implements a sophisticated, production-ready LLM switching architecture that:

- **Prioritizes cost optimization** by using free-tier Gemini as primary provider
- **Ensures reliability** through automatic fallback to paid OpenAI service
- **Maintains availability** with mock crew fallback for development and outages
- **Simplifies deployment** through environment-driven configuration
- **Provides monitoring** with comprehensive health checks and logging

This architecture enables zero-downtime provider switching, cost-effective operation, and reliable service delivery while maintaining flexibility for future LLM provider integrations.
