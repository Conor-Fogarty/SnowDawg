import unittest
from unittest.mock import Mock, patch  # Explicit imports
from app.NOAA_API import app, RESORT_COORDINATES

class TestNOAAAPI(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    @patch('requests.get')
    def test_valid_resort_forecast(self, mock_get):
        # Create mock response objects
        mock_point = Mock()
        mock_point.status_code = 200
        mock_point.json.return_value = {
            "properties": {"forecast": "https://fake-forecast"}
        }

        mock_forecast = Mock()
        mock_forecast.status_code = 200
        mock_forecast.json.return_value = {
            "properties": {"periods": [{"temperature": 25}]}
        }

        # Configure mock sequence
        mock_get.side_effect = [mock_point, mock_forecast]

        response = self.client.get('/api/forecast/Stratton')
        self.assertEqual(response.status_code, 200)

    def test_invalid_resort(self):
        response = self.client.get('/api/forecast/Narnia')
        self.assertEqual(response.status_code, 404)