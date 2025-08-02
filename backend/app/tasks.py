# app/tasks.py
from crewai import Task
from textwrap import dedent

class VehicleAnalysisTasks:
    """
    A class to define the tasks for the vehicle analysis crew.
    """
    def vehicle_comparison_task(self, agent, vehicle1, vehicle2) -> Task:
        """
        Task for the expert car reviewer to compare two vehicles.
        """
        return Task(
            description=dedent(f"""
                Conduct a comprehensive, professional comparison of the {vehicle1} and the {vehicle2}.
                
                Your analysis must include ALL of the following sections in proper markdown format:
                
                1. **Executive Summary** - Brief overview of both vehicles and their market positioning
                
                2. **Technical Specifications** - For EACH vehicle include:
                   - Engine details (size, type, cylinders)
                   - Fuel Economy (in both L/100km AND km/l)
                   - Power output (HP @ RPM)
                   - Torque (Nm @ RPM)
                   - Transmission type
                   - Drive type
                
                3. **Reliability & Maintenance** - For EACH vehicle include:
                   - Strengths (reliability aspects)
                   - Common Issues (known problems)
                   - Maintenance Cost (estimated range in LKR)
                
                4. **Pros and Cons** - Clear lists with PROS and CONS sections for EACH vehicle
                
                5. **Market Positioning in Sri Lanka** - For EACH vehicle include:
                   - Target Buyer profile
                   - Price Range (used market in LKR)
                   - Market Share information
                   - Best For (use cases)
                
                6. **Final Recommendation** - When to choose each vehicle
                
                7. **Overall Rating** - Numerical ratings out of 10 for EACH vehicle with breakdown:
                   - Fuel Economy: X/10
                   - Reliability: X/10
                   - Comfort: X/10
                   - Performance: X/10
                   - Value for Money: X/10
                
                The report must be detailed, professional, and specifically focused on the Sri Lankan market.
            """),
            expected_output=dedent(f"""
                A comprehensive markdown-formatted comparison report following this exact structure:
                
                # Vehicle Comparison: {vehicle1} vs {vehicle2}
                
                ## Executive Summary
                [Detailed overview]
                
                ## Technical Specifications
                ### {vehicle1}
                [Complete specs]
                ### {vehicle2}
                [Complete specs]
                
                ## Reliability & Maintenance
                ### {vehicle1}
                [Analysis with costs]
                ### {vehicle2}
                [Analysis with costs]
                
                ## Pros and Cons
                ### {vehicle1}
                **Pros:**
                - [Benefits]
                **Cons:**
                - [Drawbacks]
                
                ### {vehicle2}
                **Pros:**
                - [Benefits]
                **Cons:**
                - [Drawbacks]
                
                ## Market Positioning in Sri Lanka
                [Market analysis for both]
                
                ## Final Recommendation
                [When to choose each]
                
                ## Overall Rating
                ### {vehicle1}: X.X/10
                [Rating breakdown]
                ### {vehicle2}: X.X/10
                [Rating breakdown]
            """),
            agent=agent
        )

    def find_ads_task(self, agent, vehicle) -> Task:
        """
        Task for the local market analyst to find ad URLs.
        """
        return Task(
            description=dedent(f"""
                Search for active advertisements for a '{vehicle}' on popular Sri Lankan websites.
                You must focus your search on 'ikman.lk' and 'riyasewana.com'.
                
                IMPORTANT: You must return individual ad page URLs, NOT search result pages.
                
                Individual ad URLs look like:
                - ikman.lk: https://ikman.lk/en/ad/honda-fit-gp5-2013-for-sale-colombo-12345
                - riyasewana.com: https://riyasewana.com/ad/honda-fit-2015-for-sale-456789
                
                DO NOT return search pages like:
                - https://ikman.lk/en/ads/sri-lanka/cars/honda/fit (This is a search page)
                - https://riyasewana.com/search/cars/honda/fit (This is a search page)
                
                Look for URLs that contain '/ad/' or '/ads/' followed by specific vehicle details.
                Each URL should point to one specific car advertisement, not a list of cars.
                
                Return a list of exactly 5 unique URLs for individual car advertisements.
            """),
            expected_output=dedent("""
                A simple bulleted list containing ONLY the URLs of individual car advertisements.
                Each URL must be a direct link to a specific car's advertisement page.
                
                Format:
                - https://ikman.lk/en/ad/honda-fit-gp5-2013-for-sale-colombo-12345
                - https://ikman.lk/en/ad/honda-fit-2010-for-sale-gampaha-67890
                - https://riyasewana.com/ad/honda-fit-shuttle-2012-78901
                - https://riyasewana.com/ad/honda-fit-2015-blue-45678
                - https://ikman.lk/en/ad/honda-fit-gp1-2014-sale-kandy-34567
            """),
            agent=agent
        )

    def extract_details_task(self, agent, vehicle, context_task) -> Task:
        return Task(
            description=dedent(f"""
                For each URL provided in the context, use your Playwright tool to visit
                the page and extract key details for the '{vehicle}'.

                Extract the following information for EACH advertisement:
                - Ad Title (complete title as shown on the ad)
                - Price (in LKR) - Format as "4,250,000" or "Not Found" if not available
                - Location (city/area in Sri Lanka)
                - Mileage (in km) - IMPORTANT: Interpret mileage intelligently:
                  * If you see just "50" or "50 km" and it's clearly referring to mileage, it likely means "50,000 km"
                  * Common patterns: "just 25km" = "25,000 km", "only 80" = "80,000 km"
                  * Look for context clues like "low mileage", "just", "only" to identify when small numbers refer to thousands
                  * For used cars, mileage under 1,000 km is unusual unless it's brand new
                  * Convert any mileage to standard kilometers format (e.g., "198,000 km")
                - Year of Manufacture (4-digit year like "2004" or "Not Found")
                - URL (the original advertisement URL)

                If a piece of information is not available on the page, use the value 'Not Found'.
                
                CRITICAL: You must return the data as a valid JSON array that can be parsed by Python's json.loads().
            """),
            expected_output=dedent(f"""
                A valid JSON array containing objects for each advertisement. Each object must have this EXACT structure:
                
                [
                  {{
                    "Ad Title": "Nissan March K11 2000 for Sale in Maharagama",
                    "Price (in LKR)": "4,550,000",
                    "Location": "Maharagama",
                    "Mileage (in km)": "198,000 km",
                    "Year of Manufacture": 2000,
                    "URL": "https://ikman.lk/en/ad/nissan-march-k11-2000-for-sale-colombo-1013"
                  }},
                  {{
                    "Ad Title": "Nissan March K12 2004 for Sale in Ja-Ela",
                    "Price (in LKR)": "Not Found",
                    "Location": "Ja-Ela, Gampaha",
                    "Mileage (in km)": "Not Found",
                    "Year of Manufacture": 2004,
                    "URL": "https://ikman.lk/en/ad/nissan-march-k12-2004-for-sale-gampaha-2"
                  }}
                ]
                
                Return ONLY the JSON array, no additional text or explanation.
            """),
            agent=agent,
            context=[context_task]
        )
