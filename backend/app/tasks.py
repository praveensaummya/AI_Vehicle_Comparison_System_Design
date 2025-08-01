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
                Conduct a detailed comparison of the {vehicle1} and the {vehicle2}.
                Your final report should be a comprehensive, easy-to-read summary
                covering the following aspects for both vehicles:
                - Technical Specifications (Engine Size, Fuel Economy in L/100km or km/l, Power, Torque)
                - Reliability and Maintenance (Common problems, owner feedback)
                - Pros and Cons
            """),
            expected_output=dedent(f"""
                A detailed markdown-formatted report that provides a side-by-side
                comparison of the {vehicle1} and {vehicle2}.
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

                Extract the following information:
                - Ad Title
                - Price (in LKR)
                - Location
                - Mileage (in km) - IMPORTANT: Interpret mileage intelligently:
                  * If you see just "50" or "50 km" and it's clearly referring to mileage, it likely means "50,000 km"
                  * Common patterns: "just 25km" = "25,000 km", "only 80" = "80,000 km"
                  * Look for context clues like "low mileage", "just", "only" to identify when small numbers refer to thousands
                  * For used cars, mileage under 1,000 km is unusual unless it's brand new
                  * Convert any mileage to standard kilometers format (e.g., "25,000 km")
                - Year of Manufacture

                If a piece of information is not available on the page, use the value 'Not Found'.
            """),
            expected_output=dedent(f"""
                A clean, python-style list of JSON objects. Each object must represent one advertisement
                and contain the extracted details along with the original link.
            """),
            agent=agent,
            context=[context_task]
        )