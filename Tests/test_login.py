import os
import sys
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import session
from werkzeug.security import generate_password_hash
from app import app, db
from ORM.DBClasses import User, Role

class AuthTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/test_event_bookings'
        app.config['TESTING'] = True
        cls.app_context = app.app_context()
        cls.app_context.push()
        cls.client = app.test_client()

        db.create_all()
        role = Role(role_name="User")
        db.session.add(role)
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        self.test_user = User(
            username="testuser",
            firstname="Test",
            secondname="User",
            email="testuser@example.com",
            password_hash=generate_password_hash("password123"),
            role_id=1
        )
        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        db.session.query(User).delete()
        db.session.commit()

    def test_register_successful(self):
        response = self.client.post('/register', data={
            'firstname': 'New',
            'lastname': 'User',
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Registration successful!", response.data)

    def test_register_username_exists(self):
        response = self.client.post('/register', data={
            'firstname': 'Test',
            'lastname': 'User',
            'username': 'testuser',
            'email': 'uniqueemail@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Username already exists!", response.data)

    def test_register_email_exists(self):
        response = self.client.post('/register', data={
            'firstname': 'Test',
            'lastname': 'User',
            'username': 'uniqueuser',
            'email': 'testuser@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Email already registered!", response.data)

    def test_register_password_mismatch(self):
        response = self.client.post('/register', data={
            'firstname': 'Test',
            'lastname': 'User',
            'username': 'uniqueuser',
            'email': 'uniqueuser@example.com',
            'password': 'password123',
            'confirm_password': 'password456'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Passwords do not match!", response.data)

    def test_login_successful(self):
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertIn('user_id', sess)
            self.assertEqual(sess['username'], 'testuser')

    def test_login_invalid_credentials(self):
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid username or password!", response.data)

    def test_logout(self):
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)

        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"You have been logged out.", response.data)
        with self.client.session_transaction() as sess:
            self.assertNotIn('user_id', sess)
            self.assertNotIn('username', sess)

if __name__ == '__main__':
    unittest.main()
