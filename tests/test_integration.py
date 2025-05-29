import unittest
from app.NOAA_API import app as weather_app
from app.user_Backend import user_bp
from flask import Flask

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(user_bp)
        self.app.testing = True
        self.client = self.app.test_client()

        # Register a test user
        self.client.post('/api/register', json={
            "username": "integration_test",
            "password": "test123",
            "email": "integration@test.com",
            "favorite_mountains": ["Stratton", "Killington"],
            "location": "VT",
            "pass_type": "Ikon"
        })

    def test_user_with_weather(self):
        # Get user data
        user_response = self.client.get('/api/user/integration_test')
        self.assertEqual(user_response.status_code, 200)
        user_data = user_response.get_json()

        # Verify favorite mountains match resorts we support
        for resort in user_data['favorite_mountains']:
            weather_response = weather_app.test_client().get(f'/api/forecast/{resort}')
            self.assertEqual(weather_response.status_code, 200)
            weather_data = weather_response.get_json()
            self.assertIn('forecast', weather_data)

if __name__ == '__main__':
    unittest.main()