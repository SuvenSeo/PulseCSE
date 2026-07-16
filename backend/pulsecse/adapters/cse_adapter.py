# backend/pulsecse/adapters/cse_adapter.py

"""
CSE Adapter Module

This module provides an adapter for interacting with the CSE (Custom Search Engine) API.
It abstracts away the underlying API calls and provides a simple interface for searching and retrieving results.
"""

from typing import Dict, List
import requests

class CSEAdapter:
    """
    CSE Adapter Class

    This class provides an interface for interacting with the CSE API.
    It encapsulates the API key and provides methods for searching and retrieving results.
    """

    def __init__(self, api_key: str, cse_id: str):
        """
        Initialize the CSE Adapter

        Args:
            api_key (str): The API key for the CSE API
            cse_id (str): The ID of the custom search engine
        """
        self.api_key = api_key
        self.cse_id = cse_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    def search(self, query: str, **kwargs) -> Dict:
        """
        Search the CSE

        Args:
            query (str): The search query
            **kwargs: Additional parameters for the search request (e.g. num, start)

        Returns:
            Dict: The search results
        """
        params = {
            "key": self.api_key,
            "cx": self.cse_id,
            "q": query
        }
        params.update(kwargs)
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        return response.json()

    def get_results(self, query: str, num: int = 10, start: int = 0) -> List[Dict]:
        """
        Get search results

        Args:
            query (str): The search query
            num (int): The number of results to return (default: 10)
            start (int): The starting index of the results (default: 0)

        Returns:
            List[Dict]: The search results
        """
        results = self.search(query, num=num, start=start)
        return results.get("items", [])

# Example usage
if __name__ == "__main__":
    api_key = "YOUR_API_KEY"
    cse_id = "YOUR_CSE_ID"
    adapter = CSEAdapter(api_key, cse_id)
    results = adapter.get_results("example query")
    for result in results:
        print(result["title"], result["link"])