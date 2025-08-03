# AI Vehicle Comparison System - Backend Entity-Relationship Documentation

## Overview

This document provides comprehensive entity-relationship information for the AI Vehicle Comparison System backend. It's designed to help frontend developers understand data structures, API interactions, and UI component requirements.

## System Architecture

### Agentic System Flow

1. **User Input** → Vehicle Analysis Request
2. **LLM Provider Selection** → OpenAI (default) or Google Gemini (configurable)
3. **CrewAI Agents Process** → Vehicle Comparison + Ad Finding + Details Extraction
4. **Fallback System** → Mock agents on API failures for system stability
5. **System Output** → Vehicle Analysis Response
6. **Data Storage** → SQLite Database (ads) + Future Vector DB Integration

### Current LLM Provider Configuration

**Primary Provider**: OpenAI GPT-4o-mini (default)
- Model: `gpt-4o-mini`
- Environment: `OPENAI_API_KEY`, `OPENAI_MODEL_NAME`
- Status: Fully functional and stable

**Secondary Provider**: Google Gemini (configurable)
- Model: `gemini-1.5-flash`
- Environment: `GOOGLE_API_KEY`, `GEMINI_API_KEY`
- Configuration: `OPENAI_MODEL_NAME="gemini/gemini-1.5-flash"`, `LITELLM_MODEL="gemini/gemini-1.5-flash"`
- Status: Implemented with LiteLLM routing (Google AI Studio provider)
- Known Issue: LiteLLM occasionally routes to Vertex AI instead of Google AI Studio

**Fallback System**:
- Mock agents activate on API failures
- Provides sample data for system stability
- Prevents complete system downtime
- Logs fallback activation for monitoring

### Agent Workflow

```
VehicleComparisonAgent (Expert Car Reviewer)
├── LLM: OpenAI GPT-4o-mini / Gemini-1.5-flash (configurable)
├── Uses: SerperDevTool for web search
├── Output: Markdown-formatted comparison report
├── Process: Technical specs, reliability, pros/cons analysis
└── Fallback: Mock comparison report on API failure

SriLankanAdFinderAgent (Local Market Analyst)
├── LLM: OpenAI GPT-4o-mini / Gemini-1.5-flash (configurable)
├── Uses: SerperDevTool for ikman.lk & riyasewana.com
├── Output: List of advertisement URLs
├── Process: Searches for vehicle listings in Sri Lankan market
└── Fallback: Mock ad URLs on API failure

AdDetailsExtractorAgent (Ad Data Extractor)
├── LLM: OpenAI GPT-4o-mini / Gemini-1.5-flash (configurable)
├── Uses: requests + BeautifulSoup for web scraping
├── Output: JSON objects with structured ad data
├── Process: Extracts price, location, mileage, year from ad pages
└── Fallback: Mock ad details on API failure
```

## Entities

### 1. Vehicle Analysis Request

**Database Schema**: Not persisted (API request only)

```typescript
interface VehicleAnalysisRequest {
  vehicle1: string;  // Required, non-empty
  vehicle2: string;  // Required, non-empty
}
```

**Validation Rules**:
- Both fields are mandatory
- Minimum length: 2 characters
- Maximum length: 100 characters
- Special characters allowed: spaces, hyphens, parentheses

**Frontend Form Requirements**:
- Input type: text
- Placeholder examples: "Toyota Aqua", "Honda Fit"
- Auto-complete suggestions (optional)
- Real-time validation feedback

**Sample Valid Inputs**:
```json
{
  "vehicle1": "Toyota Aqua",
  "vehicle2": "Honda Fit"
}
```

**User Vehicle Request Capabilities**:
Users can request research on ANY specific vehicle models available in the Sri Lankan market:

- **Popular Japanese Models**: "Toyota Aqua", "Honda Fit", "Suzuki Alto", "Nissan March"
- **Hybrid Vehicles**: "Toyota Prius", "Honda Vezel", "Toyota CH-R"
- **Luxury Vehicles**: "BMW 320i", "Mercedes C200", "Audi A4"
- **SUVs**: "Toyota Fortuner", "Mitsubishi Pajero", "Honda CR-V"
- **Budget Cars**: "Perodua Axia", "Suzuki Wagon R", "Daihatsu Mira"
- **Commercial Vehicles**: "Toyota Hiace", "Nissan Caravan", "Isuzu D-Max"

