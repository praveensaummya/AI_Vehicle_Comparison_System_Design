# AI Vehicle Comparison System - Backend

A production-ready FastAPI backend service that uses CrewAI agents with multi-LLM support (OpenAI GPT-3.5-turbo and Google Gemini 1.5-flash) to compare vehicles and find local advertisements in Sri Lanka. Features intelligent LLM provider selection, robust fallback mechanisms, and comprehensive error handling for system stability.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Installation

1. **Clone and navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers:**
   ```bash
   playwright install
   ```

5. **Set up environment variables:**
   Create a `.env` file in the backend directory:
   ```env
   # OpenAI Configuration (Primary LLM)
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL_NAME=gpt-4o-mini
   
   # Google Gemini Configuration (Secondary LLM)
   GOOGLE_API_KEY=your_google_api_key_here
   GEMINI_API_KEY=your_google_api_key_here
   
   # Search Tool Configuration
   SERPER_API_KEY=your_serper_api_key_here
   
   # Database Configuration
   DATABASE_URL=sqlite:///./vehicle_analysis.db
   ```

6. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

7. **Run the server:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application entry point
│   ├── crew.py                      # OpenAI crew configuration
│   ├── gemini_crew.py               # Gemini crew configuration
│   ├── mock_crew.py                 # Fallback mock crew
│   ├── tasks.py                     # Task definitions for agents
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── comparison_agent.py      # Vehicle comparison agent
│   │   ├── ad_finder_agent.py       # Ad finding agent
│   │   ├── details_extractor_agent.py # Ad details extraction agent
│   │   └── mcp_enhanced_agent.py    # MCP enhanced agent (future)
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── search_tool.py           # Serper search tool
│   │   ├── playwright_scraper.py    # Web scraping tool
│   │   ├── playwright_tool.py       # Playwright integration
│   │   └── mcp_openai_tool.py       # MCP OpenAI tool
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── vehicle_schemas.py       # Pydantic models
│   ├── models/
│   │   ├── __init__.py
│   │   └── ad.py                    # SQLAlchemy Ad model
│   ├── crud/
│   │   ├── __init__.py
│   │   └── ad_crud.py               # Ad CRUD operations
│   ├── utils/
│   │   └── ad_stats.py              # Ad statistics utilities
│   └── core/
│       ├── __init__.py
│       ├── config.py                # Configuration management
│       └── db.py                    # Database configuration
├── scripts/
│   ├── start_mcp_servers.py         # MCP server startup script
│   └── warp-mcp.ps1                 # PowerShell MCP script
├── alembic/                         # Database migrations (auto-generated)
│   ├── versions/
│   └── alembic.ini
├── ads.db                           # SQLite database file
├── requirements.txt                 # Python dependencies
├── mcp-config.json                  # MCP configuration
├── test_openai_connection.py        # OpenAI connection test
├── test_gemini_direct.py            # Gemini connection test
├── run.md                           # Quick run instructions
├── llm_switch.md                    # LLM switching guide
├── .env                             # Environment variables (create this)
├── .gitignore
└── README.md
```

## 🔧 API Endpoints

### POST `/api/v1/analyze-vehicles`

Analyzes two vehicle models and finds local advertisements.

**Request Body:**
```json
{
  "vehicle1": "Toyota Aqua",
  "vehicle2": "Honda Fit"
}
```

**Response:**
```json
{
  "comparison_report": "Detailed markdown comparison...",
  "vehicle1_ads": [
    {
      "title": "Toyota Aqua 2018",
      "price": "LKR 6,500,000",
      "location": "Colombo",
      "mileage": "45,000 km",
      "year": "2018",
      "link": "https://ikman.lk/..."
    }
  ],
  "vehicle2_ads": [...]
}
```

### GET `/`

Health check endpoint.
```json
{
  "message": "Welcome to the AI Vehicle Analyst API"
}
```

## 🤖 AI Agents

### 1. VehicleComparisonAgent
- **Role:** Expert Car Reviewer
- **Goal:** Compare technical specifications, reliability, and expert reviews
- **Output:** Markdown-formatted comparison report

### 2. SriLankanAdFinderAgent
- **Role:** Local Vehicle Market Analyst
- **Goal:** Find active sale listings on Sri Lankan websites
- **Target Sites:** ikman.lk, riyasewana.com
- **Output:** List of advertisement URLs

### 3. AdDetailsExtractorAgent
- **Role:** Ad Data Extractor
- **Goal:** Extract structured data from advertisement pages
- **Output:** JSON objects with price, location, mileage, year, etc.

## 🛠️ Debugging Guide

### Common Issues and Solutions

#### 1. Import Errors
**Problem:** `ModuleNotFoundError: No module named 'app'`
**Solution:**
```bash
# Make sure you're in the backend directory
cd backend

