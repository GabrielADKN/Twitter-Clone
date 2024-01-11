"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_model.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        
        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)
        
        db.session.commit()
        
        self.testuser_id = self.testuser.id
        self.testuser2_id = self.testuser2.id
        
        self.testmessage = Message(text="test message", user_id=self.testuser_id)
        
        db.session.add(self.testmessage)
        db.session.commit()
        
        self.testmessage_id = self.testmessage.id
        
    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()
        
    def test_message_model(self):
        """Does basic model work?"""

        m = Message(
            text="test message",
            user_id=self.testuser_id
        )
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(m)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(m.user_id, self.testuser_id)

    def test_message_likes(self):
        """Does message like work?"""
        
        self.testuser2.likes.append(self.testmessage)
        db.session.commit()
        
        self.assertEqual(len(self.testuser2.likes), 1)
        self.assertEqual(self.testuser2.likes[0].id, self.testmessage_id)
    
    def test_message_delete(self):
        """Does message delete work?"""
        
        db.session.delete(self.testmessage)
        db.session.commit()
        
        self.assertEqual(len(self.testuser.messages), 0)
        
    def test_message_user(self):
        """Does message user work?"""
        
        self.assertEqual(self.testmessage.user.id, self.testuser_id)
        
    def test_message_repr(self):
        """Does message repr work?"""
        
        self.assertEqual(self.testmessage.__repr__(), f"<Message #{self.testmessage_id}: {self.testmessage.text}, {self.testmessage.user.id}>")
        
    def test_message_create(self):
        """Does message create work?"""
        
        m = Message(
            text="test message",
            user_id=self.testuser_id
        )
        
        db.session.add(m)
        db.session.commit()
        
        self.assertEqual(len(self.testuser.messages), 2)
        self.assertEqual(self.testuser.messages[1].id, m.id)
        
    