**Dynamic Vehicle Processing**:
- The system accepts any vehicle name as string input
- AI agents dynamically research the requested vehicles
- No pre-defined vehicle database - uses real-time web search
- Supports various naming formats (e.g., "Honda Fit", "Honda Fit Hybrid", "Fit GP5")

### 2. Advertisement (Ad)

**Database Schema**: `ads` table (SQLite)

```sql
CREATE TABLE ads (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    price VARCHAR(100),
    location VARCHAR(100),
    mileage VARCHAR(50),
    year VARCHAR(10),
    link VARCHAR(500) UNIQUE NOT NULL
);
```

```typescript
interface AdDetails {
  id?: number;           // Auto-generated (database only)
  title: string;         // Ad headline
  price: string;         // Format: "LKR 6,500,000" or "Not Found"
  location: string;      // City/area in Sri Lanka
  mileage: string;       // Format: "45,000 km" or "Not Found"
  year: string;          // Manufacturing year or "Not Found"
  link: string;          // Full URL to original ad
}
```

**Data Formats**:
- **Price**: "LKR 6,500,000", "Rs. 2,800,000", "Negotiable", "Not Found"
- **Location**: "Colombo", "Kandy", "Galle", "Negombo", etc.
- **Mileage**: "45,000 km", "120,000 Km", "Not Found"
- **Year**: "2018", "2015", "Not Found"
- **Link**: Full URLs from ikman.lk, riyasewana.com

**Frontend Display Requirements**:
- Price formatting with currency symbol
- Location with map integration (optional)
- Mileage with unit display
- Year validation (reasonable range: 1990-2024)
- Clickable links opening in new tab

### 3. Vehicle Analysis Response

**Database Schema**: Not persisted (API response only)

```typescript
interface VehicleAnalysisResponse {
  comparison_report: string;        // Markdown-formatted report
  vehicle1_ads: AdDetails[];       // Array of ads for first vehicle
  vehicle2_ads: AdDetails[];       // Array of ads for second vehicle
}
```

**Comparison Report Structure**:
```markdown
# Vehicle Comparison: Toyota Aqua vs Honda Fit

## Technical Specifications
### Toyota Aqua
- Engine: 1.5L Hybrid
- Fuel Economy: 35 km/l
- Power: 74 HP

### Honda Fit
- Engine: 1.3L Petrol
- Fuel Economy: 18 km/l
- Power: 100 HP

## Reliability & Maintenance
...

## Pros and Cons
...
```

**Frontend Rendering Requirements**:
- Markdown parser (react-markdown recommended)
- Responsive table layouts for specifications
- Collapsible sections for better UX
- Side-by-side comparison view

### 4. Vehicle Ads Stats (Additional Feature)

```typescript
interface VehicleAdsStatsRequest {
  ads: AdDetails[];
  min_price?: number;
  max_price?: number;
  year?: number;
  location?: string;
}

interface VehicleAdsStatsResponse {
  ads: AdDetails[];      // Filtered ads
  stats: {
    count: number;
    min_price: number | null;
    max_price: number | null;
    avg_price: number | null;
  };
}
```

## API Endpoints

### 1. Analyze Vehicles

**Endpoint**: `POST /api/v1/analyze-vehicles`

**Request**:
```json
{
  "vehicle1": "Toyota Aqua",
  "vehicle2": "Honda Fit"
}
```

**Response** (Success - 200):
```json
{
  "comparison_report": "# Vehicle Comparison...\n\n## Technical Specifications...",
  "vehicle1_ads": [
    {
      "title": "Toyota Aqua 2018 - Excellent Condition",
      "price": "LKR 6,500,000",
      "location": "Colombo",
      "mileage": "45,000 km",
      "year": "2018",
      "link": "https://ikman.lk/en/ad/toyota-aqua-2018-..."
    }
  ],
  "vehicle2_ads": [...]
}
```

**Error Responses**:
```json
// 400 Bad Request
{
  "detail": "Both vehicle1 and vehicle2 must be provided."
}

// 500 Internal Server Error
{
  "detail": "An internal server error occurred."
}
```

### 2. Vehicle Ads Statistics

**Endpoint**: `POST /api/v1/vehicle-ads-stats`

**Query Parameters**:
- `min_price`: integer (optional)
- `max_price`: integer (optional)
- `year`: integer (optional)
- `location`: string (optional)

### 3. Health Check

**Endpoint**: `GET /`

