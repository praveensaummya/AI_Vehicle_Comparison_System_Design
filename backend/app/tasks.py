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
                Return a list of the top 5 unique URLs for individual ad pages.
            """),
            expected_output=dedent("""
                A bulleted list containing only the URLs of the 5 most relevant ads.
                Example:
                - https://ikman.lk/en/ad/toyota-vitz-2018-for-sale-colombo
                - https://riyasewana.com/buy/suzuki-swift-rs-2019-for-sale-colombo-3847
            """),
            agent=agent
        )

    def extract_details_task(self, agent, vehicle, context_task) -> Task:
        return Task(
            description=dedent(f"""
                For each URL provided in the context, use your Ad Details Extractor tool to visit
                the page and extract key details for the '{vehicle}'.

                Extract the following information:
                - ad_title
                - price_lkr
                - location
                - mileage_km
                - year

                If a piece of information is not available on the page, use the value 'Not Found'.
            """),
            expected_output=dedent(f"""A clean, python-style list of JSON objects. Each object must represent one advertisement
                and contain the extracted details along with the original link."""),
            agent=agent,
            context=[context_task]
        )