# Install in development mode
pip install -e .
```

#### 2. Environment Variables Not Found
**Problem:** `KeyError: 'OPENAI_API_KEY'`
**Solution:**
- Check that `.env` file exists in backend directory
- Verify API keys are correctly set
- Restart the server after adding environment variables

#### 3. CrewAI Tool Errors
**Problem:** `SerperDevTool` not working
**Solution:**
```bash
# Reinstall crewai with tools
pip uninstall crewai
pip install "crewai[tools]"
```

#### 4. Port Already in Use
**Problem:** `OSError: [Errno 98] Address already in use`
**Solution:**
```bash
# Kill process using port 8080
# Windows
netstat -ano | findstr :8080
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8080 | xargs kill -9
```

### Debug Mode

Run with debug logging:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080 --log-level debug
```

### Testing Individual Components

#### Test Agents Individually
Create a test script `test_agents.py`:
```python
from app.agents.comparison_agent import VehicleComparisonAgent
from app.agents.ad_finder_agent import SriLankanAdFinderAgent
from app.agents.details_extractor_agent import AdDetailsExtractorAgent

# Test comparison agent
comparison_agent = VehicleComparisonAgent().expert_reviewer()
print("Comparison agent created successfully")

# Test ad finder agent
ad_finder_agent = SriLankanAdFinderAgent().ad_finder()
print("Ad finder agent created successfully")

# Test details extractor agent
details_agent = AdDetailsExtractorAgent().details_extractor()
print("Details extractor agent created successfully")
```

#### Test API Endpoint
```bash
curl -X POST "http://localhost:8080/api/v1/analyze-vehicles" \
     -H "Content-Type: application/json" \
     -d '{"vehicle1": "Toyota Aqua", "vehicle2": "Honda Fit"}'
```

## 🔍 Logging and Monitoring

### Enable Detailed Logging
Add to `app/main.py`:
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Monitor Agent Execution
The CrewAI agents run with `verbose=True`, so you'll see detailed execution logs in the console.

## 🚨 Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "detail": "Both vehicle1 and vehicle2 must be provided."
}
```

#### 500 Internal Server Error
```json
{
  "detail": "An internal server error occurred."
}
```

### Custom Error Handling
Add custom exception handlers in `app/main.py`:
```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": f"An error occurred: {str(exc)}"}
    )
```

## 🔧 Configuration

### Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for LLM | Yes |
| `SERPER_API_KEY` | Serper API key for web search | Yes |

### Configuration File
Edit `app/core/config.py` to add more configuration options:
```python
class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")
    
    # Add custom settings
    MAX_ADS_PER_VEHICLE = int(os.getenv("MAX_ADS_PER_VEHICLE", "5"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "300"))
```

## 📊 Performance Optimization

### 1. Parallel Processing
The crew currently runs sequentially. To enable parallel processing:
```python
# In app/crew.py
crew = Crew(
    agents=[...],
    tasks=[...],
    process=Process.hierarchical,  # or Process.sequential
    verbose=2
)
```

### 2. Caching
Add Redis caching for repeated requests:
```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost", encoding="utf8")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
```

### 3. Rate Limiting
Add rate limiting to prevent abuse:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/analyze-vehicles")
@limiter.limit("5/minute")
async def analyze_vehicles(request: Request, vehicle_request: VehicleAnalysisRequest):
    # ... existing code
```

## 🧪 Testing

### Unit Tests
Create `tests/` directory and add test files:
```python
# tests/test_agents.py
import pytest
from app.agents.comparison_agent import VehicleComparisonAgent

def test_comparison_agent_creation():
    agent = VehicleComparisonAgent().expert_reviewer()
    assert agent.role == "Expert Car Reviewer"
```

### Integration Tests
```python
# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_analyze_vehicles():
    response = client.post(
        "/api/v1/analyze-vehicles",
        json={"vehicle1": "Toyota Aqua", "vehicle2": "Honda Fit"}
    )
    assert response.status_code == 200
```

Run tests:
```bash
pytest tests/
```

## 🚀 Deployment

### Docker Deployment
Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Production Settings
```bash
# Use production server
uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 4

# Or with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080
```

## 📝 Development Workflow

### 1. Feature Development
```bash
# Create feature branch
git checkout -b feature/new-agent

# Make changes
# Test locally
uvicorn app.main:app --reload --port 8080

# Commit changes
git add .
git commit -m "Add new agent feature"
```

### 2. Code Quality
```bash
# Install development dependencies
pip install black flake8 mypy

# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the debugging guide above
2. Review the logs for error messages
3. Test individual components
4. Create an issue with detailed error information

## 📄 License

This project is licensed under the MIT License. 