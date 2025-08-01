# app/mock_crew.py
import structlog
import time
import json

class MockVehicleAnalysisCrew:
    """
    Mock implementation for testing without OpenAI API calls.
    This allows frontend development and testing while resolving OpenAI billing issues.
    """
    def __init__(self, vehicle1: str, vehicle2: str):
        self.logger = structlog.get_logger()
        self.vehicle1 = vehicle1
        self.vehicle2 = vehicle2
        self.logger.info("MockVehicleAnalysisCrew initialized", 
                        vehicle1=vehicle1, 
                        vehicle2=vehicle2)

    def run(self):
        self.logger.info("Starting mock crew execution workflow")
        
        # Simulate realistic processing time
        time.sleep(3)
        
        # Generate comprehensive mock comparison report
        comparison_report = self._generate_mock_comparison()
        
        # Generate mock vehicle ads
        vehicle1_ads = self._generate_mock_ads(self.vehicle1, base_price=4500000)
        vehicle2_ads = self._generate_mock_ads(self.vehicle2, base_price=3800000)

        final_output = {
            "comparison_report": comparison_report,
            "vehicle1_ads": vehicle1_ads,
            "vehicle2_ads": vehicle2_ads
        }
        
        self.logger.info("Mock crew results processed successfully", 
                        has_comparison=bool(final_output.get('comparison_report')),
                        vehicle1_ads_count=len(final_output.get('vehicle1_ads', [])),
                        vehicle2_ads_count=len(final_output.get('vehicle2_ads', [])))
        
        return final_output

    def _generate_mock_comparison(self) -> str:
        """Generate a realistic mock comparison report"""
        return f"""# Vehicle Comparison: {self.vehicle1} vs {self.vehicle2}

## Executive Summary

Both the {self.vehicle1} and {self.vehicle2} are popular compact cars in the Sri Lankan market, each offering distinct advantages for different types of buyers.

## Technical Specifications

### {self.vehicle1}
- **Engine**: 1.2L 3-cylinder petrol engine
- **Fuel Economy**: 5.2 L/100km (19.2 km/l)
- **Power**: 79 HP @ 6,000 rpm
- **Torque**: 106 Nm @ 4,400 rpm
- **Transmission**: CVT Automatic
- **Drive Type**: Front-wheel drive

### {self.vehicle2}
- **Engine**: 1.3L 4-cylinder petrol engine
- **Fuel Economy**: 5.8 L/100km (17.2 km/l)
- **Power**: 100 HP @ 6,000 rpm
- **Torque**: 127 Nm @ 4,800 rpm
- **Transmission**: CVT Automatic
- **Drive Type**: Front-wheel drive

## Reliability & Maintenance

### {self.vehicle1}
**Strengths:**
- Simple, reliable 3-cylinder engine
- Lower maintenance costs due to fewer parts
- Good availability of spare parts in Sri Lanka
- Strong dealer network

**Common Issues:**
- CVT transmission can be jerky at low speeds
- Interior plastics may feel cheap
- Road noise at highway speeds
- Limited rear seat space

**Maintenance Cost**: LKR 15,000 - 25,000 per service

### {self.vehicle2}
**Strengths:**
- Proven 4-cylinder engine reliability
- Better interior space and comfort
- Superior build quality
- Excellent resale value

**Common Issues:**
- Higher fuel consumption than competitors
- CVT transmission requires careful maintenance
- Air conditioning compressor issues (older models)
- Door handles may break with heavy use

**Maintenance Cost**: LKR 18,000 - 30,000 per service

## Pros and Cons

### {self.vehicle1}
**Pros:**
✅ Excellent fuel economy
✅ Compact size ideal for city driving
✅ Lower insurance and registration costs
✅ Easy parking in tight spaces
✅ Affordable maintenance

**Cons:**
❌ Limited power for highway driving
❌ Basic interior features
❌ Small boot space
❌ Three-cylinder engine vibration
❌ Limited rear passenger comfort

### {self.vehicle2}
**Pros:**
✅ More powerful and refined engine
✅ Better interior space and comfort
✅ Superior build quality and materials
✅ Strong brand reputation
✅ Excellent resale value

**Cons:**
❌ Higher fuel consumption
❌ More expensive to maintain
❌ Higher insurance costs
❌ Premium pricing in used market
❌ CVT transmission can be sluggish

## Market Positioning in Sri Lanka

### {self.vehicle1}
- **Target Buyer**: First-time car buyers, city commuters, budget-conscious families
- **Price Range**: LKR 3,200,000 - 4,800,000 (used market)
- **Market Share**: Strong in entry-level segment
- **Best For**: Daily city commuting, fuel efficiency priority

### {self.vehicle2}
- **Target Buyer**: Small families, quality-conscious buyers, brand loyalists
- **Price Range**: LKR 3,800,000 - 5,500,000 (used market)
- **Market Share**: Dominant in compact car segment
- **Best For**: Balanced performance, family use, resale value

## Final Recommendation

**Choose {self.vehicle1} if:**
- Fuel economy is your top priority
- You primarily drive in city conditions
- Budget is a major constraint
- You value lower running costs

**Choose {self.vehicle2} if:**
- You want better overall refinement
- Family comfort is important
- You plan to keep the car long-term
- Resale value matters to you

## Overall Rating

### {self.vehicle1}: 7.5/10
- Fuel Economy: 9/10
- Reliability: 8/10
- Comfort: 6/10
- Performance: 6/10
- Value for Money: 9/10

### {self.vehicle2}: 8.2/10
- Fuel Economy: 7/10
- Reliability: 9/10
- Comfort: 8/10
- Performance: 8/10
- Value for Money: 7/10

Both vehicles offer excellent value in their respective segments. Your choice should depend on your specific priorities and budget constraints."""

    def _generate_mock_ads(self, vehicle: str, base_price: int) -> list:
        """Generate realistic mock advertisements"""
        import random
        
        locations = ["Colombo", "Kandy", "Galle", "Negombo", "Kurunegala", "Ratnapura", "Anuradhapura"]
        years = ["2018", "2019", "2020", "2021", "2022"]
        
        ads = []
        for i in range(random.randint(3, 6)):
            year = random.choice(years)
            location = random.choice(locations)
            mileage = random.randint(25000, 85000)
            
            # Price varies based on year and mileage
            year_factor = (2023 - int(year)) * 200000
            mileage_factor = mileage * 10
            price = base_price - year_factor - mileage_factor + random.randint(-300000, 300000)
            
            price_str = f"LKR {price:,}"
            if random.random() < 0.1:  # 10% chance of "Negotiable"
                price_str = "Negotiable"
            elif random.random() < 0.05:  # 5% chance of "Contact for Price"
                price_str = "Contact for Price"
            
            condition_words = ["Excellent", "Very Good", "Good", "Well Maintained", "Perfect", "Mint"]
            condition = random.choice(condition_words)
            
            ads.append({
                "title": f"{vehicle} {year} - {condition} Condition",
                "price": price_str,
                "location": location,
                "mileage": f"{mileage:,} km",
                "year": year,
                "link": f"https://ikman.lk/en/ad/{vehicle.lower().replace(' ', '-')}-{year}-{i+1}"
            })
        
        return ads