**Response**:
```json
{
  "message": "Welcome to the AI Vehicle Analyst API"
}
```

## Frontend Component Structure

### Recommended React Components

```tsx
// Main comparison page
function VehicleComparisonPage() {
  return (
    <div>
      <VehicleSelectionForm />
      <ComparisonResults />
    </div>
  );
}

// Vehicle input form
function VehicleSelectionForm() {
  const [vehicle1, setVehicle1] = useState('');
  const [vehicle2, setVehicle2] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Form submission logic
}

// Results display
function ComparisonResults({ data }: { data: VehicleAnalysisResponse }) {
  return (
    <div>
      <ComparisonReport report={data.comparison_report} />
      <AdsSection title="Vehicle 1 Ads" ads={data.vehicle1_ads} />
      <AdsSection title="Vehicle 2 Ads" ads={data.vehicle2_ads} />
    </div>
  );
}

// Individual components
function ComparisonReport({ report }: { report: string }) {
  return <ReactMarkdown>{report}</ReactMarkdown>;
}

function AdsSection({ title, ads }: { title: string; ads: AdDetails[] }) {
  return (
    <section>
      <h2>{title}</h2>
      <div className="ads-grid">
        {ads.map((ad, index) => (
          <AdCard key={index} ad={ad} />
        ))}
      </div>
    </section>
  );
}

function AdCard({ ad }: { ad: AdDetails }) {
  return (
    <div className="ad-card">
      <h3>{ad.title}</h3>
      <p className="price">{ad.price}</p>
      <p className="location">{ad.location}</p>
      <p className="details">{ad.year} • {ad.mileage}</p>
      <a href={ad.link} target="_blank" rel="noopener noreferrer">
        View Details
      </a>
    </div>
  );
}
```

### State Management

```tsx
// Using useState for simple state management
const [comparisonData, setComparisonData] = useState<VehicleAnalysisResponse | null>(null);
const [loading, setLoading] = useState(false);
const [error, setError] = useState<string | null>(null);

// API call function
const analyzeVehicles = async (vehicle1: string, vehicle2: string) => {
  setLoading(true);
  setError(null);
  
  try {
    const response = await fetch('/api/v1/analyze-vehicles', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ vehicle1, vehicle2 }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Analysis failed');
    }
    
    const data = await response.json();
    setComparisonData(data);
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Unknown error');
  } finally {
    setLoading(false);
  }
};
```

## UI/UX Considerations

### Loading States
- Show spinner during API calls (can take 30-60 seconds)
- Progress indicators for different agent stages
- Disable form submission during processing

### Error Handling
- Network errors
- API validation errors
- Agent processing failures
- Empty results handling

### Responsive Design
- Mobile-first approach
- Collapsible comparison sections
- Horizontal scrolling for ad cards
- Touch-friendly interface elements

### Performance Optimization
- Lazy loading for ad images (if added)
- Debounced form inputs
- Memoized components for re-renders
- Virtual scrolling for large ad lists

## Data Validation

### Frontend Validation
```tsx
const validateVehicleInput = (vehicle: string): string | null => {
  if (!vehicle.trim()) {
    return 'Vehicle name is required';
  }
  if (vehicle.length < 2) {
    return 'Vehicle name must be at least 2 characters';
  }
  if (vehicle.length > 100) {
    return 'Vehicle name must be less than 100 characters';
  }
  return null;
};
```

### Backend Validation
- Automatic via Pydantic models
- FastAPI handles validation errors
- Returns structured error responses

## Future Enhancements

### Vector Database Integration
- Store vehicle specifications as embeddings
- Semantic search for similar vehicles
- Recommendation system
- Historical comparison data

### Additional Features
- User favorites/bookmarks
- Price alerts
- Comparison history
- Export to PDF
- Social sharing
- Advanced filtering

## Technical Implementation Details

### Backend Dependencies

**Core Framework**:
- `fastapi` - Web framework for API development
- `uvicorn` - ASGI server for FastAPI
- `pydantic` - Data validation and serialization

**AI/ML Stack**:
- `crewai==0.150.0` - Multi-agent orchestration framework
- `litellm` - Unified LLM API interface
- `langchain-openai` - OpenAI integration
- `langchain-google-genai` - Google Gemini integration
- `google-generativeai` - Direct Google Gemini API access

**Web Scraping & Data Extraction**:
- `requests` - HTTP client for web scraping and API calls
- `beautifulsoup4>=4.12.0` - HTML parsing and data extraction

