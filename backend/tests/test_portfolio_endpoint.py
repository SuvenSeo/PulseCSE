import json
import unittest
from unittest.mock import patch
from backend.app import create_app
from backend.models import db, Portfolio

class TestPortfolioEndpoint(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_portfolio(self):
        # Create a portfolio item
        portfolio = Portfolio(title='Test Portfolio', description='This is a test portfolio')
        db.session.add(portfolio)
        db.session.commit()

        # Make a GET request to the portfolio endpoint
        response = self.client.get('/api/portfolio')

        # Check if the response is successful
        self.assertEqual(response.status_code, 200)

        # Check if the response contains the portfolio item
        data = json.loads(response.data)
        self.assertEqual(data[0]['title'], 'Test Portfolio')
        self.assertEqual(data[0]['description'], 'This is a test portfolio')

    def test_get_portfolio_by_id(self):
        # Create a portfolio item
        portfolio = Portfolio(title='Test Portfolio', description='This is a test portfolio')
        db.session.add(portfolio)
        db.session.commit()

        # Make a GET request to the portfolio endpoint with the portfolio id
        response = self.client.get(f'/api/portfolio/{portfolio.id}')

        # Check if the response is successful
        self.assertEqual(response.status_code, 200)

        # Check if the response contains the portfolio item
        data = json.loads(response.data)
        self.assertEqual(data['title'], 'Test Portfolio')
        self.assertEqual(data['description'], 'This is a test portfolio')

    def test_create_portfolio(self):
        # Create a new portfolio item
        new_portfolio = {'title': 'New Test Portfolio', 'description': 'This is a new test portfolio'}

        # Make a POST request to the portfolio endpoint
        response = self.client.post('/api/portfolio', data=json.dumps(new_portfolio), content_type='application/json')

        # Check if the response is successful
        self.assertEqual(response.status_code, 201)

        # Check if the response contains the new portfolio item
        data = json.loads(response.data)
        self.assertEqual(data['title'], 'New Test Portfolio')
        self.assertEqual(data['description'], 'This is a new test portfolio')

    def test_update_portfolio(self):
        # Create a portfolio item
        portfolio = Portfolio(title='Test Portfolio', description='This is a test portfolio')
        db.session.add(portfolio)
        db.session.commit()

        # Update the portfolio item
        updated_portfolio = {'title': 'Updated Test Portfolio', 'description': 'This is an updated test portfolio'}

        # Make a PUT request to the portfolio endpoint with the portfolio id
        response = self.client.put(f'/api/portfolio/{portfolio.id}', data=json.dumps(updated_portfolio), content_type='application/json')

        # Check if the response is successful
        self.assertEqual(response.status_code, 200)

        # Check if the response contains the updated portfolio item
        data = json.loads(response.data)
        self.assertEqual(data['title'], 'Updated Test Portfolio')
        self.assertEqual(data['description'], 'This is an updated test portfolio')

    def test_delete_portfolio(self):
        # Create a portfolio item
        portfolio = Portfolio(title='Test Portfolio', description='This is a test portfolio')
        db.session.add(portfolio)
        db.session.commit()

        # Make a DELETE request to the portfolio endpoint with the portfolio id
        response = self.client.delete(f'/api/portfolio/{portfolio.id}')

        # Check if the response is successful
        self.assertEqual(response.status_code, 204)

        # Check if the portfolio item has been deleted
        self.assertIsNone(Portfolio.query.get(portfolio.id))

if __name__ == '__main__':
    unittest.main()