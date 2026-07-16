# backend/tests/test_portfolio_model.py

"""
Tests for the Portfolio model.
"""

from django.test import TestCase
from backend.models import Portfolio

class TestPortfolioModel(TestCase):
    """
    Test case for the Portfolio model.
    """

    def setUp(self):
        """
        Set up test data.
        """
        self.portfolio = Portfolio.objects.create(
            title="Test Portfolio",
            description="This is a test portfolio.",
            url="https://example.com",
        )

    def test_portfolio_creation(self):
        """
        Test that a portfolio can be created.
        """
        self.assertEqual(self.portfolio.title, "Test Portfolio")
        self.assertEqual(self.portfolio.description, "This is a test portfolio.")
        self.assertEqual(self.portfolio.url, "https://example.com")

    def test_portfolio_str_representation(self):
        """
        Test the string representation of a portfolio.
        """
        self.assertEqual(str(self.portfolio), "Test Portfolio")

    def test_portfolio_save(self):
        """
        Test that a portfolio can be saved.
        """
        self.portfolio.save()
        self.assertEqual(Portfolio.objects.count(), 1)

    def test_portfolio_delete(self):
        """
        Test that a portfolio can be deleted.
        """
        self.portfolio.delete()
        self.assertEqual(Portfolio.objects.count(), 0)