"""

Run 'python -m unittest Tests.test_events'
from root - Event_ticket_booking_management

"""

import unittest
import sys
import os

# Set the environment to testing
os.environ['FLASK_ENV'] = 'testing'

# Adjust the path to locate `app.py` and `ORM/DBClasses.py`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from ORM.DBClasses import (
    Role, User, Event, Booking, Seat, BookingSeat, TicketTier,
    EventTicketTier, Ticket, Notification, PaymentDetail, Payment
)
from werkzeug.security import generate_password_hash


class EventTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the app context and test client
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/test_event_bookings'
        app.config['TESTING'] = True
        cls.app_context = app.app_context()
        cls.app_context.push()
        cls.client = app.test_client()

        # Initialize the database with a role and user
        db.create_all()

        # Create a role
        role = Role(role_name="User")
        db.session.add(role)
        db.session.commit()

        # Create a user with a hashed password and assigned role
        cls.user = User(
            username="test_user",
            firstname="Test",
            secondname="User",
            email="testuser@example.com",
            password_hash=generate_password_hash("test123"),
            role_id=role.role_id
        )
        db.session.add(cls.user)
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        # Drop all tables after tests complete and remove the app context
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def login_test_user(self):
        """Helper method to log in the test user."""
        response = self.client.post('/login', data={
            'username': 'test_user',
            'password': 'test123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def setUp(self):
        # Log in the test user before each test
        self.login_test_user()

        # Set up a sample event for each test
        self.event = Event(
            title="Test Event",
            description="A test event",
            venue="Test Venue",
            start_date="2024-12-01",
            end_date="2024-12-02",
            total_tickets=100,
            available_tickets=100
        )
        db.session.add(self.event)
        db.session.commit()

    def tearDown(self):
        # Remove related seats first to handle foreign key constraint
        db.session.query(Seat).filter_by(event_id=self.event.event_id).delete()

        # Now delete the event
        db.session.query(Event).filter_by(event_id=self.event.event_id).delete()
        db.session.commit()

    def test_event_details_route(self):
        # Test a successful event details fetch
        response = self.client.get(f'/event/{self.event.event_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test Event", response.data)

    def test_event_details_not_found(self):
        # Test a non-existent event fetch, expecting a redirect
        response = self.client.get('/event/999', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        #self.assertIn(b"Event not found!", response.data)
        location = response.headers.get('Location')
        self.assertIsNotNone(location, "Expected 'Location' header missing")
        self.assertIn('/', location)


if __name__ == '__main__':
    unittest.main()
