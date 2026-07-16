"""
This module contains the PortfolioAnalyzer class, which is responsible for analyzing a portfolio of stocks.
"""

from typing import List, Dict
from backend.pulsecse.models import Stock
from backend.pulsecse.analyzers.base_analyzer import BaseAnalyzer

class PortfolioAnalyzer(BaseAnalyzer):
    """
    This class analyzes a portfolio of stocks and provides insights into its performance.
    """

    def __init__(self, portfolio: List[Stock]):
        """
        Initializes the PortfolioAnalyzer with a list of Stock objects.

        Args:
        portfolio (List[Stock]): A list of Stock objects to analyze.
        """
        self.portfolio = portfolio

    def calculate_total_value(self) -> float:
        """
        Calculates the total value of the portfolio.

        Returns:
        float: The total value of the portfolio.
        """
        total_value = sum(stock.current_price * stock.shares for stock in self.portfolio)
        return total_value

    def calculate_return_on_investment(self) -> float:
        """
        Calculates the return on investment (ROI) of the portfolio.

        Returns:
        float: The ROI of the portfolio.
        """
        total_value = self.calculate_total_value()
        total_cost = sum(stock.purchase_price * stock.shares for stock in self.portfolio)
        roi = (total_value - total_cost) / total_cost
        return roi

    def get_top_performing_stocks(self, num_stocks: int) -> List[Stock]:
        """
        Gets the top performing stocks in the portfolio.

        Args:
        num_stocks (int): The number of top performing stocks to return.

        Returns:
        List[Stock]: A list of the top performing stocks.
        """
        sorted_stocks = sorted(self.portfolio, key=lambda stock: stock.current_price / stock.purchase_price, reverse=True)
        return sorted_stocks[:num_stocks]

    def get_worst_performing_stocks(self, num_stocks: int) -> List[Stock]:
        """
        Gets the worst performing stocks in the portfolio.

        Args:
        num_stocks (int): The number of worst performing stocks to return.

        Returns:
        List[Stock]: A list of the worst performing stocks.
        """
        sorted_stocks = sorted(self.portfolio, key=lambda stock: stock.current_price / stock.purchase_price)
        return sorted_stocks[:num_stocks]

    def analyze(self) -> Dict:
        """
        Analyzes the portfolio and returns a dictionary with insights.

        Returns:
        Dict: A dictionary with insights into the portfolio's performance.
        """
        total_value = self.calculate_total_value()
        roi = self.calculate_return_on_investment()
        top_performing_stocks = self.get_top_performing_stocks(5)
        worst_performing_stocks = self.get_worst_performing_stocks(5)

        analysis = {
            "total_value": total_value,
            "roi": roi,
            "top_performing_stocks": [stock.symbol for stock in top_performing_stocks],
            "worst_performing_stocks": [stock.symbol for stock in worst_performing_stocks]
        }

        return analysis