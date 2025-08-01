# Switching LLM Modules

This guide outlines how to switch or integrate different LLM (Large Language Model) modules within your agentic system.

## Current Setup

- **Current LLM**: OpenAI using `langchain-openai` and the `ChatOpenAI` class.
- **Current Config**: Update LLM settings in `app/core/config.py`.

## Steps to Switch or Add LLM Modules

1. **Identify and Choose New LLM Provider**
   - Options include Hugging Face Transformers, other OpenAI models, etc.
   - Ensure the chosen provider offers the models and features required.

2. **Install Necessary Libraries**
   - Update your `requirements.txt` with libraries for the new LLM.
   - Example: For Hugging Face, add `transformers`, `torch`, etc.

3. **Modify Configuration**
   - Update the `app/core/config.py` with credentials or API keys.
   - Example: Add `HUGGINGFACE_API_KEY` to your environment and access it similarly.

4. **Update Agent Code**
   - Modify agents like `VehicleComparisonAgent` and crew modules to use the new LLM.
   - Instantiate these LLMs through their respective APIs or SDKs.

5. **Testing and Validation**
   - Create or update unit tests validating changes.
   - Test each agent workflow and ensure the interactions generate expected outputs.

6. **Considerations for Performance**
   - Ensure efficient API call management to minimize latency and costs.
   - Optimize LLM usage for responses by pruning unnecessary data processing.

## Example Update for New LLM

### Hugging Face Example

- **Config Update**:
  ```python
  class Settings:
      # Add new LLM API keys
      HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
  ```

- **Agent Update**:
  Example for using Hugging Face:
  ```python
  from transformers import pipeline
  # Set up pipeline
  classifier = pipeline('sentiment-analysis', api_key=settings.HUGGINGFACE_API_KEY)
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

### Configuration Updates

**Update `app/core/config.py`**:
```python
# app/core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # LLM and Agent Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # Add this line
    
    # LLM Model Selection
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # openai, gemini-flash, gemini-pro
    
    # Tool Configuration
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")

settings = Settings()

# Set environment variables for CrewAI tools
os.environ["SERPER_API_KEY"] = settings.SERPER_API_KEY
if settings.GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
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

### Migration Checklist

- [ ] Install required dependencies
- [ ] Obtain Google AI API key
- [ ] Update configuration files
- [ ] Create LLM factory
- [ ] Update crew initialization
- [ ] Test with sample requests
- [ ] Monitor performance and costs
- [ ] Update documentation

## Final Steps

- Document changes and configurations.
- Provide training or walkthroughs for team members to handle updates.

---
By following this guide, you can effectively switch or integrate new LLM modules into your existing system.
