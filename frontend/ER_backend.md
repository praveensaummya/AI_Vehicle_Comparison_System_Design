# AI Vehicle Comparison System - Backend Entity-Relationship Documentation

## Overview

This document provides comprehensive entity-relationship information for the AI Vehicle Comparison System backend. It's designed to help frontend developers understand data structures, API interactions, and UI component requirements.

## System Architecture

### Agentic System Flow

1. **User Input** → Vehicle Analysis Request
2. **CrewAI Agents Process** → Vehicle Comparison + Ad Finding + Details Extraction
3. **System Output** → Vehicle Analysis Response
4. **Data Storage** → SQLite Database (ads) + Future Vector DB Integration

### Agent Workflow

```
VehicleComparisonAgent (Expert Car Reviewer)
├── Uses: SerperDevTool for web search
├── Output: Markdown-formatted comparison report
└── Process: Technical specs, reliability, pros/cons analysis

SriLankanAdFinderAgent (Local Market Analyst)
├── Uses: SerperDevTool for ikman.lk & riyasewana.com
├── Output: List of advertisement URLs
└── Process: Searches for vehicle listings in Sri Lankan market

AdDetailsExtractorAgent (Ad Data Extractor)
├── Uses: Playwright scraper for web scraping
├── Output: JSON objects with structured ad data
└── Process: Extracts price, location, mileage, year from ad pages
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

## Testing Considerations

### Unit Tests
- Component rendering
- API integration
- Data validation
- Error handling

### Integration Tests
- End-to-end user flows
- API endpoint testing
- Cross-browser compatibility

### Sample Test Data
```json
{
  "vehicle1": "Toyota Aqua",
  "vehicle2": "Honda Fit",
  "expected_ads_count": 5,
  "expected_report_sections": ["Technical Specifications", "Reliability", "Pros and Cons"]
}
```
