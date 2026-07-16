import unittest
from unittest.mock import Mock, patch
from backend.portfolio_analyzer import PortfolioAnalyzer
from backend.models import Stock, Portfolio

class TestPortfolioAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = PortfolioAnalyzer()

    def test_analyze_portfolio(self):
        # Arrange
        portfolio = Portfolio()
        stock1 = Stock(symbol='AAPL', quantity=10)
        stock2 = Stock(symbol='GOOG', quantity=5)
        portfolio.stocks = [stock1, stock2]

        # Act
        result = self.analyzer.analyze_portfolio(portfolio)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    @patch('backend.portfolio_analyzer.Stock')
    def test_get_stock_data(self, mock_stock):
        # Arrange
        symbol = 'AAPL'
        mock_stock.get_data.return_value = {'symbol': symbol, 'price': 100.0}

        # Act
        result = self.analyzer.get_stock_data(symbol)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['symbol'], symbol)

    @patch('backend.portfolio_analyzer.Stock')
    def test_calculate_stock_value(self, mock_stock):
        # Arrange
        symbol = 'AAPL'
        quantity = 10
        mock_stock.get_data.return_value = {'symbol': symbol, 'price': 100.0}

        # Act
        result = self.analyzer.calculate_stock_value(symbol, quantity)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, float)
        self.assertEqual(result, quantity * 100.0)

    def test_calculate_portfolio_value(self):
        # Arrange
        portfolio = Portfolio()
        stock1 = Stock(symbol='AAPL', quantity=10)
        stock2 = Stock(symbol='GOOG', quantity=5)
        portfolio.stocks = [stock1, stock2]
        self.analyzer.get_stock_data = Mock(return_value={'symbol': 'AAPL', 'price': 100.0})
        self.analyzer.get_stock_data = Mock(return_value={'symbol': 'GOOG', 'price': 500.0})

        # Act
        result = self.analyzer.calculate_portfolio_value(portfolio)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, float)
        self.assertEqual(result, (10 * 100.0) + (5 * 500.0))

if __name__ == '__main__':
    unittest.main()