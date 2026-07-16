import unittest
from unittest.mock import Mock, patch
from backend.services import portfolio_service

class TestPortfolioService(unittest.TestCase):

    def test_get_portfolio(self):
        # Arrange
        portfolio_id = 1
        portfolio_data = {
            'id': portfolio_id,
            'name': 'Test Portfolio',
            'description': 'This is a test portfolio',
            'created_at': '2022-01-01 12:00:00',
            'updated_at': '2022-01-01 12:00:00'
        }
        portfolio_service.get_portfolio = Mock(return_value=portfolio_data)

        # Act
        result = portfolio_service.get_portfolio(portfolio_id)

        # Assert
        self.assertEqual(result, portfolio_data)
        portfolio_service.get_portfolio.assert_called_once_with(portfolio_id)

    def test_create_portfolio(self):
        # Arrange
        portfolio_data = {
            'name': 'Test Portfolio',
            'description': 'This is a test portfolio'
        }
        created_portfolio_data = {
            'id': 1,
            'name': 'Test Portfolio',
            'description': 'This is a test portfolio',
            'created_at': '2022-01-01 12:00:00',
            'updated_at': '2022-01-01 12:00:00'
        }
        portfolio_service.create_portfolio = Mock(return_value=created_portfolio_data)

        # Act
        result = portfolio_service.create_portfolio(portfolio_data)

        # Assert
        self.assertEqual(result, created_portfolio_data)
        portfolio_service.create_portfolio.assert_called_once_with(portfolio_data)

    def test_update_portfolio(self):
        # Arrange
        portfolio_id = 1
        updated_portfolio_data = {
            'name': 'Updated Test Portfolio',
            'description': 'This is an updated test portfolio'
        }
        updated_portfolio_response = {
            'id': portfolio_id,
            'name': 'Updated Test Portfolio',
            'description': 'This is an updated test portfolio',
            'created_at': '2022-01-01 12:00:00',
            'updated_at': '2022-01-01 12:00:00'
        }
        portfolio_service.update_portfolio = Mock(return_value=updated_portfolio_response)

        # Act
        result = portfolio_service.update_portfolio(portfolio_id, updated_portfolio_data)

        # Assert
        self.assertEqual(result, updated_portfolio_response)
        portfolio_service.update_portfolio.assert_called_once_with(portfolio_id, updated_portfolio_data)

    def test_delete_portfolio(self):
        # Arrange
        portfolio_id = 1
        portfolio_service.delete_portfolio = Mock(return_value=None)

        # Act
        result = portfolio_service.delete_portfolio(portfolio_id)

        # Assert
        self.assertIsNone(result)
        portfolio_service.delete_portfolio.assert_called_once_with(portfolio_id)

if __name__ == '__main__':
    unittest.main()