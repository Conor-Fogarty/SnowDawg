# tests/test_user_backend.py
import unittest
import sqlite3
import os
from app.user_Backend import user_bp, hash_password
from flask import Flask, json

class TestUserBackend(unittest.TestCase):
    def setUp(self):
        # Configure test environment
        self.test_db = "test_users.db"
        os.environ['TEST_DB'] = self.test_db
        
        # Create Flask test client
        self.app = Flask(__name__)
        self.app.register_blueprint(user_bp)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Initialize clean test database
        with sqlite3.connect(self.test_db) as conn:
            conn.execute('DROP TABLE IF EXISTS users')
            conn.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    email TEXT NOT NULL,
                    favorite_mountains TEXT,
                    location TEXT,
                    pass_type TEXT
                )
            ''')
            conn.commit()

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_password_hashing(self):
        """Test SHA-256 password hashing consistency"""
        password = "snowboard123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        self.assertEqual(len(hash1), 64)
        self.assertEqual(hash1, hash2)
        self.assertNotEqual(hash1, hash_password("differentpassword"))

    def test_user_lifecycle(self):
        """Full CRUD lifecycle test"""
        # Register
        reg_data = {
            "username": "powderhound",
            "password": "deepSnow123!",
            "email": "ph@example.com",
            "favorite_mountains": ["Stratton", "Killington"],
            "location": "Vermont",
            "pass_type": "Ikon"
        }
        response = self.client.post('/api/register', json=reg_data)
        self.assertEqual(response.status_code, 200)

        # Get user
        response = self.client.get('/api/user/powderhound')
        self.assertEqual(response.status_code, 200)
        user_data = json.loads(response.data)
        self.assertEqual(user_data["username"], "powderhound")
        self.assertEqual(user_data["favorite_mountains"], ["Stratton", "Killington"])

        # Update user
        update_data = {
            "email": "newph@example.com",
            "favorite_mountains": ["Stratton"],
            "pass_type": "Epic"
        }
        response = self.client.put('/api/user/powderhound', json=update_data)
        self.assertEqual(response.status_code, 200)

        # Verify update
        response = self.client.get('/api/user/powderhound')
        updated_data = json.loads(response.data)
        self.assertEqual(updated_data["email"], "newph@example.com")
        self.assertEqual(updated_data["pass_type"], "Epic")
        self.assertEqual(updated_data["favorite_mountains"], ["Stratton"])

        # Delete user
        response = self.client.delete('/api/user/powderhound')
        self.assertEqual(response.status_code, 200)

        # Verify deletion
        response = self.client.get('/api/user/powderhound')
        self.assertEqual(response.status_code, 404)

    def test_invalid_registration(self):
        """Test registration error cases"""
        # Missing required fields
        response = self.client.post('/api/register', json={
            "username": "missingfields"
        })
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()