**Database & Storage**:
- `SQLAlchemy` - ORM for database operations
- `alembic` - Database migration management

**Utilities & Configuration**:
- `python-dotenv` - Environment variable management
- `structlog` - Structured logging
- `coloredlogs` - Enhanced log formatting
- `click` - CLI tool development
- `python-multipart` - Form data handling
- `typing-extensions` - Extended type hints
- `markdown` - Markdown processing

### Environment Configuration

**Required Environment Variables**:
```bash
# OpenAI Configuration (Primary)
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL_NAME=gpt-4o-mini

# Google Gemini Configuration (Secondary)
GOOGLE_API_KEY=your_google_api_key
GEMINI_API_KEY=your_google_api_key  # Same as GOOGLE_API_KEY

# LiteLLM Configuration (for Gemini routing)
LITELLM_MODEL=gemini/gemini-1.5-flash
LITELLM_LOG=DEBUG  # Optional: for debugging routing issues

# Search Tool Configuration
SERPER_API_KEY=your_serper_api_key

# Database Configuration
DATABASE_URL=sqlite:///./vehicle_analysis.db
```

**LLM Provider Switching**:
To switch from OpenAI to Gemini:
```bash
# Clear OpenAI configuration
unset OPENAI_API_KEY
unset OPENAI_MODEL_NAME

# Set Gemini configuration
export OPENAI_MODEL_NAME="gemini/gemini-1.5-flash"
export LITELLM_MODEL="gemini/gemini-1.5-flash"
```

### Deployment Considerations

**Development Setup**:
```bash
# Install dependencies
pip install -r requirements.txt

# No additional browser installation needed for requests/BeautifulSoup

# Run database migrations
alembic upgrade head

# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Production Deployment**:
- Use ASGI server (uvicorn, gunicorn with uvicorn workers)
- Configure environment variables securely
- Set up proper logging and monitoring
- Implement rate limiting for API endpoints
- Configure CORS for frontend integration
- Use reverse proxy (nginx) for static file serving

**Docker Configuration** (Future Enhancement):
```dockerfile
FROM python:3.11-slim

# Install system dependencies (minimal for requests/BeautifulSoup)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . /app
WORKDIR /app

# Run migrations and start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
```

### Performance Optimization

**API Response Times**:
- Expected response time: 30-60 seconds for full analysis
- Implement request queuing for high load
- Cache comparison reports for repeated requests
- Async processing for independent agent tasks

**Database Optimization**:
- Index on `link` field for ad deduplication
- Implement ad data cleanup/archival strategy
- Consider read replicas for high-traffic scenarios

**Memory Management**:
- Monitor HTTP request sessions and connection pooling
- Implement request retry mechanisms with exponential backoff
- Configure appropriate timeouts for web scraping requests

### Error Handling & Monitoring

**Error Categories**:
1. **LLM API Errors**: Rate limits, authentication, model unavailability
2. **Web Scraping Errors**: Site changes, network timeouts, blocked requests
3. **Database Errors**: Connection issues, constraint violations
4. **Agent Processing Errors**: Invalid responses, task failures

**Monitoring Metrics**:
- API response times and success rates
- LLM token usage and costs
- Web scraping success rates
- Database query performance
- Agent fallback activation frequency

**Logging Strategy**:
- Structured logging with `structlog`
- Log levels: DEBUG (development), INFO (production)
- Sensitive data masking (API keys, user inputs)
- Request correlation IDs for tracing

## Testing Considerations

### Unit Tests
- Component rendering
- API integration
- Data validation
- Error handling
- LLM provider switching logic
- Mock agent functionality

### Integration Tests
- End-to-end user flows
- API endpoint testing
- Cross-browser compatibility
- Database migration testing
- Agent workflow validation

### Load Testing
- Concurrent API requests
- LLM API rate limit handling
- HTTP session management and connection pooling
- Database connection pooling

### Sample Test Data
```json
{
  "vehicle1": "Toyota Aqua",
  "vehicle2": "Honda Fit",
  "expected_ads_count": 5,
  "expected_report_sections": ["Technical Specifications", "Reliability", "Pros and Cons"],
  "test_scenarios": {
    "openai_success": "Normal OpenAI operation",
    "gemini_success": "Normal Gemini operation",
    "api_failure": "Mock agent fallback activation",
    "partial_failure": "Some agents succeed, others fail"
  }
}
```
