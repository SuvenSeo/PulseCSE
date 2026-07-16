from backend.pulsecse.models import Portfolio
from django.core.exceptions import ObjectDoesNotExist

class PortfolioService:
    def __init__(self):
        pass

    def get_all_portfolios(self):
        """
        Returns all portfolios.
        """
        return Portfolio.objects.all()

    def get_portfolio_by_id(self, id):
        """
        Returns a portfolio by id.

        Args:
            id (int): The id of the portfolio.

        Returns:
            Portfolio: The portfolio object.
        """
        try:
            return Portfolio.objects.get(id=id)
        except ObjectDoesNotExist:
            return None

    def create_portfolio(self, **kwargs):
        """
        Creates a new portfolio.

        Args:
            **kwargs: The portfolio data.

        Returns:
            Portfolio: The created portfolio object.
        """
        return Portfolio.objects.create(**kwargs)

    def update_portfolio(self, id, **kwargs):
        """
        Updates a portfolio.

        Args:
            id (int): The id of the portfolio.
            **kwargs: The updated portfolio data.

        Returns:
            Portfolio: The updated portfolio object.
        """
        try:
            portfolio = Portfolio.objects.get(id=id)
            for key, value in kwargs.items():
                setattr(portfolio, key, value)
            portfolio.save()
            return portfolio
        except ObjectDoesNotExist:
            return None

    def delete_portfolio(self, id):
        """
        Deletes a portfolio.

        Args:
            id (int): The id of the portfolio.

        Returns:
            bool: True if the portfolio was deleted, False otherwise.
        """
        try:
            portfolio = Portfolio.objects.get(id=id)
            portfolio.delete()
            return True
        except ObjectDoesNotExist:
            return False